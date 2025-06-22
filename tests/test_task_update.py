#!/usr/bin/env python3
"""
Test script to verify task update functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_task_update():
    """Test task creation and update functionality."""
    
    # Use timestamp to create unique username
    timestamp = int(time.time())
    username = f"testuser_update_{timestamp}"
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    register_data = {
        "username": username,
        "email": f"test{timestamp}@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code != 200:
        print(f"Registration failed: {response.text}")
        return False
    
    register_result = response.json()
    if not register_result.get('success'):
        print(f"Registration failed: {register_result.get('error')}")
        return False
    
    print("✓ User registered successfully")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        "username": username,
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return False
    
    login_result = response.json()
    if not login_result.get('success'):
        print(f"Login failed: {login_result.get('error')}")
        return False
    
    session_id = login_result.get('session_id')
    headers = {'Authorization': session_id}
    print("✓ Login successful")
    
    # Step 3: Create a task
    print("\n3. Creating a test task...")
    task_data = {
        "title": "Test Task for Update",
        "description": "This is a test task to verify update functionality",
        "priority": "medium",
        "tags": ["test", "update"],
        "due_date": "2024-12-31"
    }
    
    response = requests.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
    if response.status_code != 200:
        print(f"Task creation failed: {response.text}")
        return False
    
    create_result = response.json()
    if not create_result.get('success'):
        print(f"Task creation failed: {create_result.get('error')}")
        return False
    
    task_id = create_result.get('task_id')
    print(f"✓ Task created with ID: {task_id}")
    
    # Step 4: Get the task to verify it was created
    print("\n4. Verifying task was created...")
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get tasks: {response.text}")
        return False
    
    tasks_result = response.json()
    if not tasks_result.get('success'):
        print(f"Failed to get tasks: {tasks_result.get('error')}")
        return False
    
    tasks = tasks_result.get('tasks', [])
    created_task = None
    for task in tasks:
        if task.get('id') == task_id:
            created_task = task
            break
    
    if not created_task:
        print("❌ Created task not found in task list")
        return False
    
    print(f"✓ Task found: {created_task.get('title')}")
    
    # Step 5: Update the task
    print("\n5. Updating the task...")
    update_data = {
        "title": "Updated Test Task",
        "description": "This task has been updated successfully",
        "priority": "high",
        "tags": ["test", "updated", "success"],
        "due_date": "2024-12-25"
    }
    
    response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"Task update failed: {response.text}")
        return False
    
    update_result = response.json()
    if not update_result.get('success'):
        print(f"Task update failed: {update_result.get('error')}")
        return False
    
    print("✓ Task updated successfully")
    
    # Step 6: Verify the update
    print("\n6. Verifying the update...")
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get tasks: {response.text}")
        return False
    
    tasks_result = response.json()
    tasks = tasks_result.get('tasks', [])
    updated_task = None
    for task in tasks:
        if task.get('id') == task_id:
            updated_task = task
            break
    
    if not updated_task:
        print("❌ Updated task not found in task list")
        return False
    
    # Check if the update was applied
    if (updated_task.get('title') == update_data['title'] and 
        updated_task.get('description') == update_data['description'] and
        updated_task.get('priority') == update_data['priority']):
        print("✓ Task update verified successfully")
    else:
        print("❌ Task update not properly applied")
        print(f"Expected: {update_data}")
        print(f"Actual: {updated_task}")
        return False
    
    # Step 7: Test stats endpoint
    print("\n7. Testing stats endpoint...")
    response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
    if response.status_code != 200:
        print(f"Stats endpoint failed: {response.text}")
        return False
    
    stats_result = response.json()
    if not stats_result.get('success'):
        print(f"Stats endpoint failed: {stats_result.get('error')}")
        return False
    
    print("✓ Stats endpoint working")
    
    # Step 8: Clean up - delete the task
    print("\n8. Cleaning up - deleting the task...")
    response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
    if response.status_code != 200:
        print(f"Task deletion failed: {response.text}")
        return False
    
    delete_result = response.json()
    if not delete_result.get('success'):
        print(f"Task deletion failed: {delete_result.get('error')}")
        return False
    
    print("✓ Task deleted successfully")
    
    # Step 9: Delete the test user
    print("\n9. Cleaning up - deleting test user...")
    response = requests.delete(f"{BASE_URL}/api/auth/delete-account", headers=headers)
    if response.status_code != 200:
        print(f"User deletion failed: {response.text}")
        return False
    
    delete_result = response.json()
    if not delete_result.get('success'):
        print(f"User deletion failed: {delete_result.get('error')}")
        return False
    
    print("✓ Test user deleted successfully")
    
    print("\n🎉 All tests passed! Task update functionality is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_task_update()
        if not success:
            print("\n❌ Some tests failed. Please check the output above.")
            exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        exit(1) 