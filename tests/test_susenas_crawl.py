"""
Test Susenas Crawler - Actual Crawl Test
Downloads real data from Susenas Web Monitoring
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers import get_crawler
from app.config import Config

def test_susenas_crawl():
    """Test actual Susenas crawl"""
    print("\n" + "="*70)
    print("🧪 SUSENAS CRAWLER - ACTUAL CRAWL TEST")
    print("="*70)
    print(f"📅 Target Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📁 Download Path: {Config.DOWNLOAD_PATH}")
    print(f"👤 Username: {Config.USERNAME}")
    print("="*70)
    
    # Confirm
    print("\n⚠️  This will:")
    print("   1. Login to BPS SSO")
    print("   2. Navigate to Web Monitoring SEN")
    print("   3. Download 7 Excel reports")
    print("   4. Save files to downloads folder")
    
    response = input("\n❓ Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Test cancelled")
        return
    
    print("\n" + "="*70)
    print("🚀 Starting Susenas Crawl Test...")
    print("="*70)
    
    try:
        # Get crawler
        print("\n1️⃣ Initializing Susenas Crawler...")
        SusenasCrawler = get_crawler('susenas')
        
        # Create instance with headless=True for speed test
        crawler = SusenasCrawler(
            username=Config.USERNAME,
            password=Config.PASSWORD,
            headless=True  # Headless mode for performance test
        )
        print("   ✅ Crawler initialized (HEADLESS MODE)")
        
        # Run crawl
        print("\n2️⃣ Running Crawl Process...")
        print("   (Headless mode - no browser window)")
        print("   ⏱️  Timing started...")
        start_time = time.time()
        
        result = crawler.run()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("📊 CRAWL TEST RESULTS")
        print("="*70)
        
        if result.get('success') and not result.get('skipped'):
            print("✅ Status: SUCCESS")
            print(f"⏱️  Duration: {elapsed:.2f} seconds")
            print(f"📄 Files Downloaded: Check {Config.DOWNLOAD_PATH}")
            print(f"📝 Message: {result.get('message', 'N/A')}")
            print(f"📅 Data Date: {result.get('data_tanggal', 'N/A')}")
            
            # List downloaded files
            if os.path.exists(Config.DOWNLOAD_PATH):
                files = sorted([f for f in os.listdir(Config.DOWNLOAD_PATH) 
                              if f.endswith('.xlsx')], 
                              key=lambda x: os.path.getmtime(os.path.join(Config.DOWNLOAD_PATH, x)),
                              reverse=True)
                
                print(f"\n📦 Downloaded Files (latest first):")
                today_str = datetime.now().strftime('%Y-%m-%d')
                today_files = [f for f in files if today_str in f]
                
                if today_files:
                    for i, file in enumerate(today_files[:7], 1):
                        filepath = os.path.join(Config.DOWNLOAD_PATH, file)
                        size_kb = os.path.getsize(filepath) / 1024
                        print(f"   {i}. {file} ({size_kb:.2f} KB)")
                else:
                    print("   ⚠️  No files with today's date found")
                    print("\n   All recent files:")
                    for i, file in enumerate(files[:7], 1):
                        print(f"   {i}. {file}")
        
        elif result.get('success') and result.get('skipped'):
            print("⏭️  Status: SKIPPED")
            print(f"⏱️  Duration: {elapsed:.2f} seconds")
            print(f"📝 Message: {result.get('message', 'Data already exists')}")
            print(f"📅 Data Date: {result.get('data_tanggal', 'N/A')}")
            print("ℹ️  Data untuk tanggal ini sudah pernah didownload")
        
        else:
            print("❌ Status: FAILED")
            print(f"⏱️  Duration: {elapsed:.2f} seconds")
            print(f"📝 Message: {result.get('message', 'Unknown error')}")
            if 'error' in result:
                print(f"🐛 Error: {result['error']}")
        
        print("\n" + "="*70)
        print("🎯 TEST COMPLETE")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        
        import traceback
        print("\n📋 Full Error Trace:")
        traceback.print_exc()
    
    print("\n💡 Tips:")
    print("   - Check console logs above for detailed process")
    print("   - Verify files in downloads folder")
    print("   - Review download_log.json for records")
    print("   - If failed, check credentials in .env")

if __name__ == "__main__":
    test_susenas_crawl()
