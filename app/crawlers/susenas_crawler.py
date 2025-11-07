"""
Susenas Crawler - BPS Web Monitoring System
Downloads 7 Excel files from different progress reports
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import re
from datetime import datetime
from app.crawlers.base_crawler import BaseCrawler
from app.config import Config

class SusenasCrawler(BaseCrawler):
    """
    Crawler untuk Susenas BPS - Web Monitoring System
    Mengunduh 7 laporan progress dalam 1x crawl:
    1. Laporan Pencacahan
    2. Laporan Pemeriksaan (Edcod)
    3. Laporan Pengiriman ke Kabkot
    4. Laporan Penerimaan di Kabkot
    5. Laporan Penerimaan di IPDS
    6. Laporan Pengolahan Dokumen M
    7. Laporan Pengolahan Dokumen KP
    """
    
    def __init__(self, username=None, password=None, headless=None):
        super().__init__(username, password, headless)
        self.source_name = "Susenas"
        
        # SSO Login URL
        self.sso_url = "https://sso.bps.go.id/auth/realms/pegawai-bps/protocol/openid-connect/auth?scope=profile-pegawai%2Cemail&response_type=code&approval_prompt=auto&redirect_uri=https%3A%2F%2Fwebmonitoring.bps.go.id%2F&client_id=03310-webmon-1kw"
        
        # Report URLs (akan di-append dengan tanggal hari ini)
        self.base_report_url = "https://webmonitoring.bps.go.id/sen/progress"
        self.reports = [
            {'name': 'pencacahan', 'label': 'Laporan Pencacahan'},
            {'name': 'edcod', 'label': 'Laporan Pemeriksaan'},
            {'name': 'pengiriman', 'label': 'Laporan Pengiriman ke Kabkot'},
            {'name': 'penerimaan', 'label': 'Laporan Penerimaan di Kabkot'},
            {'name': 'ipds', 'label': 'Laporan Penerimaan di IPDS'},
            {'name': 'pengolahan', 'label': 'Laporan Pengolahan Dokumen M'},
            {'name': 'pengolahan2', 'label': 'Laporan Pengolahan Dokumen KP'},
        ]
        
        # Tanggal hari ini untuk URL
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def login(self):
        """Login ke Susenas melalui SSO BPS (sama seperti Seruti)"""
        try:
            logging.info("🔐 Logging in to Susenas via SSO...")
            
            # Navigate to SSO login page
            self.driver.get(self.sso_url)
            time.sleep(3)
            
            # Wait for username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            logging.info(f"✅ Username entered: {self.username}")
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            logging.info("✅ Password entered")
            
            # Click login button
            login_button = self.driver.find_element(By.ID, "kc-login")
            login_button.click()
            logging.info("🔄 Login button clicked")
            
            # Wait for redirect to dashboard
            time.sleep(5)
            
            # Check if login successful (should redirect to webmonitoring.bps.go.id)
            current_url = self.driver.current_url
            if "webmonitoring.bps.go.id" in current_url:
                logging.info("✅ Login successful - redirected to Web Monitoring")
                return True
            else:
                logging.error(f"❌ Login failed - current URL: {current_url}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Login error: {str(e)}")
            raise
    
    def navigate_to_data_page(self):
        """Navigate to SEN index page"""
        try:
            logging.info("🧭 Navigating to SEN index page...")
            
            # Navigate to SEN main page
            sen_url = "https://webmonitoring.bps.go.id/sen/site/index"
            self.driver.get(sen_url)
            time.sleep(2)
            
            logging.info("✅ Navigation to SEN page successful")
            return True
            
        except Exception as e:
            logging.error(f"❌ Navigation failed: {str(e)}")
            raise
    
    def get_data_date(self):
        """
        Get data date - untuk Susenas menggunakan tanggal hari ini
        
        Returns:
            str: Data date in format YYYY-MM-DD (today's date)
        """
        try:
            logging.info("📅 Getting data date...")
            
            # Susenas menggunakan tanggal hari ini untuk parameter URL
            data_date = self.today
            
            logging.info(f"✅ Data date: {data_date}")
            return data_date
            
        except Exception as e:
            logging.error(f"❌ Error getting data date: {str(e)}")
            raise
    
    def download_data(self):
        """
        Download 7 Excel files from Susenas progress reports
        Returns list of downloaded filenames
        """
        try:
            process_start_time = time.time()
            logging.info("📥 Starting Susenas download process...")
            logging.info(f"   Target date: {self.today}")
            logging.info(f"   Start time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Record start timestamp for checking downloaded files later
            download_start_timestamp = time.time()
            
            # Download each report (without individual file checks)
            for i, report in enumerate(self.reports, 1):
                try:
                    logging.info(f"\n📊 [{i}/7] Downloading {report['label']}...")
                    
                    # Construct URL with today's date
                    report_url = f"{self.base_report_url}/{report['name']}?wil=17&view=tabel&tgl_his={self.today}"
                    logging.info(f"   URL: {report_url}")
                    
                    # Navigate to report page
                    self.driver.get(report_url)
                    time.sleep(2)
                    
                    # Find and click export-excel button
                    export_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "export-excel"))
                    )
                    
                    logging.info("   ✅ Found export button, clicking...")
                    export_button.click()
                    
                    # Wait a bit for download to start
                    time.sleep(1.5)
                    
                except Exception as e:
                    logging.error(f"   ❌ Failed to process {report['label']}: {str(e)}")
                    # Continue with next report even if one fails
                    continue
            
            # Wait a bit more to ensure all downloads complete
            logging.info("\n⏳ Waiting for all downloads to complete...")
            time.sleep(3)
            
            # Now check all files downloaded in the last 5 minutes
            logging.info("\n🔍 Checking downloaded files...")
            downloaded_files = self._get_recent_downloads(
                since_timestamp=download_start_timestamp,
                time_window=300  # 5 minutes
            )
            
            process_end_time = time.time()
            total_duration = process_end_time - process_start_time
            
            # Summary
            logging.info(f"\n📦 Download Summary:")
            logging.info(f"   Total files downloaded: {len(downloaded_files)}/7")
            logging.info(f"   ⏱️  Total duration: {total_duration:.2f} seconds")
            logging.info(f"   End time: {datetime.now().strftime('%H:%M:%S')}")
            
            if downloaded_files:
                logging.info(f"\n📄 Downloaded files:")
                for idx, file in enumerate(downloaded_files, 1):
                    logging.info(f"   {idx}. {file}")
                
                # Return first filename for compatibility
                return downloaded_files[0]
            else:
                raise Exception("No files were downloaded in the last 5 minutes")
                
        except Exception as e:
            logging.error(f"❌ Download process failed: {str(e)}")
            raise

