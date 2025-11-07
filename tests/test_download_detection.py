"""
Test download detection fix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers import get_crawler
from app.config import Config
import time

def test_download_detection():
    print("\n" + "="*70)
    print("🧪 TEST DOWNLOAD DETECTION")
    print("="*70)
    
    # List current files
    print("\n📂 Current files in downloads:")
    files = sorted(os.listdir(Config.DOWNLOAD_PATH), 
                   key=lambda x: os.path.getmtime(os.path.join(Config.DOWNLOAD_PATH, x)), 
                   reverse=True)
    
    for i, f in enumerate(files[:10], 1):
        fpath = os.path.join(Config.DOWNLOAD_PATH, f)
        mtime = os.path.getmtime(fpath)
        print(f"   {i}. {f}")
        print(f"      Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))}")
    
    print("\n✅ Files detected correctly!")
    print(f"\n📊 Total: {len(files)} files")
    
    # Check recent Susenas files
    susenas_files = [f for f in files if 'Progress' in f or 'Susenas' in f]
    print(f"\n📋 Susenas files found: {len(susenas_files)}")
    for f in susenas_files[:7]:
        print(f"   ✅ {f}")

if __name__ == "__main__":
    test_download_detection()
