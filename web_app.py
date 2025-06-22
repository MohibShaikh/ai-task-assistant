#!/usr/bin/env python3
"""
Web Interface for AI Task Assistant
A beautiful, modern web application for task management.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from task_assistant import TaskAssistant
from user_manager import UserManager
from flask import session
from datetime import datetime, timedelta
import json
import os
from functools import wraps
from dotenv import load_dotenv
from flask_cors import CORS
from sentence_transformers import SentenceTransformer

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Pre-load the model globally to avoid multiple loading
print("🚀 Pre-loading sentence transformer model...")
try:
    GLOBAL_MODEL = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    print("✅ Sentence transformer model loaded successfully!")
except Exception as e:
    print(f"⚠️ Failed to load global model: {e}")
    GLOBAL_MODEL = None

# Global components
user_manager = None
task_assistant = None  # Will be user-specific

def initialize_components():
    """Initialize all components with proper error handling."""
    global user_manager, task_assistant
    
    try:
        print("🔧 Initializing user manager...")
        user_manager = UserManager()
        
        print("🔧 Initializing task assistant...")
        task_assistant = TaskAssistant()  # Will be user-specific
        
        print("✅ All components initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        return False

# Initialize components
if not initialize_components():
    print("❌ Failed to initialize components. Exiting.")
    exit(1)

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('session_id') or request.headers.get('Authorization')
        
        # Handle Bearer token format
        if session_id and session_id.startswith('Bearer '):
            session_id = session_id[7:]  # Remove 'Bearer ' prefix
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user = user_manager.get_user_from_session(session_id)
        if not user:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        # Add user to request context
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for cloud platforms."""
    try:
        # Basic health check
        return jsonify({
            'status': 'healthy',
            'service': 'AI Task Assistant',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'Username, email, and password are required'
            }), 400
        
        result = user_manager.register_user(username, email, password)
        
        if result['success']:
            # Automatically log the user in after successful registration
            login_result = user_manager.login_user(username, password)
            
            if login_result['success']:
                response = jsonify({
                    'success': True,
                    'user': login_result['user'],
                    'session_id': login_result['session_id'],
                    'message': 'User registered and logged in successfully'
                })
                # Set session cookie (allow JavaScript to read it)
                response.set_cookie('session_id', login_result['session_id'], max_age=30*24*60*60, httponly=False)
                return response
            else:
                return jsonify({
                    'success': True,
                    'message': 'User registered successfully. Please log in.'
                })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        result = user_manager.login_user(username, password)
        
        if result['success']:
            response = jsonify({
                'success': True,
                'user': result['user'],
                'session_id': result['session_id'],
                'message': 'Login successful'
            })
            # Set session cookie (allow JavaScript to read it)
            response.set_cookie('session_id', result['session_id'], max_age=30*24*60*60, httponly=False)
            return response
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout a user."""
    try:
        session_id = request.cookies.get('session_id') or request.headers.get('Authorization')
        
        # Handle Bearer token format
        if session_id and session_id.startswith('Bearer '):
            session_id = session_id[7:]  # Remove 'Bearer ' prefix
        
        user_manager.logout_user(session_id)
        
        response = jsonify({
            'success': True,
            'message': 'Logout successful'
        })
        response.delete_cookie('session_id')
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/me')
@require_auth
def get_current_user():
    """Get current user information."""
    return jsonify({
        'success': True,
        'user': request.user
    })

@app.route('/api/auth/validate', methods=['POST'])
def validate_session():
    """Validate the current session and return user info."""
    try:
        session_id = request.cookies.get('session_id') or request.headers.get('Authorization')
        
        # Handle Bearer token format
        if session_id and session_id.startswith('Bearer '):
            session_id = session_id[7:]  # Remove 'Bearer ' prefix
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session found'
            }), 401
        
        user = user_manager.get_user_from_session(session_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 401
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/delete-account', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete the current user's account and all associated data."""
    try:
        user_id = request.user['user_id']
        session_id = request.cookies.get('session_id') or request.headers.get('Authorization')
        
        # Delete user and all their data
        success = user_manager.delete_user(user_id)
        
        if success:
            # Logout the user
            user_manager.logout_user(session_id)
            
            response = jsonify({
                'success': True,
                'message': 'Account deleted successfully'
            })
            response.delete_cookie('session_id')
            return response
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete account'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks')
@require_auth
def get_tasks():
    """Get all tasks for the authenticated user."""
    try:
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Only use in-memory cache; do not refresh from Pinecone
        tasks = user_assistant.memory.get_all_tasks()
        
        # Process tasks for frontend
        processed_tasks = []
        for task in tasks:
            processed_task = {
                'id': task.get('id'),
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'priority': task.get('priority', 'medium'),
                'tags': task.get('tags', []),
                'due_date': task.get('due_date'),
                'completed': task.get('completed', False),
                'created_at': task.get('created_at'),
                'updated_at': task.get('updated_at'),
                'status': 'completed' if task.get('completed', False) else 'pending'
            }
            
            # Calculate due date status
            if processed_task['due_date']:
                try:
                    due_date = datetime.strptime(processed_task['due_date'], '%Y-%m-%d')
                    today = datetime.now().date()
                    due_date_obj = due_date.date()
                    
                    if processed_task['completed']:
                        processed_task['due_status'] = 'completed'
                    elif due_date_obj < today:
                        processed_task['due_status'] = 'overdue'
                    elif due_date_obj == today:
                        processed_task['due_status'] = 'today'
                    elif (due_date_obj - today).days <= 3:
                        processed_task['due_status'] = 'soon'
                    else:
                        processed_task['due_status'] = 'upcoming'
                except ValueError:
                    processed_task['due_status'] = 'invalid'
            else:
                processed_task['due_status'] = 'no_due_date'
            
            processed_tasks.append(processed_task)
        
        return jsonify({
            'success': True,
            'tasks': processed_tasks,
            'total': len(processed_tasks)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks', methods=['POST'])
@require_auth
def add_task():
    """Add a new task for the authenticated user."""
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'medium')
        tags = data.get('tags', [])
        due_date = data.get('due_date')
        
        if not title:
            return jsonify({
                'success': False,
                'error': 'Task title is required'
            }), 400
        
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Add task using the assistant
        task_id = user_assistant.memory.add_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date
        )
        
        if task_id:
            # Get the created task to return it
            created_task = user_assistant.memory.get_task_by_id(task_id)
            if created_task:
                return jsonify(created_task), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Task created but could not retrieve details'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add task'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
