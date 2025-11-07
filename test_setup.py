"""
Test script untuk memverifikasi SSO BPS crawler setup
Run: .venv\\Scripts\\python.exe test_setup.py
"""

import sys
import os

def test_imports():
    """Test semua dependencies terinstall"""
    print("🔍 Testing imports...")
    try:
        import flask
        print("  ✅ Flask installed")
    except ImportError:
        print("  ❌ Flask not installed")
        return False
    
    try:
        import selenium
        print("  ✅ Selenium installed")
    except ImportError:
        print("  ❌ Selenium not installed")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("  ✅ WebDriver Manager installed")
    except ImportError:
        print("  ❌ WebDriver Manager not installed")
        return False
    
    try:
        import dotenv
        print("  ✅ Python-dotenv installed")
    except ImportError:
        print("  ❌ Python-dotenv not installed")
        return False
    
    return True

def test_env_file():
    """Test .env file exists"""
    print("\n🔍 Testing .env file...")
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
        
        # Read and check basic config
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'TARGET_URL=' in content:
            print("  ✅ TARGET_URL configured")
        else:
            print("  ⚠️  TARGET_URL not configured")
            
        if 'USERNAME=' in content:
            print("  ✅ USERNAME configured")
        else:
            print("  ⚠️  USERNAME not configured")
            
        if 'PASSWORD=' in content:
            print("  ✅ PASSWORD configured")
        else:
            print("  ⚠️  PASSWORD not configured")
        
        return True
    else:
        print("  ❌ .env file not found")
        print("  💡 Run: Copy-Item .env.example .env")
        return False

def test_directories():
    """Test required directories exist"""
    print("\n🔍 Testing directories...")
    
    dirs = ['app', 'downloads', 'logs', 'app/templates']
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/ exists")
        else:
            print(f"  ❌ {dir_name}/ not found")
            all_exist = False
    
    return all_exist

def test_app_files():
    """Test app files exist"""
    print("\n🔍 Testing app files...")
    
    files = [
        'run.py',
        'app/__init__.py',
        'app/config.py',
        'app/crawler.py',
        'app/routes.py',
        'app/templates/index.html'
    ]
    
    all_exist = True
    
    for file_name in files:
        if os.path.exists(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} not found")
            all_exist = False
    
    return all_exist

def test_sso_handler():
    """Test SSO handler exists in crawler"""
    print("\n🔍 Testing SSO handler...")
    
    try:
        with open('app/crawler.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '_handle_sso_bps_login' in content:
            print("  ✅ SSO BPS handler implemented")
        else:
            print("  ❌ SSO BPS handler not found")
            return False
        
        if 'sso.bps.go.id' in content:
            print("  ✅ SSO BPS detection implemented")
        else:
            print("  ⚠️  SSO BPS detection might be missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading crawler.py: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Web Crawler SSO BPS - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Environment File", test_env_file()))
    results.append(("Directories", test_directories()))
    results.append(("App Files", test_app_files()))
    results.append(("SSO Handler", test_sso_handler()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Setup is complete.")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your SSO BPS credentials")
        print("2. Run: .venv\\Scripts\\python.exe run.py")
        print("3. Open: http://localhost:5000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
