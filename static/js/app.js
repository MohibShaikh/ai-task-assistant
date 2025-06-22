// Global variables
let tasks = [];
let filteredTasks = [];
let currentView = 'list';
let currentEditingTask = null;
let sessionId = null;

// Performance optimizations
let searchDebounceTimer = null;
let statsCache = null;
let suggestionsCache = null;
let lastStatsUpdate = 0;
let lastSuggestionsUpdate = 0;
const CACHE_DURATION = 30000; // 30 seconds

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Check for OAuth callback first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('login') || urlParams.has('session_id')) {
        handleOAuthCallback();
        return;
    }
    
    checkAuth();
});

// Check authentication status and show appropriate page
function checkAuth() {
    sessionId = getCookie('session_id');
    if (sessionId) {
        validateSession();
    } else {
        showLandingPage();
    }
}

// Show landing page
function showLandingPage() {
    document.getElementById('landing-page').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
    setupLandingPageEventListeners();
}

// Show dashboard
function showDashboard() {
    document.getElementById('landing-page').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    setupEventListeners();
    initApp();
}

// Setup landing page event listeners
function setupLandingPageEventListeners() {
    console.log('Setting up landing page event listeners...');
    
    // Login buttons
    const loginButtons = document.querySelectorAll('#landing-login-btn');
    console.log('Found login buttons:', loginButtons.length);
    loginButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            console.log('Login button clicked');
            e.preventDefault();
            showAuthModal('login');
        });
    });
    
    // Register buttons
    const registerButtons = document.querySelectorAll('#landing-register-btn, #hero-register-btn, #cta-register-btn');
    console.log('Found register buttons:', registerButtons.length);
    registerButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            console.log('Register button clicked');
            e.preventDefault();
            showAuthModal('register');
        });
    });
    
    // Learn more button
    const learnMoreBtn = document.getElementById('learn-more-btn');
    console.log('Found learn more button:', !!learnMoreBtn);
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', (e) => {
            console.log('Learn more button clicked');
            e.preventDefault();
            scrollToFeatures();
        });
    }
}

// Show auth modal with specified tab
function showAuthModal(tab) {
    console.log('showAuthModal called with tab:', tab);
    
    const overlay = document.getElementById('auth-overlay');
    console.log('Found auth overlay:', !!overlay);
    
    if (!overlay) {
        console.error('Auth overlay not found!');
        return;
    }
    
    overlay.style.display = 'flex';
    console.log('Auth overlay display set to flex');
    
    if (tab === 'login') {
        showLoginForm();
    } else {
        showRegisterForm();
    }
    
    // Setup auth form listeners
    setupAuthEventListeners();
}

// Scroll to features section
function scrollToFeatures() {
    const featuresSection = document.getElementById('features-section');
    if (featuresSection) {
        featuresSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Add task form
    document.getElementById('add-task-form').addEventListener('submit', handleAddTask);
    
    // Edit task form
    document.getElementById('edit-task-form').addEventListener('submit', handleEditTask);
    
    // Search input with debouncing
    document.getElementById('search-input').addEventListener('input', function() {
        // Clear previous timer
        if (searchDebounceTimer) {
            clearTimeout(searchDebounceTimer);
        }
        
        // Set new timer for debounced search
        searchDebounceTimer = setTimeout(() => {
            filterTasks();
        }, 300); // 300ms delay
    });
    
    // Modal backdrop clicks
    document.getElementById('add-task-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeAddTaskModal();
        }
    });
    
    document.getElementById('edit-task-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeEditTaskModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'n':
                    e.preventDefault();
                    openAddTaskModal();
                    break;
                case 'f':
                    e.preventDefault();
                    document.getElementById('search-input').focus();
                    break;
            }
        }
        
        if (e.key === 'Escape') {
            closeAddTaskModal();
            closeEditTaskModal();
        }
    });
    
    // Google Sign-In buttons
    const googleLoginBtn = document.getElementById('google-login-btn');
    const googleRegisterBtn = document.getElementById('google-register-btn');
    
    if (googleLoginBtn) {
        googleLoginBtn.removeEventListener('click', handleGoogleSignIn);
        googleLoginBtn.addEventListener('click', () => handleGoogleSignIn('login'));
    }
    
    if (googleRegisterBtn) {
        googleRegisterBtn.removeEventListener('click', handleGoogleSignIn);
        googleRegisterBtn.addEventListener('click', () => handleGoogleSignIn('register'));
    }
}

