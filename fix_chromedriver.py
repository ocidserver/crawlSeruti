"""
Script untuk clear ChromeDriver cache dan fix WinError 193
Run: .venv\Scripts\python.exe fix_chromedriver.py
"""

import os
import shutil
import sys

def get_cache_paths():
    """Get possible ChromeDriver cache locations"""
    cache_paths = []
    
    # WebDriver Manager cache locations
    home = os.path.expanduser("~")
    
    # Windows cache locations
    cache_locations = [
        os.path.join(home, ".wdm"),
        os.path.join(home, ".cache", "selenium"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'webdriver_manager'),
        os.path.join(os.environ.get('APPDATA', ''), 'webdriver_manager'),
    ]
    
    for location in cache_locations:
        if os.path.exists(location):
            cache_paths.append(location)
    
    return cache_paths

def clear_cache():
    """Clear ChromeDriver cache"""
    print("=" * 60)
    print("🔧 ChromeDriver Cache Cleaner")
    print("=" * 60)
    
    cache_paths = get_cache_paths()
    
    if not cache_paths:
        print("\n✅ No cache found (this is normal for first run)")
        return True
    
    print(f"\n📁 Found {len(cache_paths)} cache location(s):")
    for path in cache_paths:
        print(f"   - {path}")
    
    print("\n⚠️  This will delete ChromeDriver cache.")
    print("   ChromeDriver will be re-downloaded on next run.")
    
    response = input("\n❓ Continue? (y/n): ").lower().strip()
    
    if response != 'y':
        print("\n❌ Cancelled.")
        return False
    
    print("\n🗑️  Clearing cache...")
    
    for path in cache_paths:
        try:
            shutil.rmtree(path)
            print(f"   ✅ Deleted: {path}")
        except Exception as e:
            print(f"   ⚠️  Could not delete {path}: {e}")
    
    print("\n✅ Cache cleared successfully!")
    print("\n📝 Next steps:")
    print("   1. Run: .venv\\Scripts\\python.exe run.py")
    print("   2. ChromeDriver will be downloaded fresh")
    
    return True

def check_chrome_installed():
    """Check if Chrome is installed"""
    print("\n" + "=" * 60)
    print("🔍 Checking Chrome Installation")
    print("=" * 60)
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"\n✅ Chrome found: {path}")
            chrome_found = True
            
            # Try to get version
            try:
                import subprocess
                result = subprocess.run([path, '--version'], capture_output=True, text=True)
                version = result.stdout.strip()
                print(f"   Version: {version}")
            except:
                pass
            break
    
    if not chrome_found:
        print("\n❌ Chrome not found!")
        print("\n📝 Please install Google Chrome:")
        print("   https://www.google.com/chrome/")
        return False
    
    return True

def test_import():
    """Test if selenium can be imported"""
    print("\n" + "=" * 60)
    print("🔍 Testing Selenium Import")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        print("\n✅ All imports successful")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\n📝 Run: .venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        return False

def main():
    """Main function"""
    print("\n")
    
    # Test imports
    if not test_import():
        return 1
    
    # Check Chrome
    if not check_chrome_installed():
        return 1
    
    # Clear cache
    if not clear_cache():
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Fix Complete!")
    print("=" * 60)
    print("\n📝 ChromeDriver will be downloaded fresh on next run.")
    print("   If issue persists, ensure:")
    print("   1. Chrome browser is up to date")
    print("   2. Antivirus is not blocking ChromeDriver")
    print("   3. You have internet connection for driver download")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
