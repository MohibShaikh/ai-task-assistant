import numpy as np
import pinecone
import pickle
import os
from hf_api import HuggingFaceAPI
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import uuid
import threading
from collections import defaultdict
import time

# Global model cache to avoid reloading
_MODEL_CACHE = {}
_MODEL_LOCK = threading.Lock()

# Try to import global model from web_app if available
try:
    from web_app import GLOBAL_MODEL
    _GLOBAL_MODEL_AVAILABLE = GLOBAL_MODEL is not None
except ImportError:
    _GLOBAL_MODEL_AVAILABLE = False

class PineconeMemory:
    def __init__(self, user_id: str = "default", model_name: str = "sentence-transformers/all-mpnet-base-v2", 
                 api_key: str = None, environment: str = None, index_name: str = None):
        """
        Initialize the Pinecone vector memory system for task storage and retrieval.
        
        Args:
            user_id: Unique identifier for the user (creates separate namespaces)
            model_name: Name of the Hugging Face model to use
            api_key: Pinecone API key
            environment: Pinecone environment (e.g., 'us-west1-gcp')
            index_name: Pinecone index name
        """
        self.user_id = user_id
        self.model_name = model_name
        
        # Pinecone configuration
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment or os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'ai-task-assistant')
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize Pinecone (new API)
        self.pc = pinecone.Pinecone(api_key=self.api_key)
        
        # Get or create cached model
        self.model = self._get_cached_model(model_name)
        self.dimension = 768  # Standard dimension for most sentence transformers
        
        # Initialize Pinecone index (simpler approach)
        self.index = self.pc.Index(self.index_name)
        
        # Task metadata storage (local cache for faster access)
        self.tasks = []
        self.tasks_by_id = {}  # O(1) lookup dictionary
        self.task_id_counter = 0
        
        # Performance optimizations
        self._dirty = False  # Track if data needs saving
        self._save_timer = None
        self._save_delay = 2.0  # Save after 2 seconds of inactivity
        self._lock = threading.RLock()  # Thread-safe operations
        
        # Load existing data
        self._load_existing_data()
    
    def _get_cached_model(self, model_name: str) -> HuggingFaceAPI:
        """Get or create a cached model instance."""
        with _MODEL_LOCK:
            # First try to use global model if available
            if _GLOBAL_MODEL_AVAILABLE and model_name == "sentence-transformers/all-mpnet-base-v2":
                try:
                    from web_app import GLOBAL_MODEL
                    if GLOBAL_MODEL is not None:
                        print("✅ Using pre-loaded global model")
                        return GLOBAL_MODEL
                except ImportError:
                    pass
            
            # Fall back to cache
            if model_name not in _MODEL_CACHE:
                print(f"Loading Hugging Face model {model_name}...")
                _MODEL_CACHE[model_name] = HuggingFaceAPI(model_name)
                print(f"Model {model_name} loaded and cached.")
            return _MODEL_CACHE[model_name]
    
    def _load_existing_data(self):
        """Load existing tasks from Pinecone."""
        try:
            # Clear existing local cache first
            self.tasks = []
            self.tasks_by_id = {}
            self.task_id_counter = 0
            
            print(f"🔍 Loading existing tasks for user {self.user_id} from Pinecone...")
            
            # Query all vectors in the user's namespace using fetch instead of query
            try:
                # First, let's try to get all vector IDs in the namespace
                # We'll use a dummy query to get some vectors, then fetch them all
                results = self.index.query(
                    vector=[0] * self.dimension,  # Dummy vector
                    top_k=1000,  # Get up to 1000 vectors
                    include_metadata=True,
                    namespace=self.user_id
                )
                
                print(f"📊 Found {len(results.matches)} vectors in namespace {self.user_id}")
                
                # Extract tasks from metadata
                for match in results.matches:
                    if match.metadata:
                        task = {
                            'id': match.metadata.get('task_id'),
                            'user_id': self.user_id,
                            'title': match.metadata.get('title', ''),
                            'description': match.metadata.get('description', ''),
                            'priority': match.metadata.get('priority', 'medium'),
                            'status': match.metadata.get('status', 'pending'),
                            'tags': match.metadata.get('tags', []),
                            'due_date': match.metadata.get('due_date'),
                            'created_at': match.metadata.get('created_at'),
                            'updated_at': match.metadata.get('updated_at'),
                            'completed': match.metadata.get('completed', False)
                        }
                        
                        if task['id']:
                            self.tasks.append(task)
                            self.tasks_by_id[task['id']] = task
                            # Update task_id_counter to avoid conflicts
                            try:
                                task_num = int(task['id'].split('-')[-1], 16)
                                self.task_id_counter = max(self.task_id_counter, task_num)
                            except (ValueError, IndexError):
                                pass
                
                print(f"✅ Loaded {len(self.tasks)} existing tasks for user {self.user_id} from Pinecone.")
                
            except Exception as e:
                print(f"⚠️ Error querying Pinecone for user {self.user_id}: {e}")
                print("Starting with fresh memory.")
                # Ensure clean state
                self.tasks = []
                self.tasks_by_id = {}
                self.task_id_counter = 0
                
        except Exception as e:
            print(f"❌ Error loading existing data for user {self.user_id}: {e}")
            print("Starting with fresh memory.")
            # Ensure clean state
            self.tasks = []
            self.tasks_by_id = {}
            self.task_id_counter = 0
    
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
        """Save data to Pinecone (this is handled automatically in add/update/delete)."""
        # Pinecone operations are immediate, so this is mainly for cleanup
        pass
    
    def _clean_metadata(self, metadata):
        # Ensure all date fields are strings or omitted
        for key in ["due_date", "created_at", "updated_at"]:
            if key in metadata:
                v = metadata[key]
                if v is None:
                    del metadata[key]
                elif not isinstance(v, str):
                    try:
                        metadata[key] = v.isoformat()
                    except Exception:
                        metadata[key] = str(v)
        return {k: v for k, v in metadata.items() if v is not None}
    
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
                
                print(f"➕ Adding task '{title}' for user {self.user_id} with ID {task_id}")
                
                # Generate embedding for the task
                task_text = f"{title} {description} {' '.join(tags or [])}"
                embedding = self.model.encode([task_text])[0]
                
                # Prepare metadata for Pinecone
                metadata = {
                    'task_id': task_id,
                    'user_id': self.user_id,
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'tags': tags or [],
                    'due_date': due_date,
                    'created_at': task['created_at'],
                    'updated_at': task['updated_at'],
                    'completed': False
                }
                metadata = self._clean_metadata(metadata)
                
                print(f"📤 Upserting task to Pinecone namespace {self.user_id}...")
                
                # Add to Pinecone
                self.index.upsert(
                    vectors=[(task_id, embedding.tolist(), metadata)],
                    namespace=self.user_id
                )
                
                print(f"✅ Task successfully saved to Pinecone")
                
                # Store task metadata locally
                self.tasks.append(task)
                self.tasks_by_id[task_id] = task
                self.task_id_counter += 1
                
                print(f"📋 Local cache updated. Total tasks for user {self.user_id}: {len(self.tasks)}")
                
                return task_id
                
            except Exception as e:
                print(f"❌ Error adding task for user {self.user_id}: {e}")
                import traceback
                traceback.print_exc()
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
            
            try:
                # Generate embedding for the query
                query_embedding = self.model.encode([query])[0]
                
                # Search in Pinecone
                results = self.index.query(
                    vector=query_embedding.tolist(),
                    top_k=min(k, len(self.tasks)),
                    include_metadata=True,
                    namespace=self.user_id
                )
                
                # Return tasks with scores
                results_list = []
                for match in results.matches:
                    if match.metadata:
                        task = {
                            'id': match.metadata.get('task_id'),
                            'user_id': self.user_id,
                            'title': match.metadata.get('title', ''),
                            'description': match.metadata.get('description', ''),
                            'priority': match.metadata.get('priority', 'medium'),
                            'status': match.metadata.get('status', 'pending'),
                            'tags': match.metadata.get('tags', []),
                            'due_date': match.metadata.get('due_date'),
                            'created_at': match.metadata.get('created_at'),
                            'updated_at': match.metadata.get('updated_at'),
                            'completed': match.metadata.get('completed', False),
                            'similarity_score': float(match.score)
                        }
                        results_list.append(task)
                
                return results_list
                
            except Exception as e:
                print(f"Error searching tasks: {e}")
                return []
    
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
            
            try:
                # Recompute embedding if title, description, or tags changed
                if any(key in kwargs for key in ['title', 'description', 'tags']):
                    task_text = f"{task['title']} {task['description']} {' '.join(task['tags'])}"
                    embedding = self.model.encode([task_text])[0]
                else:
                    # Use existing embedding (we'd need to store it, but for now, recompute)
                    task_text = f"{task['title']} {task['description']} {' '.join(task['tags'])}"
                    embedding = self.model.encode([task_text])[0]
                
                # Prepare updated metadata
                metadata = {
                    'task_id': task_id,
                    'user_id': self.user_id,
                    'title': task['title'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'status': task['status'],
                    'tags': task['tags'],
                    'due_date': task['due_date'],
                    'created_at': task['created_at'],
                    'updated_at': task['updated_at'],
                    'completed': task['completed']
                }
                metadata = self._clean_metadata(metadata)
                
                # Update in Pinecone
                self.index.upsert(
                    vectors=[(task_id, embedding.tolist(), metadata)],
                    namespace=self.user_id
                )
                
                return True
                
            except Exception as e:
                print(f"Error updating task: {e}")
                return False
    
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
            
            try:
                # Delete from Pinecone
                self.index.delete(ids=[task_id], namespace=self.user_id)
                
                # Remove from local storage
                self.tasks = [t for t in self.tasks if t['id'] != task_id]
                self.tasks_by_id.pop(task_id, None)
                
                return True
                
            except Exception as e:
                print(f"Error deleting task: {e}")
                return False
    
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
                    
                    # Update in Pinecone
                    return self.update_task(task_id, completed=True)
                
                return False  # Task not found
                
            except Exception as e:
                print(f"Error completing task: {e}")
                return False
    
    def refresh_cache(self):
        """Refresh the local cache with data from Pinecone."""
        self._load_existing_data()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, '_save_timer') and self._save_timer:
            self._save_timer.cancel() 