// Setup auth event listeners
function setupAuthEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.removeEventListener('submit', handleLogin);
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.removeEventListener('submit', handleRegister);
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Close modal on backdrop click
    const authOverlay = document.getElementById('auth-overlay');
    authOverlay.addEventListener('click', function(e) {
        if (e.target === this) {
            hideAuthOverlay();
        }
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideAuthOverlay();
        }
    });
}

// Load tasks from API with caching
async function loadTasks() {
    try {
        showLoading(true);
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        if (data.success) {
            tasks = data.tasks;
            filteredTasks = [...tasks];
            renderTasks();
            updateStats();
        } else {
            showToast('Error loading tasks: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Failed to load tasks: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Load statistics with caching
async function loadStats() {
    // Calculate stats from current tasks data instead of calling backend
    // This ensures stats are always up-to-date and works with the original backend format
    updateStatsDisplay();
}

// Load smart suggestions with caching
async function loadSuggestions() {
    const now = Date.now();
    
    // Use cached suggestions if available and fresh
    if (suggestionsCache && (now - lastSuggestionsUpdate) < CACHE_DURATION) {
        renderSuggestionList(suggestionsCache);
        return;
    }
    
    const section = document.getElementById('suggestions-section');
    const list = document.getElementById('suggestions-list');
    list.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading suggestions...</div>';
    
    try {
        const response = await fetch('/api/suggestions');
        const data = await response.json();
        if (data.success && data.suggestions.length > 0) {
            suggestionsCache = data.suggestions;
            lastSuggestionsUpdate = now;
            renderSuggestionList(data.suggestions);
        } else {
            list.innerHTML = '<div class="no-suggestions">No smart suggestions available. Add more tasks to get recommendations.</div>';
        }
    } catch (error) {
        list.innerHTML = `<div class="no-suggestions">Failed to load suggestions: ${error.message}</div>`;
    }
}

// Render the suggestions list
function renderSuggestionList(suggestions) {
    const list = document.getElementById('suggestions-list');
    list.innerHTML = suggestions.map(s => `
        <div class="suggestion-card">
            <div class="suggestion-title"><i class="fas fa-lightbulb"></i> ${escapeHtml(s.title)}</div>
            <div class="suggestion-description">${escapeHtml(s.description)}</div>
            <div class="suggestion-meta">
                <span class="suggestion-priority ${s.priority}">${s.priority}</span>
                <span class="suggestion-tags">${s.tags.map(tag => `<span class="suggestion-tag">${escapeHtml(tag)}</span>`).join('')}</span>
            </div>
            <div class="suggestion-reasoning">${escapeHtml(s.reasoning)}</div>
        </div>
    `).join('');
}

// Render tasks
function renderTasks() {
    const container = document.getElementById('tasks-container');
    const noTasks = document.getElementById('no-tasks');
    
    if (filteredTasks.length === 0) {
        container.innerHTML = '';
        noTasks.style.display = 'block';
        return;
    }
    
    noTasks.style.display = 'none';
    
    if (currentView === 'list') {
        renderListView(container);
    } else {
        renderGridView(container);
    }
}

// Render list view
function renderListView(container) {
    container.className = 'tasks-container list-view';
    container.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');
}

// Render grid view
function renderGridView(container) {
    container.className = 'tasks-container grid-view';
    container.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');
}

// Create task card HTML
function createTaskCard(task) {
    const dueDateDisplay = getDueDateDisplay(task);
    const priorityClass = task.priority || 'medium';
    const statusClass = task.completed ? 'completed' : '';
    
    // Handle tags - could be string or array from backend
    let tags = [];
    if (task.tags) {
        if (Array.isArray(task.tags)) {
            tags = task.tags;
        } else if (typeof task.tags === 'string') {
            tags = task.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
        }
    }
    
    return `
        <div class="task-card ${statusClass}" data-task-id="${task.id}">
            <div class="task-header">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-actions">
                    <button class="task-action-btn" onclick="editTask('${task.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="task-action-btn" onclick="deleteTask('${task.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="task-action-btn" onclick="toggleTaskComplete('${task.id}')" title="${task.completed ? 'Mark as pending' : 'Mark as completed'}">
                        <i class="fas fa-${task.completed ? 'undo' : 'check'}"></i>
                    </button>
                </div>
            </div>
            ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
            <div class="task-meta">
                <span class="task-priority ${priorityClass}">${priorityClass}</span>
                ${tags.length > 0 ? `<div class="task-tags">${tags.map(tag => `<span class="task-tag">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
                ${dueDateDisplay ? `<div class="task-due-date ${dueDateDisplay.class}"><i class="fas fa-calendar"></i> ${dueDateDisplay.text}</div>` : ''}
            </div>
        </div>
    `;
}

// Get due date display information
function getDueDateDisplay(task) {
    if (!task.due_date) return null;
    
    const dueDate = new Date(task.due_date);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Reset time for comparison
    today.setHours(0, 0, 0, 0);
    tomorrow.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);
    
    if (task.completed) {
        return {
            text: `Completed on ${dueDate.toLocaleDateString()}`,
            class: 'completed'
        };
    }
    
    if (dueDate < today) {
        return {
            text: `Overdue (${dueDate.toLocaleDateString()})`,
            class: 'overdue'
        };
    }
    
    if (dueDate.getTime() === today.getTime()) {
        return {
            text: 'Due today',
            class: 'today'
        };
    }
    
    if (dueDate.getTime() === tomorrow.getTime()) {
        return {
            text: 'Due tomorrow',
            class: 'soon'
        };
    }
    
    const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
    if (diffDays <= 7) {
        return {
            text: `Due in ${diffDays} days`,
            class: 'soon'
        };
    }
    
    return {
        text: `Due ${dueDate.toLocaleDateString()}`,
        class: 'upcoming'
    };
}

// Filter tasks based on search and filters
function filterTasks() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const priorityFilter = document.getElementById('priority-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    const dueFilter = document.getElementById('due-filter').value;
    
    filteredTasks = tasks.filter(task => {
        // Search filter
        const matchesSearch = !searchTerm || 
            task.title.toLowerCase().includes(searchTerm) ||
            (task.description && task.description.toLowerCase().includes(searchTerm)) ||
            (task.tags && (
                Array.isArray(task.tags) ? 
                    task.tags.some(tag => tag.toLowerCase().includes(searchTerm)) :
                    task.tags.toLowerCase().includes(searchTerm)
            ));
        
        // Priority filter
        const matchesPriority = !priorityFilter || task.priority === priorityFilter;
        
        // Status filter
        const matchesStatus = !statusFilter || 
            (statusFilter === 'completed' && task.completed) ||
            (statusFilter === 'pending' && !task.completed);
        
        // Due date filter
        const matchesDue = !dueFilter || matchesDueFilter(task, dueFilter);
        
        return matchesSearch && matchesPriority && matchesStatus && matchesDue;
    });
    
    renderTasks();
    updateFilterCount();
}

// Check if task matches due date filter
function matchesDueFilter(task, filter) {
    if (!task.due_date) return filter === 'no_due_date';
    
    const dueDate = new Date(task.due_date);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Reset time for comparison
    today.setHours(0, 0, 0, 0);
    tomorrow.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);
    
    switch (filter) {
        case 'overdue':
            return dueDate < today && !task.completed;
        case 'today':
            return dueDate.getTime() === today.getTime();
        case 'soon':
            const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
            return diffDays > 0 && diffDays <= 7;
        case 'upcoming':
            const diffDaysUpcoming = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
            return diffDaysUpcoming > 7;
        default:
            return true;
    }
}

// Update filter count display
function updateFilterCount() {
    const count = filteredTasks.length;
    const total = tasks.length;
    // You can add a filter count display here if needed
}

// Search tasks (legacy function for backward compatibility)
function searchTasks() {
    filterTasks();
}

// Handle add task form submission
async function handleAddTask(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title') || document.getElementById('task-title').value,
        description: formData.get('description') || document.getElementById('task-description').value,
        priority: formData.get('priority') || document.getElementById('task-priority').value,
        due_date: formData.get('due_date') || document.getElementById('task-due-date').value,
        tags: formData.get('tags') || document.getElementById('task-tags').value
    };
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        const data = await response.json();
        
        // Backend returns the created task object directly on success (201 status)
        if (response.ok && data.id) {
            showToast('Task added successfully!', 'success');
            closeAddTaskModal();
            e.target.reset();
            loadTasks();
            clearCaches();
        } else {
            // Handle error response
            const errorMessage = data.error || 'Failed to add task';
            showToast('Error adding task: ' + errorMessage, 'error');
        }
    } catch (error) {
        showToast('Failed to add task: ' + error.message, 'error');
    }
}

// Handle edit task form submission
async function handleEditTask(e) {
    e.preventDefault();
    
    if (!currentEditingTask) return;
    
    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title') || document.getElementById('edit-task-title').value,
        description: formData.get('description') || document.getElementById('edit-task-description').value,
        priority: formData.get('priority') || document.getElementById('edit-task-priority').value,
        due_date: formData.get('due_date') || document.getElementById('edit-task-due-date').value,
        tags: formData.get('tags') || document.getElementById('edit-task-tags').value,
        completed: document.getElementById('edit-task-completed').checked
    };
    
    try {
        const response = await fetch(`/api/tasks/${currentEditingTask}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        const data = await response.json();
        
        // Backend returns the updated task object directly on success
        if (response.ok && data.id) {
            showToast('Task updated successfully!', 'success');
            closeEditTaskModal();
            loadTasks();
            clearCaches();
        } else {
            // Handle error response
            const errorMessage = data.error || 'Failed to update task';
            showToast('Error updating task: ' + errorMessage, 'error');
        }
    } catch (error) {
        showToast('Failed to update task: ' + error.message, 'error');
    }
}

// Toggle task completion status
async function toggleTaskComplete(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...task,
                completed: !task.completed
            })
        });
        
        const data = await response.json();
        
        // Backend returns the updated task object directly on success
        if (response.ok && data.id) {
            showToast(task.completed ? 'Task marked as pending!' : 'Task completed!', 'success');
            loadTasks();
            clearCaches();
        } else {
            // Handle error response
            const errorMessage = data.error || 'Failed to update task';
            showToast('Error updating task: ' + errorMessage, 'error');
        }
    } catch (error) {
        showToast('Failed to update task: ' + error.message, 'error');
    }
}

// Delete task
async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Task deleted successfully!', 'success');
            loadTasks();
            clearCaches();
        } else {
            showToast('Error deleting task: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Failed to delete task: ' + error.message, 'error');
    }
}

// Delete current editing task
function deleteCurrentTask() {
    if (currentEditingTask) {
        deleteTask(currentEditingTask);
        closeEditTaskModal();
    }
}

// Edit task
function editTask(taskId) {
    console.log('editTask called with taskId:', taskId);
    const task = tasks.find(t => t.id === taskId);
    console.log('Found task:', task);
    if (!task) return;
    
    currentEditingTask = taskId;
    
    document.getElementById('edit-task-id').value = task.id;
    document.getElementById('edit-task-title').value = task.title;
    document.getElementById('edit-task-description').value = task.description || '';
    document.getElementById('edit-task-priority').value = task.priority || 'medium';
    document.getElementById('edit-task-due-date').value = task.due_date || '';
    
    // Handle tags - convert array to string for input field
    let tagsString = '';
    if (task.tags) {
        if (Array.isArray(task.tags)) {
            tagsString = task.tags.join(', ');
        } else if (typeof task.tags === 'string') {
            tagsString = task.tags;
        }
    }
    document.getElementById('edit-task-tags').value = tagsString;
    
    document.getElementById('edit-task-completed').checked = task.completed || false;
    
    console.log('Opening edit modal...');
    openEditTaskModal();
}

// Modal functions
function openAddTaskModal() {
    document.getElementById('add-task-modal').classList.add('show');
}

function closeAddTaskModal() {
    document.getElementById('add-task-modal').classList.remove('show');
}

function openEditTaskModal() {
    document.getElementById('edit-task-modal').classList.add('show');
}

function closeEditTaskModal() {
    document.getElementById('edit-task-modal').classList.remove('show');
    currentEditingTask = null;
}

// View functions
function setView(view) {
    currentView = view;
    
    // Update active button
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    renderTasks();
}

// Theme functions
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Stats functions
function updateStatsDisplay(stats) {
    // Calculate stats from the current tasks data instead of relying on backend
    const total = tasks.length;
    let completed = 0;
    let pending = 0;
    let overdue = 0;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    tasks.forEach(task => {
        if (task.completed) {
            completed++;
        } else {
            pending++;
            
            // Check if overdue
            if (task.due_date) {
                try {
                    const dueDate = new Date(task.due_date);
                    dueDate.setHours(0, 0, 0, 0);
                    if (dueDate < today) {
                        overdue++;
                    }
                } catch (e) {
                    // Skip invalid dates
                }
            }
        }
    });
    
    document.getElementById('total-tasks').textContent = total;
    document.getElementById('completed-tasks').textContent = completed;
    document.getElementById('pending-tasks').textContent = pending;
    document.getElementById('overdue-tasks').textContent = overdue;
}

function updateStats() {
    loadStats();
}

// Utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="${getToastIcon(type)}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Authentication functions
async function validateSession() {
    try {
        const response = await fetch('/api/auth/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showDashboard();
        } else {
            setCookie('session_id', '', -1);
            showLandingPage();
        }
    } catch (error) {
        console.error('Session validation failed:', error);
        setCookie('session_id', '', -1);
        showLandingPage();
    }
}

function initApp() {
    loadTasks();
    loadSuggestions();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
}

function showAuthOverlay() {
    document.getElementById('auth-overlay').style.display = 'flex';
}

function hideAuthOverlay() {
    document.getElementById('auth-overlay').style.display = 'none';
}

function showLoginForm() {
    console.log('showLoginForm called');
    document.getElementById('login-tab').classList.add('active');
    document.getElementById('register-tab').classList.remove('active');
    document.getElementById('login-form-section').style.display = 'block';
    document.getElementById('register-form-section').style.display = 'none';
    clearAuthError();
}

function showRegisterForm() {
    console.log('showRegisterForm called');
    document.getElementById('register-tab').classList.add('active');
    document.getElementById('login-tab').classList.remove('active');
    document.getElementById('register-form-section').style.display = 'block';
    document.getElementById('login-form-section').style.display = 'none';
    clearAuthError();
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionId = getSessionIdFromResponse(response, data);
            setCookie('session_id', sessionId, 7);
            hideAuthOverlay();
            showDashboard();
            showToast('Login successful!', 'success');
        } else {
            showAuthError(data.error || 'Login failed');
        }
    } catch (error) {
        showAuthError('Network error. Please try again.');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionId = getSessionIdFromResponse(response, data);
            setCookie('session_id', sessionId, 7);
            hideAuthOverlay();
            showDashboard();
            showToast('Registration successful!', 'success');
        } else {
            showAuthError(data.error || 'Registration failed');
        }
    } catch (error) {
        showAuthError('Network error. Please try again.');
    }
}

function showAuthError(msg) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'auth-error';
    errorDiv.textContent = msg;
    
    const activeForm = document.querySelector('#login-form-section[style*="block"]') || 
                      document.querySelector('#register-form-section[style*="block"]');
    
    if (activeForm) {
        const existingError = activeForm.querySelector('.auth-error');
        if (existingError) {
            existingError.remove();
        }
        activeForm.appendChild(errorDiv);
    }
}

function clearAuthError() {
    const errors = document.querySelectorAll('.auth-error');
    errors.forEach(error => error.remove());
}

// Cookie functions
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

function getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function getSessionIdFromResponse(res, data) {
    // Try to get session_id from response headers first
    const sessionId = res.headers.get('Set-Cookie')?.match(/session_id=([^;]+)/)?.[1];
    if (sessionId) return sessionId;
    
    // Fallback to data object
    return data.session_id || data.user?.session_id;
}

function clearCaches() {
    // Clear all caches to force fresh data
    statsCache = null;
    suggestionsCache = null;
    lastStatsUpdate = 0;
    lastSuggestionsUpdate = 0;
    
    // Reload stats immediately
    loadStats();
}

// Logout function
function logoutUser() {
    if (confirm('Are you sure you want to logout?')) {
        setCookie('session_id', '', -1);
        sessionId = null;
        clearCaches();
        showLandingPage();
        showToast('Logged out successfully', 'info');
    }
}

// Handle Google Sign-In
async function handleGoogleSignIn(action) {
    try {
        showLoading(true);
        
        // Get the current page URL to redirect back after OAuth
        const currentUrl = window.location.href;
        
        // Call backend to get Google OAuth URL
        const response = await fetch('/api/auth/google/login', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to Google OAuth with state parameter for redirect back
            const authUrl = new URL(data.auth_url);
            authUrl.searchParams.set('state', currentUrl);
            window.location.href = authUrl.toString();
        } else {
            showToast(data.error || 'Failed to initiate Google Sign-In', 'error');
        }
    } catch (error) {
        console.error('Google Sign-In error:', error);
        showToast('Failed to connect to Google Sign-In', 'error');
    } finally {
        showLoading(false);
    }
}

// Handle OAuth callback (called when user returns from Google)
function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const loginStatus = urlParams.get('login');
    const sessionId = urlParams.get('session_id');
    
    if (loginStatus === 'success' && sessionId) {
        // Set the session cookie
        setCookie('session_id', sessionId, 30);
        
        // Clear URL parameters
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        
        // Show success message and redirect to dashboard
        showToast('Successfully signed in with Google!', 'success');
        setTimeout(() => {
            showDashboard();
        }, 1000);
    } else if (loginStatus === 'error') {
        const error = urlParams.get('error') || 'Authentication failed';
        showToast(error, 'error');
    }
} 