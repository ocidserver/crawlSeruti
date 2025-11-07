"""
Base Crawler Class
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from app.config import Config
from app.download_log import download_logger

class BaseCrawler(ABC):
    """Base class untuk semua crawler"""
    
    def __init__(self, username=None, password=None, headless=None, task_name=None):
        self.username = username or Config.USERNAME
        self.password = password or Config.PASSWORD
        self.headless = headless if headless is not None else Config.HEADLESS_MODE
        self.driver = None
        self.download_path = Config.DOWNLOAD_PATH
        self.source_name = self.__class__.__name__  # Nama crawler
        self.task_name = task_name  # Nama task dari scheduler
        
    def setup_driver(self):
        """Setup Chrome WebDriver dengan konfigurasi download"""
        try:
            logging.info("Setting up Chrome WebDriver...")
            chrome_options = Options()
            
            # Set headless mode
            if self.headless:
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--disable-gpu')
            
            # Additional options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance optimizations
            chrome_options.page_load_strategy = 'eager'
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--log-level=3')
            
            # Set download preferences
            prefs = {
                "download.default_directory": self.download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize driver with better error handling
            try:
                logging.info("Installing/updating ChromeDriver...")
                driver_path = ChromeDriverManager().install()
                logging.info(f"ChromeDriver reported path: {driver_path}")
                
                # Fix webdriver-manager path issue
                if not driver_path.endswith('.exe'):
                    # Find the actual chromedriver.exe in the directory
                    driver_dir = os.path.dirname(driver_path)
                    for file in os.listdir(driver_dir):
                        if file == 'chromedriver.exe':
                            driver_path = os.path.join(driver_dir, file)
                            logging.info(f"Found actual chromedriver: {driver_path}")
                            break
                
                if not os.path.exists(driver_path):
                    raise Exception(f"ChromeDriver not found at: {driver_path}")
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(Config.BROWSER_TIMEOUT)
                
                logging.info("✅ WebDriver initialized successfully")
                return True
                
            except Exception as driver_error:
                logging.error(f"ChromeDriver initialization failed: {str(driver_error)}")
                logging.info("Trying to reinstall ChromeDriver...")
                
                # Try to clean cache and reinstall
                import shutil
                cache_path = os.path.join(os.path.expanduser('~'), '.wdm')
                if os.path.exists(cache_path):
                    logging.info(f"Cleaning cache: {cache_path}")
                    try:
                        shutil.rmtree(cache_path)
                    except:
                        pass
                
                # Retry installation
                driver_path = ChromeDriverManager().install()
                
                # Fix path again
                if not driver_path.endswith('.exe'):
                    driver_dir = os.path.dirname(driver_path)
                    for file in os.listdir(driver_dir):
                        if file == 'chromedriver.exe':
                            driver_path = os.path.join(driver_dir, file)
                            break
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(Config.BROWSER_TIMEOUT)
                
                logging.info("✅ WebDriver initialized successfully (after retry)")
                return True
            
        except Exception as e:
            logging.error(f"Setup driver error: {str(e)}")
            raise
    
    @abstractmethod
    def login(self):
        """Login method - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def navigate_to_data_page(self):
        """Navigate to data page - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def get_data_date(self):
        """Get data date from page - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def download_data(self):
        """Download data - must be implemented by subclass"""
        pass
    
    def check_if_should_download(self, data_tanggal):
        """
        Check if should download based on log
        
        Returns:
            (should_download: bool, reason: str)
        """
        # Check if already downloaded
        exists = download_logger.check_if_exists(self.source_name, data_tanggal)
        
        if exists:
            logging.info(f"⏭️  Data tanggal {data_tanggal} sudah pernah didownload")
            return False, f"Data {data_tanggal} sudah ada"
        else:
            logging.info(f"✅ Data tanggal {data_tanggal} belum ada, akan didownload")
            return True, f"Data {data_tanggal} baru"
    
    def log_download(self, filename, data_tanggal=None):
        """Log download ke database"""
        download_logger.add_download(
            nama_file=filename,
            tanggal_download=datetime.now(),
            laman_web=self.source_name,
            data_tanggal=data_tanggal,
            task_name=self.task_name
        )
    
    def _wait_for_download(self, timeout=30, check_recent=True):
        """
        Wait for download to complete
        
        Args:
            timeout: Maximum wait time in seconds
            check_recent: If True, also check for files modified during wait period
        """
        logging.info("⏳ Waiting for download to complete...")
        
        download_path = Config.DOWNLOAD_PATH
        if not os.path.isabs(download_path):
            download_path = os.path.join(os.getcwd(), download_path)
        
        # Get initial state with timestamps
        initial_files = {}
        if os.path.exists(download_path):
            for f in os.listdir(download_path):
                fpath = os.path.join(download_path, f)
                if os.path.isfile(fpath):
                    initial_files[f] = os.path.getmtime(fpath)
        
        start_time = time.time()
        check_interval = 0.5
        found_new_file = None
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            
            if not os.path.exists(download_path):
                continue
            
            current_files = set(os.listdir(download_path))
            
            # Check for files in progress
            in_progress = any(f.endswith(('.crdownload', '.tmp', '.part')) for f in current_files)
            
            if in_progress:
                # Still downloading, reset found file and continue waiting
                found_new_file = None
                continue
            
            # Check for NEW files
            new_files = current_files - set(initial_files.keys())
            if new_files:
                # Filter out temp files
                actual_new = [f for f in new_files if not f.endswith(('.crdownload', '.tmp', '.part', '.gitkeep'))]
                if actual_new:
                    found_new_file = actual_new[0]
                    # Wait a bit more to ensure download is complete
                    time.sleep(1)
                    # Check if still no .crdownload files
                    current_files = set(os.listdir(download_path))
                    in_progress = any(f.endswith(('.crdownload', '.tmp', '.part')) for f in current_files)
                    if not in_progress:
                        logging.info(f"✅ New file downloaded: {found_new_file}")
                        return found_new_file
            
            # Check for MODIFIED files (recently downloaded) - only if check_recent is True
            if check_recent and not found_new_file:
                for f in current_files:
                    if f.endswith(('.crdownload', '.tmp', '.part', '.gitkeep')):
                        continue
                    fpath = os.path.join(download_path, f)
                    if os.path.isfile(fpath):
                        mtime = os.path.getmtime(fpath)
                        # If file was modified after we started waiting
                        if mtime >= start_time - 1:  # 1 second buffer before start
                            # And it's either new or modified since initial check
                            if f not in initial_files or mtime > initial_files[f]:
                                # Wait a bit to ensure it's complete
                                time.sleep(1)
                                current_files_check = set(os.listdir(download_path))
                                in_progress = any(x.endswith(('.crdownload', '.tmp', '.part')) for x in current_files_check)
                                if not in_progress:
                                    logging.info(f"✅ File downloaded: {f}")
                                    return f
        
        logging.warning("⚠️ Download timeout or no new files detected")
        return None
    
    def _get_latest_downloads(self):
        """Get latest downloaded files"""
        try:
            files = []
            for filename in os.listdir(self.download_path):
                filepath = os.path.join(self.download_path, filename)
                if os.path.isfile(filepath) and not filename.startswith('.'):
                    files.append(filename)
            return sorted(files, key=lambda x: os.path.getmtime(os.path.join(self.download_path, x)), reverse=True)[:5]
        except Exception as e:
            logging.error(f"Error getting downloads: {str(e)}")
            return []
    
    def _get_recent_downloads(self, since_timestamp, time_window=300):
        """
        Get files downloaded within a time window
        
        Args:
            since_timestamp: Unix timestamp to check from
            time_window: Time window in seconds (default 300 = 5 minutes)
        
        Returns:
            List of filenames downloaded within the time window
        """
        try:
            recent_files = []
            cutoff_time = since_timestamp - 5  # 5 second buffer before start
            
            if not os.path.exists(self.download_path):
                return recent_files
            
            for filename in os.listdir(self.download_path):
                # Skip temp files and hidden files
                if filename.startswith('.') or filename.endswith(('.crdownload', '.tmp', '.part')):
                    continue
                
                filepath = os.path.join(self.download_path, filename)
                if os.path.isfile(filepath):
                    mtime = os.path.getmtime(filepath)
                    # Check if file was modified within time window from start
                    if mtime >= cutoff_time:
                        recent_files.append(filename)
            
            # Sort by modification time (newest first)
            recent_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(self.download_path, x)), 
                reverse=True
            )
            
            logging.info(f"   Found {len(recent_files)} files downloaded since {datetime.fromtimestamp(cutoff_time).strftime('%H:%M:%S')}")
            
            return recent_files
            
        except Exception as e:
            logging.error(f"Error getting recent downloads: {str(e)}")
            return []
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed")
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")
    
    def run(self):
        """
        Main run method - template pattern
        
        Returns:
            dict: Result of crawl
        """
        try:
            logging.info("=" * 70)
            logging.info(f"🚀 STARTING {self.source_name}")
            logging.info("=" * 70)
            
            # Step 1: Setup
            self.setup_driver()
            
            # Step 2: Login
            self.login()
            
            # Step 3: Navigate to data page
            self.navigate_to_data_page()
            
            # Step 4: Get data date
            data_tanggal = self.get_data_date()
            logging.info(f"📅 Data tanggal: {data_tanggal}")
            
            # Step 5: Check if should download
            should_download, reason = self.check_if_should_download(data_tanggal)
            
            if not should_download:
                logging.info(f"⏭️  Skip download: {reason}")
                return {
                    'success': True,
                    'skipped': True,
                    'message': reason,
                    'data_tanggal': data_tanggal
                }
            
            # Step 6: Download
            filename = self.download_data()
            
            # Step 7: Log download
            if filename:
                self.log_download(filename, data_tanggal)
            
            logging.info("=" * 70)
            logging.info("✅ CRAWL COMPLETED SUCCESSFULLY")
            logging.info("=" * 70)
            
            return {
                'success': True,
                'skipped': False,
                'message': f'Downloaded: {filename}',
                'file': filename,
                'data_tanggal': data_tanggal
            }
            
        except Exception as e:
            logging.error(f"❌ Crawl error: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            self.close()
