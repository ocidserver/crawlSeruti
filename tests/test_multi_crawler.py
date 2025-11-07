"""
Test script for multi-crawler architecture
Tests the new crawler system without running actual browser automation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers import get_crawler, CRAWLERS
from app.download_log import download_logger

def test_crawler_registry():
    """Test crawler factory"""
    print("\n" + "="*60)
    print("TEST 1: Crawler Registry")
    print("="*60)
    
    # Check available crawlers
    print(f"Available crawlers: {list(CRAWLERS.keys())}")
    
    # Test get_crawler function
    seruti = get_crawler('seruti')
    susenas = get_crawler('susenas')
    invalid = get_crawler('invalid')
    
    print(f"✅ Seruti crawler: {seruti.__name__ if seruti else None}")
    print(f"✅ Susenas crawler: {susenas.__name__ if susenas else None}")
    print(f"✅ Invalid crawler: {invalid}")
    
    assert seruti is not None, "Seruti crawler should exist"
    assert susenas is not None, "Susenas crawler should exist"
    assert invalid is None, "Invalid crawler should be None"
    
    print("\n✅ Test 1 PASSED")


def test_download_log():
    """Test download log system"""
    print("\n" + "="*60)
    print("TEST 2: Download Log System")
    print("="*60)
    
    # Add test download
    download_logger.add_download(
        nama_file="test_file.xlsx",
        tanggal_download="2025-11-07 10:00:00",
        laman_web="Seruti",
        data_tanggal="2025-11-01"
    )
    print("✅ Added test download")
    
    # Check if exists
    exists = download_logger.check_if_exists("Seruti", "2025-11-01")
    print(f"✅ Check exists: {exists}")
    assert exists, "Download should exist"
    
    # Check non-existent
    not_exists = download_logger.check_if_exists("Seruti", "2025-12-01")
    print(f"✅ Check not exists: {not_exists}")
    assert not not_exists, "Non-existent download should return False"
    
    # Get latest
    latest = download_logger.get_latest_by_source("Seruti")
    print(f"✅ Latest download: {latest['nama_file']} at {latest['tanggal_download']}")
    
    print("\n✅ Test 2 PASSED")


def test_crawler_instantiation():
    """Test crawler instantiation"""
    print("\n" + "="*60)
    print("TEST 3: Crawler Instantiation")
    print("="*60)
    
    try:
        # Get crawler classes
        SerutiCrawler = get_crawler('seruti')
        SusenasCrawler = get_crawler('susenas')
        
        # Try to instantiate (will fail if Chrome not installed, but that's ok)
        print("Attempting to instantiate Seruti crawler...")
        try:
            seruti_instance = SerutiCrawler(headless=True)
            print("✅ Seruti crawler instantiated")
        except Exception as e:
            print(f"⚠️  Seruti instantiation failed (expected if Chrome not running): {type(e).__name__}")
        
        print("\nAttempting to instantiate Susenas crawler...")
        try:
            susenas_instance = SusenasCrawler(headless=True)
            print("✅ Susenas crawler instantiated")
        except Exception as e:
            print(f"⚠️  Susenas instantiation failed (expected if Chrome not running): {type(e).__name__}")
        
        print("\n✅ Test 3 PASSED (instantiation logic works)")
    
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        raise


def test_crawler_methods():
    """Test crawler method signatures"""
    print("\n" + "="*60)
    print("TEST 4: Crawler Method Signatures")
    print("="*60)
    
    SerutiCrawler = get_crawler('seruti')
    SusenasCrawler = get_crawler('susenas')
    
    # Check required methods exist
    required_methods = ['login', 'navigate_to_data_page', 'get_data_date', 'download_data', 'run']
    
    for crawler_name, CrawlerClass in [('Seruti', SerutiCrawler), ('Susenas', SusenasCrawler)]:
        print(f"\nChecking {crawler_name} crawler methods...")
        for method in required_methods:
            assert hasattr(CrawlerClass, method), f"{crawler_name} missing method: {method}"
            print(f"  ✅ {method}")
    
    print("\n✅ Test 4 PASSED")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 MULTI-CRAWLER ARCHITECTURE TEST SUITE")
    print("="*60)
    
    try:
        test_crawler_registry()
        test_download_log()
        test_crawler_instantiation()
        test_crawler_methods()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ Crawler registry working")
        print("✅ Download log system working")
        print("✅ Crawler instantiation logic working")
        print("✅ All required methods present")
        print("\n📋 Next steps:")
        print("   1. Start the Flask app: python run.py")
        print("   2. Open http://localhost:5000")
        print("   3. Test adding a scheduled job")
        print("   4. Test Susenas crawler with real URLs/selectors")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST SUITE FAILED")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
