"""
Seruti Crawler - BPS Seruti System
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

class SerutiCrawler(BaseCrawler):
    """Crawler untuk Seruti BPS"""
    
    def __init__(self, username=None, password=None, headless=None):
        super().__init__(username, password, headless)
        self.source_name = "Seruti"
        self.target_url = "https://olah.web.bps.go.id/seruti/login/sso"
    
    def login(self):
        """Login ke Seruti via SSO"""
        try:
            logging.info("🔐 Logging in to Seruti SSO...")
            
            # Navigate to SSO login
            self.driver.get(self.target_url)
            time.sleep(2)
            
            # Find and fill username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Find and fill password
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Press Enter to login
            password_input.send_keys(Keys.RETURN)
            
            # Wait for redirect
            time.sleep(3)
            
            logging.info("✅ Login successful")
            return True
            
        except Exception as e:
            logging.error(f"❌ Login failed: {str(e)}")
            raise
    
    def navigate_to_data_page(self):
        """Navigate to Progres page"""
        try:
            logging.info("🧭 Navigating to Progres page...")
            
            progres_url = "https://olah.web.bps.go.id/seruti/progres#/"
            self.driver.get(progres_url)
            time.sleep(3)
            
            logging.info("✅ Navigation successful")
            return True
            
        except Exception as e:
            logging.error(f"❌ Navigation failed: {str(e)}")
            raise
    
    def get_data_date(self):
        """
        Get kondisi data tanggal from progres page
        
        Returns:
            str: Data date in format YYYY-MM-DD or description
        """
        try:
            logging.info("📅 Getting data date...")
            
            # Try to find kondisi data element
            try:
                kondisi_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ml-2"))
                )
                kondisi_text = kondisi_elem.text
                logging.info(f"   Kondisi data: {kondisi_text}")
                
                # Extract date from text (format: "Kondisi data tanggal 01 November 2025 jam 10:00")
                date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', kondisi_text)
                if date_match:
                    day = date_match.group(1).zfill(2)
                    month_name = date_match.group(2)
                    year = date_match.group(3)
                    
                    # Convert month name to number
                    months = {
                        'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04',
                        'Mei': '05', 'Juni': '06', 'Juli': '07', 'Agustus': '08',
                        'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'
                    }
                    month = months.get(month_name, '01')
                    
                    data_date = f"{year}-{month}-{day}"
                    logging.info(f"   Parsed date: {data_date}")
                    return data_date
                else:
                    # If can't parse, return the text itself
                    return kondisi_text
                    
            except Exception as e:
                logging.warning(f"⚠️ Could not get kondisi data: {str(e)}")
                # Fallback: use current date
                return datetime.now().strftime('%Y-%m-%d')
                
        except Exception as e:
            logging.error(f"❌ Error getting data date: {str(e)}")
            return None
    
    def get_current_triwulan(self):
        """Get current triwulan based on current date"""
        current_month = datetime.now().month
        
        if 1 <= current_month <= 3:
            return "Triwulan I"
        elif 4 <= current_month <= 6:
            return "Triwulan II"
        elif 7 <= current_month <= 9:
            return "Triwulan III"
        else:
            return "Triwulan IV"
    
    def download_data(self, override_triwulan=None):
        """
        Download data from progres page
        
        Args:
            override_triwulan: Optional override for testing
        """
        try:
            logging.info("📥 Starting download process...")
            
            # Step 1: Select tabel
            logging.info("   Selecting tabel...")
            tabel_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-control.form-control-sm"))
            )
            
            select_tabel = Select(tabel_select)
            try:
                select_tabel.select_by_visible_text("Progres Entri per Kab/Kota")
                logging.info("   ✅ Selected: Progres Entri per Kab/Kota")
            except:
                for option in select_tabel.options:
                    if "Progres Entri" in option.text and "Kab/Kota" in option.text:
                        select_tabel.select_by_visible_text(option.text)
                        logging.info(f"   ✅ Selected: {option.text}")
                        break
            
            time.sleep(1)
            
            # Step 2: Select triwulan
            if override_triwulan:
                current_triwulan = override_triwulan
                logging.info(f"   [OVERRIDE] Using: {current_triwulan}")
            else:
                current_triwulan = self.get_current_triwulan()
                logging.info(f"   Auto-detected: {current_triwulan}")
            
            all_selects = self.driver.find_elements(By.CSS_SELECTOR, "select.form-control.form-control-sm")
            
            for select_elem in all_selects:
                try:
                    select_obj = Select(select_elem)
                    options_text = [opt.text for opt in select_obj.options]
                    
                    if any("Triwulan" in opt for opt in options_text):
                        select_obj.select_by_visible_text(current_triwulan)
                        logging.info(f"   ✅ Selected: {current_triwulan}")
                        break
                except:
                    continue
            
            time.sleep(1)
            
            # Step 3: Click Tampilkan
            logging.info("   Clicking Tampilkan...")
            tampilkan_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-sm.btn-primary"))
            )
            tampilkan_button.click()
            time.sleep(1.5)
            
            # Step 4: Click Export
            logging.info("   Clicking Export...")
            export_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(text(), 'Export') or contains(@class, 'export')]"
                ))
            )
            export_button.click()
            time.sleep(2)
            
            # Wait for download
            filename = self._wait_for_download()
            
            if filename:
                logging.info(f"✅ Download successful: {filename}")
                return filename
            else:
                logging.warning("⚠️ Download may have failed")
                return None
                
        except Exception as e:
            logging.error(f"❌ Download failed: {str(e)}")
            raise
