"""
Debug Susenas Crawler - dengan screenshot
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers import get_crawler
from app.config import Config

def test_susenas_debug():
    """Test Susenas dengan debug mode"""
    print("\n" + "="*70)
    print("🐛 SUSENAS CRAWLER - DEBUG MODE")
    print("="*70)
    
    try:
        # Create crawler
        SusenasCrawler = get_crawler('susenas')
        crawler = SusenasCrawler(
            username=Config.USERNAME,
            password=Config.PASSWORD,
            headless=False  # Visual mode
        )
        
        print("\n1️⃣ Setup Driver...")
        crawler.setup_driver()
        print("   ✅ Driver ready")
        
        print("\n2️⃣ Testing Login...")
        input("   Press Enter to start login...")
        success = crawler.login()
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        input("\n   Check browser - is login successful? Press Enter to continue...")
        
        print("\n3️⃣ Testing Navigation...")
        crawler.navigate_to_data_page()
        print("   ✅ Navigated to SEN")
        
        input("\n   Check browser - on SEN page? Press Enter to continue...")
        
        print("\n4️⃣ Testing First Report URL...")
        report_url = f"{crawler.base_report_url}/pencacahan?wil=17&view=tabel&tgl_his={crawler.today}"
        print(f"   URL: {report_url}")
        crawler.driver.get(report_url)
        time.sleep(3)
        
        input("\n   Check browser - is report page loaded? Press Enter to continue...")
        
        print("\n5️⃣ Looking for export button...")
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            button = WebDriverWait(crawler.driver, 10).until(
                EC.presence_of_element_located((By.ID, "export-excel"))
            )
            print(f"   ✅ Button found: {button.text}")
            print(f"   Button visible: {button.is_displayed()}")
            print(f"   Button enabled: {button.is_enabled()}")
            
            input("\n   Press Enter to click button...")
            button.click()
            print("   ✅ Button clicked")
            
            input("\n   Check if download started. Press Enter to finish...")
            
        except Exception as e:
            print(f"   ❌ Button not found: {e}")
            
            # Try to find any button with 'export' or 'excel'
            print("\n   Looking for alternative buttons...")
            buttons = crawler.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                text = btn.text.lower()
                if 'export' in text or 'excel' in text or 'download' in text:
                    print(f"   Found: {btn.text} (id={btn.get_attribute('id')})")
        
        print("\n✅ Debug session complete")
        input("Press Enter to close browser...")
        
        crawler.driver.quit()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_susenas_debug()
