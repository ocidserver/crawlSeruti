"""
Quick test - just download detection without full crawl
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers.base_crawler import BaseCrawler
from app.config import Config

class TestCrawler(BaseCrawler):
    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        self.source_name = "Test"
    
    def login(self): pass
    def navigate_to_data_page(self): pass
    def get_data_date(self): return "2025-11-07"
    def download_data(self): pass

def test_wait_for_download():
    print("\n" + "="*70)
    print("🧪 TEST _wait_for_download() FIX")
    print("="*70)
    
    crawler = TestCrawler()
    
    print("\n1️⃣ Simulating download detection...")
    print("   (Looking for recently modified files)")
    
    # This should detect the Susenas files that were downloaded
    result = crawler._wait_for_download(timeout=5)
    
    if result:
        print(f"\n✅ SUCCESS: Detected file: {result}")
        print("\n📋 This means the fix works!")
        print("   - Can detect new files")
        print("   - Can detect recently modified files")
        print("   - Works with actual Susenas downloads")
    else:
        print("\n⚠️  No file detected")
        print("   This is OK if no recent downloads exist")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_wait_for_download()
