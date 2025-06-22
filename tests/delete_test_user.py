#!/usr/bin/env python3
"""
Delete Test User Script
"""

import sqlite3
import os

def delete_test_user():
    """Delete the test user from the database."""
    db_path = "users.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find the test user
        cursor.execute("SELECT id, username, email FROM users WHERE username = ? OR email = ?", 
                      ("testuser", "test@example.com"))
        user = cursor.fetchone()
        
        if user:
            user_id, username, email = user
            print(f"🗑️ Found test user: ID={user_id}, Username={username}, Email={email}")
            
            # Delete sessions for this user
            cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            sessions_deleted = cursor.rowcount
            print(f"   Deleted {sessions_deleted} sessions")
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cursor.rowcount > 0:
                print(f"   ✅ User deleted successfully")
                
                conn.commit()
                conn.close()
                return True
            else:
                print("   ❌ Failed to delete user")
                return False
        else:
            print("✅ No test user found in database")
            return True
            
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

if __name__ == "__main__":
    success = delete_test_user()
    if success:
        print("\n🎉 Test user cleanup completed!")
    else:
        print("\n❌ Test user cleanup failed!") 