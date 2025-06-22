import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import yaml
from datetime import datetime
import uuid
import threading
import time
from collections import defaultdict

# Global model cache to avoid reloading
_MODEL_CACHE = {}
_MODEL_LOCK = threading.Lock()

class VectorMemory:
    def __init__(self, user_id: str = "default", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector memory system for task storage and retrieval.
        
        Args:
            user_id: Unique identifier for the user (creates separate databases)
            model_name: Name of the sentence transformer model to use
        """
        self.user_id = user_id
        self.model_name = model_name
        
        # Create user-specific file names
        self.index_file = f"task_index_{user_id}.faiss"
        self.metadata_file = f"task_metadata_{user_id}.pkl"
        
        # Get or create cached model
        self.model = self._get_cached_model(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Task metadata storage with O(1) lookup
        self.tasks = []
        self.tasks_by_id = {}  # O(1) lookup dictionary
        self.task_id_counter = 0
        
        # Performance optimizations
        self._dirty = False  # Track if data needs saving
        self._save_timer = None
        self._save_delay = 2.0  # Save after 2 seconds of inactivity
        self._lock = threading.RLock()  # Thread-safe operations
        
        # Load existing data if available
        self._load_existing_data()
    
    def _get_cached_model(self, model_name: str) -> SentenceTransformer:
        """Get or create a cached model instance."""
        with _MODEL_LOCK:
            if model_name not in _MODEL_CACHE:
                print(f"Loading model {model_name}...")
                _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
                print(f"Model {model_name} loaded and cached.")
            return _MODEL_CACHE[model_name]
    
    def _load_existing_data(self):
        """Load existing index and metadata if files exist."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.tasks = data.get('tasks', [])
                    self.task_id_counter = data.get('task_id_counter', 0)
                
                # Build lookup dictionary
                self.tasks_by_id = {task['id']: task for task in self.tasks}
                
                print(f"Loaded {len(self.tasks)} existing tasks for user {self.user_id}.")
            except Exception as e:
                print(f"Error loading existing data for user {self.user_id}: {e}")
                print("Starting with fresh memory.")
    
    def _schedule_save(self):
        """Schedule a delayed save operation."""
        if self._save_timer:
            self._save_timer.cancel()
        
        def delayed_save():
            with self._lock:
                if self._dirty:
                    self._save_data()
                    self._dirty = False
        
        self._save_timer = threading.Timer(self._save_delay, delayed_save)
        self._save_timer.start()
    
    def _save_data(self):
        """Save index and metadata to files."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save metadata
            data = {
                'tasks': self.tasks,
                'task_id_counter': self.task_id_counter,
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving data for user {self.user_id}: {e}")
    
    def add_task(self, title: str, description: str = "", priority: str = "medium", 
                 status: str = "pending", tags: List[str] = None, due_date: str = None) -> str:
        """Add a new task to the system."""
        with self._lock:
            try:
                task_id = str(uuid.uuid4())
                task = {
                    'id': task_id,
                    'user_id': self.user_id,
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'tags': tags or [],
                    'due_date': due_date,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'completed': False
                }
                
                # Generate embedding for the task
                task_text = f"{title} {description} {' '.join(tags or [])}"
                embedding = self.model.encode([task_text])[0]
                
                # Add to FAISS index
                self.index.add(np.array([embedding], dtype=np.float32))
                
                # Store task metadata
                self.tasks.append(task)
                self.tasks_by_id[task_id] = task
                self.task_id_counter += 1
                
                # Mark as dirty and schedule save
                self._dirty = True
                self._schedule_save()
                
                return task_id
                
            except Exception as e:
                print(f"Error adding task for user {self.user_id}: {e}")
                return None
    
    def search_tasks(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for tasks using semantic similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of task dictionaries with similarity scores
        """
        with self._lock:
            if len(self.tasks) == 0:
                return []
            
            # Generate embedding for the query
            query_embedding = self.model.encode([query])[0]
            
            # Search in FAISS index
            scores, indices = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                min(k, len(self.tasks))
            )
            
            # Return tasks with scores
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.tasks):
                    task = self.tasks[idx].copy()
                    task['similarity_score'] = float(score)
                    results.append(task)
            
            return results
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a task by its ID (O(1) lookup)."""
        return self.tasks_by_id.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """
        Update a task's properties.
        
        Args:
            task_id: ID of the task to update
            **kwargs: Properties to update
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            task = self.get_task_by_id(task_id)
            if not task:
                return False
            
            # Update task properties
            for key, value in kwargs.items():
                if key in task:
                    task[key] = value
            
            task['updated_at'] = datetime.now().isoformat()
            
            # Recompute embedding if title, description, or tags changed
            if any(key in kwargs for key in ['title', 'description', 'tags']):
                self._recompute_task_embedding(task_id)
            
            # Mark as dirty and schedule save
            self._dirty = True
            self._schedule_save()
            
            return True
    
    def _recompute_task_embedding(self, task_id: str):
        """Recompute embedding for a specific task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return
        
        # Find the task index in the list
        task_idx = None
        for i, t in enumerate(self.tasks):
            if t['id'] == task_id:
                task_idx = i
                break
        
        if task_idx is None:
            return
        
        # Generate new embedding
        task_text = f"{task['title']} {task['description']} {' '.join(task['tags'])}"
        new_embedding = self.model.encode([task_text])[0]
        
        # Remove old embedding and add new one
        # Note: FAISS doesn't support direct updates, so we need to rebuild the index
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild the FAISS index from scratch."""
        # Create new index
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Batch encode all tasks for better performance
        if self.tasks:
            task_texts = []
            for task in self.tasks:
                task_text = f"{task['title']} {task['description']} {' '.join(task['tags'])}"
                task_texts.append(task_text)
            
            # Batch encode
            embeddings = self.model.encode(task_texts)
            
            # Add all embeddings to index
            self.index.add(embeddings.astype(np.float32))
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            task = self.get_task_by_id(task_id)
            if not task:
                return False
            
            # Remove from tasks list and lookup
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.tasks_by_id.pop(task_id, None)
            
            # Rebuild index without the deleted task
            self._rebuild_index()
            
            # Mark as dirty and schedule save
            self._dirty = True
            self._schedule_save()
            
            return True
    
    def get_all_tasks(self, status: str = None, priority: str = None) -> List[Dict]:
        """
        Get all tasks with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            
        Returns:
            List of task dictionaries
        """
        with self._lock:
            tasks = self.tasks.copy()
            
            if status:
                tasks = [t for t in tasks if t['status'] == status]
            
            if priority:
                tasks = [t for t in tasks if t['priority'] == priority]
            
            return tasks
    
    def get_task_statistics(self) -> Dict:
        """Get statistics about stored tasks."""
        with self._lock:
            if not self.tasks:
                return {
                    'total_tasks': 0,
                    'by_status': {},
                    'by_priority': {}
                }
            
            stats = {
                'total_tasks': len(self.tasks),
                'by_status': defaultdict(int),
                'by_priority': defaultdict(int)
            }
            
            # Count by status and priority in one pass
            for task in self.tasks:
                stats['by_status'][task['status']] += 1
                stats['by_priority'][task['priority']] += 1
            
            # Convert defaultdict to regular dict
            stats['by_status'] = dict(stats['by_status'])
            stats['by_priority'] = dict(stats['by_priority'])
            
            return stats
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        with self._lock:
            try:
                task = self.get_task_by_id(task_id)
                if task:
                    task['completed'] = True
                    task['updated_at'] = datetime.now().isoformat()
                    
                    # Mark as dirty and schedule save
                    self._dirty = True
                    self._schedule_save()
                    
                    return True
                
                return False  # Task not found
                
            except Exception as e:
                print(f"Error completing task: {e}")
                return False
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self._save_timer:
            self._save_timer.cancel()
        
        # Force save if dirty
        if self._dirty:
            self._save_data() 