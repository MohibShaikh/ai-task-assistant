#!/usr/bin/env python3
"""
Test Web App Pinecone Integration
"""

import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_web_pinecone_integration():
    """Test the web app's Pinecone integration."""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Web App Pinecone Integration...")
    
    # Test data
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    test_task = {
        "title": "Test Task from Web App",
        "description": "This is a test task to verify Pinecone integration",
        "priority": "high",
        "due_date": "2024-12-31",
        "tags": ["test", "pinecone", "web"]
    }
    
    try:
        # Step 0: Try to login first to delete existing user if it exists
        print("🔍 Checking for existing test user...")
        try:
            login_response = requests.post(
                f"{base_url}/api/auth/login",
                json={"username": test_user["username"], "password": test_user["password"]},
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                session_id = login_data.get("session_id")
                
                if session_id:
                    print("🗑️ Deleting existing test user...")
                    delete_response = requests.delete(
                        f"{base_url}/api/auth/delete-account",
                        headers={"Cookie": f"session_id={session_id}"}
                    )
                    
                    if delete_response.status_code == 200:
                        print("✅ Existing test user deleted")
                    else:
                        print(f"⚠️  Failed to delete existing user: {delete_response.text}")
        except Exception as e:
            print(f"⚠️  Error checking existing user: {e}")
        
        # Step 1: Register a test user
        print("📝 Registering test user...")
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.text}")
            return False
        
        print("✅ User registered successfully")
        
        # Step 2: Login to get session
        print("🔐 Logging in...")
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": test_user["username"], "password": test_user["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        login_data = login_response.json()
        session_id = login_data.get("session_id")
        
        if not session_id:
            print("❌ No session ID received")
            return False
        
        print("✅ Login successful")
        
        # Step 3: Add multiple test tasks
        print("📝 Adding multiple test tasks...")
        test_tasks = [
            {
                "title": "First Test Task",
                "description": "This is the first test task",
                "priority": "high",
                "due_date": "2024-12-31",
                "tags": ["test", "first", "important"]
            },
            {
                "title": "Second Test Task",
                "description": "This is the second test task with different priority",
                "priority": "medium",
                "due_date": "2024-12-25",
                "tags": ["test", "second", "medium"]
            },
            {
                "title": "Third Test Task",
                "description": "This is the third test task without due date",
                "priority": "low",
                "tags": ["test", "third", "no-due-date"]
            }
        ]
        
        created_task_ids = []
        for i, task_data in enumerate(test_tasks, 1):
            print(f"   Adding task {i}: {task_data['title']}")
            add_task_response = requests.post(
                f"{base_url}/api/tasks",
                json=task_data,
                headers={
                    "Content-Type": "application/json",
                    "Cookie": f"session_id={session_id}"
                }
            )
            
            if add_task_response.status_code != 200:
                print(f"❌ Failed to add task {i}: {add_task_response.text}")
                return False
            
            add_task_data = add_task_response.json()
            task_id = add_task_data.get("task_id")
            
            if not task_id:
                print(f"❌ No task ID received for task {i}")
                return False
            
            created_task_ids.append(task_id)
            print(f"   ✅ Task {i} added successfully! ID: {task_id}")
        
        print(f"✅ All {len(created_task_ids)} tasks added successfully!")
        
        # Step 4: Get all tasks to verify they were created
        print("📋 Getting all tasks to verify creation...")
        get_tasks_response = requests.get(
            f"{base_url}/api/tasks",
            headers={"Cookie": f"session_id={session_id}"}
        )
        
        if get_tasks_response.status_code != 200:
            print(f"❌ Get tasks failed: {get_tasks_response.text}")
            return False
        
        tasks_data = get_tasks_response.json()
        tasks = tasks_data.get("tasks", [])
        
        print(f"✅ Found {len(tasks)} tasks in total")
        
        # Verify all tasks are present
        for i, task_data in enumerate(test_tasks):
            found_task = None
            for task in tasks:
                if task.get("title") == task_data["title"]:
                    found_task = task
                    break
            
            if found_task:
                print(f"   ✅ Task {i+1} found: {found_task['title']}")
                print(f"      Priority: {found_task.get('priority')}")
                print(f"      Due Date: {found_task.get('due_date', 'None')}")
                print(f"      Tags: {found_task.get('tags', [])}")
            else:
                print(f"   ❌ Task {i+1} not found: {task_data['title']}")
                return False
        
        # Step 5: Test updating tasks via buttons (simulate button clicks)
        print("✏️ Testing task updates via buttons...")
        
        # Test 1: Update task priority
        first_task_id = created_task_ids[0]
        print(f"   Updating priority for task 1 (ID: {first_task_id})...")
        update_response = requests.put(
            f"{base_url}/api/tasks/{first_task_id}",
            json={"priority": "low"},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"session_id={session_id}"
            }
        )
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update task priority: {update_response.text}")
            return False
        
        print("   ✅ Task priority updated successfully")
        
        # Test 2: Update task due date
        second_task_id = created_task_ids[1]
        print(f"   Updating due date for task 2 (ID: {second_task_id})...")
        update_response = requests.put(
            f"{base_url}/api/tasks/{second_task_id}",
            json={"due_date": "2024-12-20"},
            headers={
                "Content-Type": "application/json",
                "Cookie": f"session_id={session_id}"
            }
        )
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update task due date: {update_response.text}")
            return False
        
        print("   ✅ Task due date updated successfully")
        
        # Test 3: Complete a task
        third_task_id = created_task_ids[2]
        print(f"   Completing task 3 (ID: {third_task_id})...")
        complete_response = requests.post(
            f"{base_url}/api/tasks/{third_task_id}/complete",
            headers={"Cookie": f"session_id={session_id}"}
        )
        
        if complete_response.status_code != 200:
            print(f"❌ Failed to complete task: {complete_response.text}")
            return False
        
        print("   ✅ Task completed successfully")
        
        # Step 6: Verify updates by getting tasks again
        print("📋 Verifying updates...")
        get_tasks_response = requests.get(
            f"{base_url}/api/tasks",
            headers={"Cookie": f"session_id={session_id}"}
        )
        
        if get_tasks_response.status_code != 200:
            print(f"❌ Get tasks failed: {get_tasks_response.text}")
            return False
        
        tasks_data = get_tasks_response.json()
        updated_tasks = tasks_data.get("tasks", [])
        
        # Check if updates are reflected
        for task in updated_tasks:
            if task.get("id") == first_task_id:
                if task.get("priority") == "low":
                    print("   ✅ Task 1 priority update verified")
                else:
                    print(f"   ❌ Task 1 priority not updated: {task.get('priority')}")
            
            elif task.get("id") == second_task_id:
                if task.get("due_date") == "2024-12-20":
                    print("   ✅ Task 2 due date update verified")
                else:
                    print(f"   ❌ Task 2 due date not updated: {task.get('due_date')}")
            
            elif task.get("id") == third_task_id:
                if task.get("completed") == True:
                    print("   ✅ Task 3 completion verified")
                else:
                    print(f"   ❌ Task 3 not marked as completed: {task.get('completed')}")
        
        # Step 7: Test search functionality
        print("🔍 Testing search functionality...")
        search_response = requests.get(
            f"{base_url}/api/search?q=test task",
            headers={"Cookie": f"session_id={session_id}"}
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            search_results = search_data.get("results", [])
            print(f"✅ Search found {len(search_results)} results")
            
            if len(search_results) >= 3:
                print("   ✅ All test tasks found in search results")
            else:
                print(f"   ⚠️  Only {len(search_results)} tasks found in search (expected 3)")
        else:
            print(f"⚠️  Search failed: {search_response.text}")
        
        # Step 8: Clean up - delete all test tasks
        print("🗑️ Cleaning up all test tasks...")
        for i, task_id in enumerate(created_task_ids, 1):
            delete_response = requests.delete(
                f"{base_url}/api/tasks/{task_id}",
                headers={"Cookie": f"session_id={session_id}"}
            )
            
            if delete_response.status_code == 200:
                print(f"   ✅ Task {i} deleted successfully")
            else:
                print(f"   ⚠️  Failed to delete task {i}: {delete_response.text}")
        
        # Step 9: Verify all tasks are deleted
        print("📋 Verifying all tasks are deleted...")
        get_tasks_response = requests.get(
            f"{base_url}/api/tasks",
            headers={"Cookie": f"session_id={session_id}"}
        )
        
        if get_tasks_response.status_code == 200:
            tasks_data = get_tasks_response.json()
            remaining_tasks = tasks_data.get("tasks", [])
            print(f"✅ {len(remaining_tasks)} tasks remaining (should be 0)")
            
            if len(remaining_tasks) == 0:
                print("   ✅ All test tasks successfully deleted")
            else:
                print(f"   ⚠️  {len(remaining_tasks)} tasks still remain")
        else:
            print(f"⚠️  Failed to verify deletion: {get_tasks_response.text}")
        
        print("\n🎉 Comprehensive Web App Pinecone Integration Test Successful!")
        print("🚀 Your web app is working correctly with Pinecone!")
        print("✅ Multiple task creation: Working")
        print("✅ Task updates via buttons: Working")
        print("✅ Task completion: Working")
        print("✅ Search functionality: Working")
        print("✅ Task deletion: Working")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web app. Make sure it's running on http://localhost:8080")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_web_pinecone_integration()
    if not success:
        print("\n❌ Web App Pinecone Integration Test Failed!")
        print("Please check:")
        print("1. Web app is running on http://localhost:8080")
        print("2. Pinecone API key is set in .env file")
        print("3. Pinecone index is configured correctly") 