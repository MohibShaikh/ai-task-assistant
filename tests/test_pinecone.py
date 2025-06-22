#!/usr/bin/env python3
"""
Simple Pinecone Test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pinecone():
    """Test Pinecone connection."""
    print("🧪 Testing Pinecone...")
    
    # Get API key
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        import pinecone
        print("✅ Pinecone package imported successfully")
        
        # Initialize Pinecone
        pc = pinecone.Pinecone(api_key=api_key)
        print("✅ Pinecone initialized successfully")
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"✅ Found {len(indexes)} indexes")
        
        for idx in indexes:
            print(f"  - {idx.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_pinecone()
    if success:
        print("\n🎉 Pinecone test successful!")
    else:
        print("\n❌ Pinecone test failed!") 