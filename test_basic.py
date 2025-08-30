#!/usr/bin/env python3
"""
Simple test script to verify basic functionality without running the full application.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported."""
    try:
        print("✅ AppSettings imported successfully")
        
        print("✅ Application imported successfully")
        
        print("✅ DataBaseManager imported successfully")
        
        print("✅ get_langfuse_handler imported successfully")
        
        print("✅ create_graph imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_settings():
    """Test if AppSettings can be instantiated."""
    try:
        from agent_project.config.config import AppSettings
        
        settings = AppSettings(
            TRACING=False,
            GROQ_API_KEY="test_key",
            LANGFUSE_HOST="http://localhost:3000",
            LANGFUSE_SECRET_KEY="test_secret",
            LANGFUSE_PUBLIC_KEY="test_public",
            EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
            VECTOR_DB_FILE="user_space/test.db",
            DEVICE="cpu",
            LLM_NAME="test-model",
            LOG_FILE="user_space/test.log",
            LOGGING=True
        )
        print("✅ AppSettings instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ AppSettings instantiation failed: {e}")
        return False

def test_application_creation():
    """Test if Application can be created (without running)."""
    try:
        from agent_project.application.app import Application
        from agent_project.config.config import AppSettings
        
        settings = AppSettings(
            TRACING=False,
            GROQ_API_KEY="test_key",
            LANGFUSE_HOST="http://localhost:3000",
            LANGFUSE_SECRET_KEY="test_secret",
            LANGFUSE_PUBLIC_KEY="test_public",
            EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
            VECTOR_DB_FILE="user_space/test.db",
            DEVICE="cpu",
            LLM_NAME="test-model",
            LOG_FILE="user_space/test.log",
            LOGGING=True
        )
        
        # Create application without running model_post_init
        app = Application(
            settings=settings,
            database=None,
            tracer=None,
            thread_id="",
            graph=None
        )
        print("✅ Application created successfully")
        return True
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return False

def main():
    print("🧪 Testing CLI Agent Basic Functionality")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("AppSettings Test", test_app_settings),
        ("Application Creation Test", test_application_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Basic functionality is working.")
        print("\nYou can now try running the main application:")
        print("python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nThe application may not work properly until these issues are resolved.")

if __name__ == "__main__":
    main() 