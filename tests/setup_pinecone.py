#!/usr/bin/env python3
"""
Pinecone Setup Script
Helps configure and test Pinecone integration for the AI Task Assistant.
"""

import os
import sys
from dotenv import load_dotenv

def setup_pinecone():
    """Setup Pinecone configuration."""
    print("🌲 Pinecone Setup for AI Task Assistant")
    print("=" * 50)
    
    # Load existing environment variables
    load_dotenv()
    
    # Check if Pinecone is already configured
    api_key = os.getenv('PINECONE_API_KEY')
    environment = os.getenv('PINECONE_ENVIRONMENT')
    index_name = os.getenv('PINECONE_INDEX_NAME')
    
    if api_key:
        print(f"✅ Pinecone API Key found: {api_key[:10]}...")
    else:
        print("❌ Pinecone API Key not found")
        api_key = input("Enter your Pinecone API Key: ").strip()
        if not api_key:
            print("❌ API Key is required. Exiting.")
            return False
    
    if not environment:
        print("🌍 Pinecone Environment not set")
        environment = input("Enter your Pinecone Environment (e.g., us-west1-gcp): ").strip()
        if not environment:
            environment = "us-west1-gcp"  # Default
            print(f"Using default environment: {environment}")
    
    if not index_name:
        print("📁 Pinecone Index Name not set")
        index_name = input("Enter your Pinecone Index Name (or press Enter for default): ").strip()
        if not index_name:
            index_name = "ai-task-assistant"
            print(f"Using default index name: {index_name}")
    
    # Save to .env file
    env_content = f"""# Pinecone Configuration
PINECONE_API_KEY={api_key}
PINECONE_ENVIRONMENT={environment}
PINECONE_INDEX_NAME={index_name}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Configuration saved to .env file")
    
    # Test Pinecone connection
    print("\n🧪 Testing Pinecone connection...")
    try:
        import pinecone
        from pinecone_memory import PineconeMemory
        
        # Initialize Pinecone (new API)
        pc = pinecone.Pinecone(api_key=api_key)
        
        # Test connection
        indexes = pc.list_indexes()
        print(f"✅ Connected to Pinecone! Found {len(indexes)} indexes")
        
        # Test creating/accessing index
        index_names = [idx.name for idx in indexes]
        if index_name in index_names:
            print(f"✅ Index '{index_name}' already exists")
        else:
            print(f"📝 Creating new index '{index_name}'...")
            # This will be created automatically when first used
        
        # Test memory creation
        print("🧪 Testing memory creation...")
        test_memory = PineconeMemory(user_id="test", index_name=index_name)
        print("✅ Pinecone memory created successfully!")
        
        # Test basic operations
        print("🧪 Testing basic operations...")
        task_id = test_memory.add_task(
            title="Test Task",
            description="This is a test task for Pinecone setup",
            priority="medium",
            tags=["test", "setup"]
        )
        print(f"✅ Task added successfully! ID: {task_id}")
        
        # Test search
        results = test_memory.search_tasks("test task", k=1)
        print(f"✅ Search works! Found {len(results)} results")
        
        # Cleanup test data
        test_memory.delete_task(task_id)
        print("✅ Test cleanup completed")
        
        print("\n🎉 Pinecone setup completed successfully!")
        print("You can now use the AI Task Assistant with Pinecone vector storage.")
        
        return True
        
    except ImportError:
        print("❌ Pinecone client not installed. Installing...")
        os.system("pip install pinecone-client")
        print("✅ Please run this script again after installation.")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Pinecone: {e}")
        print("Please check your API key and environment settings.")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Pinecone Setup Script")
        print("Usage: python setup_pinecone.py")
        print("This script helps configure Pinecone for the AI Task Assistant.")
        return
    
    success = setup_pinecone()
    if success:
        print("\n🚀 You're ready to use Pinecone!")
        print("Start the web app with: python web_app.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 