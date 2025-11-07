"""
Test script untuk Seruti Crawler dengan flow baru
"""
from app.crawler import SerutiCrawler
from app.config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_seruti_flow():
    """Test full Seruti flow: Login SSO -> Dashboard -> Progres"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING SERUTI CRAWLER - NEW FLOW")
    print("=" * 70)
    print(f"Target URL: {Config.TARGET_URL}")
    print(f"Username: {Config.USERNAME}")
    print(f"Headless: False (untuk testing)")
    print("=" * 70 + "\n")
    
    try:
        # Initialize crawler (non-headless untuk testing)
        crawler = SerutiCrawler(
            username=Config.USERNAME,
            password=Config.PASSWORD,
            headless=False  # Set False untuk melihat prosesnya
        )
        
        # Run full crawl dengan flow baru
        result = crawler.run_full_crawl(
            target_url=Config.TARGET_URL
        )
        
        print("\n" + "=" * 70)
        print("📊 TEST RESULT")
        print("=" * 70)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        if result.get('file'):
            print(f"File: {result['file']}")
        if result.get('screenshots'):
            print(f"Screenshots: {', '.join(result['screenshots'])}")
        print("=" * 70 + "\n")
        
        if result['success']:
            print("✅ TEST PASSED!")
        else:
            print("❌ TEST FAILED!")
            
        return result
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}\n")
        return {'success': False, 'message': str(e)}

if __name__ == "__main__":
    test_seruti_flow()
