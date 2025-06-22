#!/usr/bin/env python3
"""
Test Pinecone Memory System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pinecone_memory():
    """Test the Pinecone memory system."""
    print("🧪 Testing Pinecone Memory System...")
    
    try:
        from pinecone_memory import PineconeMemory
        
        # Create memory instance
        print("📝 Creating Pinecone memory...")
        memory = PineconeMemory(user_id="test_user")
        print("✅ Memory created successfully!")
        
        # Test adding a task
        print("📝 Adding test task...")
        task_id = memory.add_task(
            title="Test Task for Pinecone",
            description="This is a test task to verify Pinecone integration",
            priority="high",
            tags=["test", "pinecone", "integration"]
        )
        print(f"✅ Task added! ID: {task_id}")
        
        # Test getting all tasks
        print("📋 Getting all tasks...")
        tasks = memory.get_all_tasks()
        print(f"✅ Found {len(tasks)} tasks")
        
        # Test search
        print("🔍 Testing search...")
        results = memory.search_tasks("test task", k=3)
        print(f"✅ Search found {len(results)} results")
        
        # Test updating task
        print("✏️ Testing task update...")
        success = memory.update_task(task_id, priority="medium")
        print(f"✅ Task update: {'Success' if success else 'Failed'}")
        
        # Test getting task by ID
        print("🔍 Getting task by ID...")
        task = memory.get_task_by_id(task_id)
        if task:
            print(f"✅ Found task: {task['title']}")
        else:
            print("❌ Task not found")
        
        # Test statistics
        print("📊 Getting statistics...")
        stats = memory.get_task_statistics()
        print(f"✅ Statistics: {stats}")
        
        # Test completing task
        print("✅ Testing task completion...")
        success = memory.complete_task(task_id)
        print(f"✅ Task completion: {'Success' if success else 'Failed'}")
        
        # Cleanup - delete test task
        print("🗑️ Cleaning up test task...")
        success = memory.delete_task(task_id)
        print(f"✅ Task deletion: {'Success' if success else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pinecone_memory()
    if success:
        print("\n🎉 Pinecone Memory System test successful!")
        print("🚀 You can now use Pinecone with your AI Task Assistant!")
    else:
        print("\n❌ Pinecone Memory System test failed!") 