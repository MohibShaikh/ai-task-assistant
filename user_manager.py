#!/usr/bin/env python3
"""
User Manager for AI Task Assistant
Handles user authentication, sessions, and user-specific data access.
"""

import os
import json
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import sqlite3

# Import the appropriate memory system
try:
    from pinecone_memory import PineconeMemory
    USE_PINECONE = True
    print("🌐 UserManager: Using Pinecone for vector storage")
except ImportError:
    from vector_memory import VectorMemory
    USE_PINECONE = False
    print("💾 UserManager: Using local FAISS for vector storage")

class UserManager:
    def __init__(self, db_path: str = "users.db"):
        """Initialize the user manager."""
        self.db_path = db_path
        self.sessions = {}  # In-memory session storage (use Redis in production)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for user management."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """Register a new user."""
        try:
            # Hash the password with bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Username or email already exists"}
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Create user-specific vector memory
            self._create_user_vector_memory(str(user_id))
            
            return {"success": True, "user_id": user_id, "message": "User registered successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login_user(self, username: str, password: str) -> Dict:
        """Login a user and create a session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find user
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE (username = ? OR email = ?) AND is_active = 1",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"success": False, "error": "Invalid credentials"}
            
            user_id, username, email, password_hash = user
            
            # Verify password with bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                conn.close()
                return {"success": False, "error": "Invalid credentials"}
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=30)  # 30-day session
            
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
                (session_id, user_id, expires_at)
            )
            
            conn.commit()
            conn.close()
            
            # Store session in memory
            self.sessions[session_id] = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "expires_at": expires_at
            }
            
            return {
                "success": True,
                "session_id": session_id,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login_user_by_email(self, email: str) -> Dict:
        """Login a user by email (for OAuth flows)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find user by email
            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = ? AND is_active = 1",
                (email,)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"success": False, "error": "User not found"}
            
            user_id, username, email = user
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=30)  # 30-day session
            
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
                (session_id, user_id, expires_at)
            )
            
            conn.commit()
            conn.close()
            
            # Store session in memory
            self.sessions[session_id] = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "expires_at": expires_at
            }
            
            return {
                "success": True,
                "session_id": session_id,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout_user(self, session_id: str) -> bool:
        """Logout a user by invalidating their session."""
        try:
            # Remove from memory
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False
    
    def get_user_from_session(self, session_id: str) -> Optional[Dict]:
        """Get user information from session ID."""
        # Check memory first
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session["expires_at"] > datetime.now():
                return session
            else:
                # Session expired, remove it
                del self.sessions[session_id]
        
        # Check database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.user_id, u.username, u.email, s.expires_at 
                FROM sessions s 
                JOIN users u ON s.user_id = u.id 
                WHERE s.session_id = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, username, email, expires_at = result
                session_data = {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "expires_at": datetime.fromisoformat(expires_at)
                }
                # Cache in memory
                self.sessions[session_id] = session_data
                return session_data
            
            return None
            
        except Exception as e:
            print(f"Error getting user from session: {e}")
            return None
    
    def get_user_vector_memory(self, user_id: str):
        """Get or create user-specific vector memory."""
        if USE_PINECONE:
            return PineconeMemory(user_id=user_id)
        else:
            return VectorMemory(user_id=user_id)
    
    def _create_user_vector_memory(self, user_id: str):
        """Create user-specific vector memory (this happens automatically on first access)."""
        try:
            if USE_PINECONE:
                memory = PineconeMemory(user_id=user_id)
                print(f"Created Pinecone memory for user {user_id}")
            else:
                memory = VectorMemory(user_id=user_id)
                print(f"Created local vector memory for user {user_id}")
        except Exception as e:
            print(f"Error creating vector memory for user {user_id}: {e}")
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and their data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete user sessions
            cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            # Clean up vector memory files (for local storage)
            if not USE_PINECONE:
                try:
                    index_file = f"task_index_{user_id}.faiss"
                    metadata_file = f"task_metadata_{user_id}.pkl"
                    
                    if os.path.exists(index_file):
                        os.remove(index_file)
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
                except Exception as e:
                    print(f"Error cleaning up vector memory files: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute("SELECT username, email, created_at, last_login FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {}
            
            username, email, created_at, last_login = user
            
            # Get session count
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
            session_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at,
                "last_login": last_login,
                "active_sessions": session_count
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} expired sessions")
                
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user information by email."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = ? AND is_active = 1",
                (email,)
            )
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_id, username, email = user
                return {
                    "user_id": user_id,
                    "username": username,
                    "email": email
                }
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None 