@require_auth
def update_task(task_id):
    """Update a task for the authenticated user."""
    try:
        data = request.get_json()
        
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Use the memory's update_task method
        success = user_assistant.memory.update_task(task_id, **data)
        
        if success:
            # Get the updated task to return it
            updated_task = user_assistant.memory.get_task_by_id(task_id)
            if updated_task:
                return jsonify(updated_task), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Task updated but could not retrieve details'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found or failed to update'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    """Delete a task for the authenticated user."""
    try:
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Use the memory's delete_task method
        success = user_assistant.memory.delete_task(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found or failed to delete'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
@require_auth
def complete_task(task_id):
    """Complete a task for the authenticated user."""
    try:
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        success = user_assistant.memory.complete_task(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found or already completed'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
@require_auth
def search_tasks():
    """Search tasks for the authenticated user."""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Search tasks
        results = user_assistant.memory.search_tasks(query, k=10)
        
        # Process results for frontend
        processed_results = []
        for task in results:
            processed_task = {
                'id': task.get('id'),
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'priority': task.get('priority', 'medium'),
                'tags': task.get('tags', []),
                'due_date': task.get('due_date'),
                'completed': task.get('completed', False),
                'similarity_score': task.get('similarity_score', 0)
            }
            processed_results.append(processed_task)
        
        return jsonify({
            'success': True,
            'results': processed_results,
            'query': query,
            'total': len(processed_results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
@require_auth
def get_stats():
    """Get statistics for the authenticated user."""
    try:
        # Create user-specific task assistant
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        
        # Get basic task statistics
        task_stats = user_assistant.memory.get_task_statistics()
        
        return jsonify({
            'success': True,
            'stats': task_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suggestions')
@require_auth
def get_suggestions():
    """Get smart task suggestions for the authenticated user."""
    try:
        user_assistant = TaskAssistant(user_id=str(request.user['user_id']))
        suggestions = user_assistant.suggestions.get_smart_suggestions(limit=5)
        suggestions_json = [
            {
                'title': s.title,
                'description': s.description,
                'priority': s.priority,
                'tags': s.tags,
                'reasoning': s.reasoning,
                'suggestion_type': s.suggestion_type
            }
            for s in suggestions
        ]
        return jsonify({'success': True, 'suggestions': suggestions_json})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 8080))
    
    print("🌐 Starting AI Task Assistant Web Interface...")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("🚀 Press Ctrl+C to stop the server")
    
    # Use production settings for cloud deployment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)


