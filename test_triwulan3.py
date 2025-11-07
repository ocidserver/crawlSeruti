"""
Test script untuk download Triwulan 3
Digunakan untuk testing karena Triwulan 4 belum tersedia
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.crawler import SerutiCrawler
from app.config import Config

def test_triwulan3():
    """Test download data Triwulan 3"""
    
    # Start timing
    start_time = time.time()
    start_datetime = datetime.now()
    
    print("=" * 70)
    print("🧪 TESTING SERUTI CRAWLER - TRIWULAN 3 (HEADLESS)")
    print("=" * 70)
    print(f"Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target URL: {Config.TARGET_URL}")
    print(f"Username: {Config.USERNAME}")
    print(f"Headless: True (background mode)")
    print(f"Override Triwulan: Triwulan III")
    print("=" * 70)
    print()
    
    # Initialize crawler (headless mode)
    crawler = SerutiCrawler(headless=True)
    
    # Track timing for each step
    timings = {}
    
    try:
        # Setup driver
        step_start = time.time()
        print("📦 Setting up browser...")
        crawler.setup_driver()
        timings['setup'] = time.time() - step_start
        print(f"✅ Browser ready ({timings['setup']:.2f}s)")
        print()
        
        # Login
        step_start = time.time()
        print("🔐 Logging in to Seruti...")
        crawler.login_seruti()
        timings['login'] = time.time() - step_start
        print(f"✅ Login successful ({timings['login']:.2f}s)")
        print()
        
        # Navigate to Progres
        step_start = time.time()
        print("🧭 Navigating to Progres page...")
        crawler.navigate_to_progres()
        timings['navigate'] = time.time() - step_start
        print(f"✅ Navigation successful ({timings['navigate']:.2f}s)")
        print()
        
        # Process Progres page with Triwulan III override
        step_start = time.time()
        print("📊 Processing Progres page (Triwulan III)...")
        crawler.process_progres_page(override_triwulan="Triwulan III")
        timings['process'] = time.time() - step_start
        print(f"✅ Processing successful ({timings['process']:.2f}s)")
        print()
        
        # Get downloaded files
        downloaded_files = crawler._get_downloaded_files()
        
        # Calculate total time
        total_time = time.time() - start_time
        end_datetime = datetime.now()
        
        print("=" * 70)
        print("📊 TEST RESULT")
        print("=" * 70)
        print(f"Success: True")
        print(f"Message: Download Triwulan III completed successfully")
        if downloaded_files:
            latest_file = downloaded_files[-1]
            print(f"File: {latest_file}")
        print("=" * 70)
        print()
        
        # Performance metrics
        print("⏱️  PERFORMANCE METRICS")
        print("=" * 70)
        print(f"Setup Browser    : {timings['setup']:.2f}s")
        print(f"Login SSO        : {timings['login']:.2f}s")
        print(f"Navigate         : {timings['navigate']:.2f}s")
        print(f"Process & Export : {timings['process']:.2f}s")
        print("-" * 70)
        print(f"TOTAL TIME       : {total_time:.2f}s ({total_time/60:.2f} minutes)")
        print(f"Start            : {start_datetime.strftime('%H:%M:%S')}")
        print(f"End              : {end_datetime.strftime('%H:%M:%S')}")
        print("=" * 70)
        print()
        
        print("✅ TEST PASSED!")
        print()
        
        return True
        
    except Exception as e:
        print("=" * 70)
        print("📊 TEST RESULT")
        print("=" * 70)
        print(f"Success: False")
        print(f"Error: {str(e)}")
        print("=" * 70)
        print()
        print("❌ TEST FAILED!")
        print()
        
        return False
        
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        crawler.close()
        print("✅ Cleanup done")

if __name__ == "__main__":
    test_triwulan3()
