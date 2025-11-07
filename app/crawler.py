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
from app.config import Config

# Setup logging
logging.basicConfig(
    filename=os.path.join(Config.LOG_PATH, f'crawler_{datetime.now().strftime("%Y%m%d")}.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SerutiCrawler:
    """Web crawler untuk login dan download files dari target website"""
    
    def __init__(self, username=None, password=None, headless=None):
        self.username = username or Config.USERNAME
        self.password = password or Config.PASSWORD
        self.headless = headless if headless is not None else Config.HEADLESS_MODE
        self.driver = None
        self.download_path = Config.DOWNLOAD_PATH
        
    def setup_driver(self):
        """Setup Chrome WebDriver dengan konfigurasi download"""
        try:
            logging.info("Setting up Chrome WebDriver...")
            chrome_options = Options()
            
            # Set headless mode
            if self.headless:
                chrome_options.add_argument('--headless=new')  # Updated headless syntax
                chrome_options.add_argument('--disable-gpu')
            
            # Additional options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance optimizations
            chrome_options.page_load_strategy = 'eager'  # Don't wait for full page load
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--log-level=3')  # Minimal logging
            
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
            logging.info("Installing/updating ChromeDriver...")
            try:
                # Force fresh install of ChromeDriver
                driver_path = ChromeDriverManager().install()
                logging.info(f"ChromeDriver path: {driver_path}")
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(Config.BROWSER_TIMEOUT)
                
                logging.info("WebDriver initialized successfully")
                logging.info(f"Chrome version: {self.driver.capabilities['browserVersion']}")
                return True
                
            except Exception as driver_error:
                logging.error(f"ChromeDriver error: {str(driver_error)}")
                
                # Try alternative: use Selenium Manager (built-in)
                logging.info("Trying with Selenium Manager...")
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.implicitly_wait(Config.BROWSER_TIMEOUT)
                
                logging.info("WebDriver initialized successfully using Selenium Manager")
                return True
            
        except Exception as e:
            logging.error(f"Error setting up WebDriver: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Provide helpful error messages
            error_msg = str(e)
            if "WinError 193" in error_msg or "not a valid Win32 application" in error_msg:
                raise Exception(
                    "ChromeDriver architecture mismatch. "
                    "Please try: 1) Restart application, 2) Clear driver cache, "
                    "3) Ensure Chrome browser is installed and up to date."
                )
            elif "chrome not reachable" in error_msg.lower():
                raise Exception(
                    "Chrome browser not found. Please install Google Chrome: "
                    "https://www.google.com/chrome/"
                )
            else:
                raise Exception(f"Failed to initialize browser: {str(e)}")
    
    def login_seruti(self, target_url=None):
        """
        Login ke Seruti BPS dengan URL SSO langsung:
        1. Buka https://olah.web.bps.go.id/seruti/login/sso (langsung ke SSO)
        2. Isi username & password dari Config
        3. Klik login
        4. Auto-redirect ke dashboard
        
        Args:
            target_url: URL SSO (default dari Config.TARGET_URL)
        """
        try:
            # Gunakan URL SSO langsung
            url = target_url or Config.TARGET_URL
            
            if not url:
                raise Exception("Target URL tidak ditemukan")
            
            logging.info("=" * 70)
            logging.info("🔐 SERUTI SSO LOGIN (Direct)")
            logging.info("=" * 70)
            
            # Step 1: Langsung buka URL SSO
            logging.info(f"📂 Opening SSO page: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            current_url = self.driver.current_url
            logging.info(f"📍 Loaded: {current_url}")
            
            # Step 2: Isi username dari Config
            logging.info("📝 Filling login form...")
            username_from_config = Config.USERNAME
            logging.info(f"   👤 Username from Config: {username_from_config}")
            
            # Find username field
            username_input = None
            selectors = [
                (By.ID, 'username'),
                (By.NAME, 'username'),
                (By.XPATH, "//input[@type='text']"),
            ]
            
            for by_type, selector in selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"   ✅ Username field found")
                    break
                except:
                    continue
            
            if not username_input:
                raise Exception("Username field tidak ditemukan!")
            
            username_input.clear()
            username_input.send_keys(username_from_config)
            logging.info(f"   ✅ Username: {username_from_config}")
            time.sleep(1)
            
            # Find password field
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            password_input.clear()
            password_input.send_keys(Config.PASSWORD)
            logging.info("   ✅ Password filled")
            time.sleep(1)
            
            # Step 3: Tekan Enter (lebih reliable daripada cari button)
            logging.info("🔘 Pressing Enter to login...")
            password_input.send_keys(Keys.RETURN)
            logging.info("✅ Enter pressed!")
            
            # Step 4: Wait for redirect
            logging.info("⏳ Waiting for redirect to dashboard...")
            time.sleep(3)  # Reduced from 6s to 3s
            
            current_url = self.driver.current_url
            logging.info(f"📍 After login: {current_url}")
            
            if 'dashboard' in current_url or 'seruti' in current_url:
                logging.info("=" * 70)
                logging.info("✅ LOGIN SUCCESS!")
                logging.info("=" * 70)
                return True
            else:
                logging.warning(f"⚠️ Unexpected URL: {current_url}")
                return True
            
        except Exception as e:
            logging.error(f"❌ Login failed: {str(e)}")
            self._take_screenshot("login_error")
            raise Exception(f"Login gagal: {str(e)}")
            
            if not url:
                raise Exception("Target URL tidak ditemukan")
            
            logging.info("=" * 70)
            logging.info("🔐 SERUTI LOGIN FLOW")
            logging.info("=" * 70)
            
            # Step 1: Buka halaman login Seruti (JANGAN ISI FORM!)
            logging.info(f"📂 Step 1: Opening Seruti login page...")
            logging.info(f"   URL: {url}")
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(3)
            
            current_url = self.driver.current_url
            logging.info(f"📍 Page loaded: {current_url}")
            
            # Step 2: Klik button "Login SSO" TANPA ISI FORM APAPUN!
            logging.info("🔘 Step 2: Looking for 'Login SSO' button...")
            logging.info("   ⚠️ TIDAK mengisi username/password di halaman ini!")
            logging.info("   ⚠️ LANGSUNG klik 'Login SSO'!")
            
            try:
                # Method 1: By text and class
                login_sso_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH, 
                        "//button[contains(@class, 'btn-outline-light') and (contains(text(), 'Login SSO') or contains(text(), 'SSO'))]"
                    ))
                )
                logging.info("   ✅ Found 'Login SSO' button")
            except:
                # Method 2: Just by class
                try:
                    login_sso_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 
                            "button.btn.btn-outline-light"
                        ))
                    )
                    logging.info("   ✅ Found button by class 'btn-outline-light'")
                except:
                    raise Exception("❌ Button 'Login SSO' tidak ditemukan!")
            
            logging.info("�️ Clicking 'Login SSO' button...")
            login_sso_button.click()
            logging.info("✅ Button clicked!")
            
            # Step 3: Wait for redirect to SSO
            logging.info("⏳ Step 3: Waiting for redirect to SSO BPS...")
            time.sleep(4)
            
            current_url = self.driver.current_url
            logging.info(f"📍 Redirected to: {current_url}")
            
            if 'sso.bps.go.id' not in current_url:
                logging.warning(f"⚠️ Not on SSO page yet: {current_url}")
                time.sleep(3)
                current_url = self.driver.current_url
                logging.info(f"📍 Now at: {current_url}")
            
            # Step 4: BARU isi form SSO (Username & Password)
            logging.info("📝 Step 4: Filling SSO login form...")
            logging.info("   🔍 Finding username field...")
            
            # Try multiple username selectors
            username_input = None
            username_selectors = [
                (By.ID, 'username'),
                (By.ID, 'user'),
                (By.NAME, 'username'),
                (By.XPATH, "//input[@type='text']"),
            ]
            
            for by_type, selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"   ✅ Found username: {by_type}='{selector}'")
                    break
                except:
                    continue
            
            if not username_input:
                raise Exception("❌ Username field tidak ditemukan!")
            
            username_input.clear()
            username_input.send_keys(self.username)
            logging.info(f"   ✅ Username filled: {self.username}")
            time.sleep(1)
            
            # Find password field
            logging.info("   🔍 Finding password field...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            logging.info("   ✅ Password filled")
            time.sleep(1)
            
            # Step 5: Klik button login dengan class="btn btn-primary btn-block btn-lg" dan name="login"
            logging.info("🔘 Step 5: Looking for SSO login button...")
            
            login_button = None
            try:
                # Method 1: By name="login"
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[@name='login']"
                    ))
                )
                logging.info("   ✅ Found by name='login'")
            except:
                # Method 2: By classes
                try:
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            "button.btn.btn-primary.btn-block.btn-lg"
                        ))
                    )
                    logging.info("   ✅ Found by classes")
                except:
                    # Method 3: Any submit button
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//button[@type='submit']"
                        ))
                    )
                    logging.info("   ✅ Found submit button")
            
            logging.info("🖱️ Clicking login button...")
            login_button.click()
            logging.info("✅ Login clicked!")
            
            # Step 6: Wait for redirect to dashboard
            logging.info("⏳ Step 6: Waiting for redirect to dashboard...")
            time.sleep(5)
            
            current_url = self.driver.current_url
            logging.info(f"� After login: {current_url}")
            
            if 'dashboard' in current_url or 'seruti' in current_url:
                logging.info("=" * 70)
                logging.info("✅ LOGIN SUCCESSFUL!")
                logging.info("=" * 70)
                return True
            else:
                logging.warning(f"⚠️ Unexpected URL: {current_url}")
                self._take_screenshot("after_login_url")
                return True
            
        except Exception as e:
            logging.error(f"❌ Login failed: {str(e)}")
            self._take_screenshot("login_seruti_error")
            raise Exception(f"Login gagal: {str(e)}")
    
    def login(self, target_url=None, username_field='username', password_field='password', submit_button='//button[@type="submit"]'):
        """
        Login ke website target (fallback method - gunakan login_seruti() untuk Seruti BPS)
        
        Args:
            target_url: URL halaman login
            username_field: ID atau name dari input username
            password_field: ID atau name dari input password
            submit_button: XPath dari tombol submit
        """
        try:
            url = target_url or Config.TARGET_URL
            
            if not url:
                raise Exception("Target URL tidak ditemukan")
            
            logging.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for redirect or page load
            time.sleep(3)
            
            # Check if redirected to SSO
            current_url = self.driver.current_url
            logging.info(f"Current URL after navigation: {current_url}")
            
            # Handle SSO BPS redirect
            if 'sso.bps.go.id' in current_url:
                logging.info("Detected SSO BPS redirect, handling SSO login...")
                return self._handle_sso_bps_login()
            
            # Standard login flow (if not redirected to SSO)
            # Find and fill username
            logging.info("Filling username")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, username_field))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            
            # Find and fill password
            logging.info("Filling password")
            password_input = self.driver.find_element(By.NAME, password_field)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Click submit button
            logging.info("Clicking submit button")
            submit = self.driver.find_element(By.XPATH, submit_button)
            submit.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            logging.info("Login successful")
            return True
            
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            raise Exception(f"Login gagal: {str(e)}")
    
    def _handle_sso_bps_login(self):
        """
        Handle login khusus untuk SSO BPS (https://sso.bps.go.id)
        SSO BPS biasanya menggunakan field dan struktur yang spesifik
        """
        try:
            logging.info("Processing SSO BPS login form...")
            
            # Wait for SSO page to fully load
            time.sleep(2)
            
            # Try multiple possible field selectors for SSO BPS
            # SSO might use 'username', 'user', 'email', or 'userId'
            username_selectors = [
                (By.ID, 'username'),
                (By.ID, 'user'),
                (By.ID, 'email'),
                (By.NAME, 'username'),
                (By.NAME, 'user'),
                (By.NAME, 'email'),
                (By.CSS_SELECTOR, 'input[type="text"]'),
                (By.CSS_SELECTOR, 'input[type="email"]'),
            ]
            
            username_input = None
            for by_type, selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"Found username field using {by_type}='{selector}'")
                    break
                except:
                    continue
            
            if not username_input:
                raise Exception("Username field tidak ditemukan di SSO BPS")
            
            # Fill username
            logging.info("Filling SSO username")
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Try multiple possible password field selectors
            password_selectors = [
                (By.ID, 'password'),
                (By.ID, 'pass'),
                (By.NAME, 'password'),
                (By.NAME, 'pass'),
                (By.CSS_SELECTOR, 'input[type="password"]'),
            ]
            
            password_input = None
            for by_type, selector in password_selectors:
                try:
                    password_input = self.driver.find_element(by_type, selector)
                    logging.info(f"Found password field using {by_type}='{selector}'")
                    break
                except:
                    continue
            
            if not password_input:
                raise Exception("Password field tidak ditemukan di SSO BPS")
            
            # Fill password
            logging.info("Filling SSO password")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Try to find and click submit button
            submit_selectors = [
                (By.XPATH, '//button[@type="submit"]'),
                (By.XPATH, '//input[@type="submit"]'),
                (By.XPATH, '//button[contains(text(), "Login")]'),
                (By.XPATH, '//button[contains(text(), "Masuk")]'),
                (By.XPATH, '//button[contains(text(), "Sign")]'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
                (By.ID, 'submit'),
                (By.ID, 'login'),
            ]
            
            submit_button = None
            for by_type, selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(by_type, selector)
                    logging.info(f"Found submit button using {by_type}='{selector}'")
                    break
                except:
                    continue
            
            if not submit_button:
                # Try pressing Enter as fallback
                logging.info("Submit button not found, trying Enter key")
                password_input.send_keys('\n')
            else:
                logging.info("Clicking SSO submit button")
                submit_button.click()
            
            # Wait for SSO to redirect back to original site
            logging.info("Waiting for SSO redirect...")
            time.sleep(5)
            
            # Check if still on SSO page (might indicate login failure)
            current_url = self.driver.current_url
            if 'sso.bps.go.id' in current_url:
                # Take screenshot for debugging
                self._take_screenshot('sso_still_on_page')
                logging.warning("Still on SSO page after login attempt")
            else:
                logging.info(f"SSO redirect successful to: {current_url}")
            
            logging.info("SSO BPS login completed")
            return True
            
        except Exception as e:
            logging.error(f"SSO BPS login failed: {str(e)}")
            self._take_screenshot('sso_login_error')
            raise Exception(f"SSO BPS login gagal: {str(e)}")
    
    def navigate_to_progres(self):
        """
        Navigate ke halaman Progres setelah login
        URL: https://olah.web.bps.go.id/seruti/progres#/
        """
        try:
            logging.info("📊 Navigating to Progres page...")
            
            # Option 1: Direct URL navigation
            progres_url = "https://olah.web.bps.go.id/seruti/progres#/"
            self.driver.get(progres_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            logging.info(f"📍 Current URL: {current_url}")
            
            if 'progres' in current_url:
                logging.info("✅ Successfully navigated to Progres page")
                return True
            else:
                # Option 2: Try clicking menu if available
                logging.info("🔍 Trying to find Progres menu link...")
                try:
                    progres_link = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//a[contains(@href, 'progres') or contains(text(), 'Progres')]"
                        ))
                    )
                    progres_link.click()
                    time.sleep(3)
                    logging.info("✅ Clicked Progres menu link")
                    return True
                except:
                    logging.warning("⚠️ Could not find Progres menu link, but may already be on correct page")
                    return True
        
        except Exception as e:
            logging.error(f"❌ Failed to navigate to Progres: {str(e)}")
            self._take_screenshot("navigate_progres_error")
            raise Exception(f"Gagal ke halaman Progres: {str(e)}")
    
    def get_current_triwulan(self):
        """
        Determine triwulan based on current date
        Returns: 'Triwulan I', 'Triwulan II', 'Triwulan III', or 'Triwulan IV'
        """
        from datetime import datetime
        
        current_month = datetime.now().month
        
        if 1 <= current_month <= 3:
            return "Triwulan I"
        elif 4 <= current_month <= 6:
            return "Triwulan II"
        elif 7 <= current_month <= 9:
            return "Triwulan III"
        else:  # 10-12
            return "Triwulan IV"
    
    def process_progres_page(self, override_triwulan=None):
        """
        Process halaman Progres:
        1. Ambil info kondisi data (tanggal update terakhir)
        2. Pilih tabel: "Progres Entri per Kab/Kota"
        3. Pilih triwulan sesuai tanggal hari ini (atau override untuk testing)
        4. Klik Tampilkan
        5. Klik Export
        
        Args:
            override_triwulan: Optional string untuk override triwulan (contoh: "Triwulan III")
                              Berguna untuk testing saat triwulan saat ini belum tersedia
                              Jika None, akan auto-detect based on current date
        """
        try:
            logging.info("=" * 70)
            logging.info("📋 Processing Progres Page")
            logging.info("=" * 70)
            
            # Step 1: Get kondisi data (tanggal update terakhir)
            try:
                kondisi_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ml-2"))
                )
                kondisi_text = kondisi_element.text
                logging.info(f"📅 {kondisi_text}")
                
                # Extract date if possible
                import re
                date_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', kondisi_text)
                if date_match:
                    last_update = date_match.group(0)
                    logging.info(f"⏰ Last Update: {last_update}")
            except Exception as e:
                logging.warning(f"⚠️ Could not get kondisi data: {str(e)}")
            
            time.sleep(2)
            
            # Step 2: Select Tabel - "Progres Entri per Kab/Kota"
            logging.info("📊 Selecting table: Progres Entri per Kab/Kota")
            try:
                # Find the form-control select for Tabel
                tabel_select = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "select.form-control.form-control-sm"
                    ))
                )
                
                # Use Select class for dropdown
                from selenium.webdriver.support.ui import Select
                select_tabel = Select(tabel_select)
                
                # Try to select by visible text
                try:
                    select_tabel.select_by_visible_text("Progres Entri per Kab/Kota")
                    logging.info("✅ Selected: Progres Entri per Kab/Kota")
                except:
                    # Try partial match
                    for option in select_tabel.options:
                        if "Progres Entri" in option.text and "Kab/Kota" in option.text:
                            select_tabel.select_by_visible_text(option.text)
                            logging.info(f"✅ Selected: {option.text}")
                            break
                
                time.sleep(1)
            except Exception as e:
                logging.error(f"❌ Failed to select tabel: {str(e)}")
                self._take_screenshot('tabel_select_error')
                raise
            
            # Step 3: Select Triwulan based on current date or override
            if override_triwulan:
                current_triwulan = override_triwulan
                logging.info(f"📅 [TESTING MODE] Using override triwulan: {current_triwulan}")
            else:
                current_triwulan = self.get_current_triwulan()
                logging.info(f"📅 Auto-detected triwulan: {current_triwulan}")
            
            try:
                # Find all select elements (there might be multiple)
                all_selects = self.driver.find_elements(By.CSS_SELECTOR, "select.form-control.form-control-sm")
                
                triwulan_selected = False
                for select_elem in all_selects:
                    try:
                        select_obj = Select(select_elem)
                        # Check if this select has triwulan options
                        options_text = [opt.text for opt in select_obj.options]
                        
                        if any("Triwulan" in opt for opt in options_text):
                            # This is the triwulan selector
                            select_obj.select_by_visible_text(current_triwulan)
                            logging.info(f"✅ Selected: {current_triwulan}")
                            triwulan_selected = True
                            break
                    except:
                        continue
                
                if not triwulan_selected:
                    logging.warning("⚠️ Could not find triwulan selector")
                
                time.sleep(1)
            except Exception as e:
                logging.error(f"❌ Failed to select triwulan: {str(e)}")
                self._take_screenshot('triwulan_select_error')
            
            # Step 4: Click Tampilkan button
            logging.info("🔘 Clicking Tampilkan button")
            try:
                tampilkan_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "button.btn.btn-sm.btn-primary"
                    ))
                )
                tampilkan_button.click()
                logging.info("✅ Clicked Tampilkan button")
                time.sleep(1.5)  # Wait for data to load (reduced from 3s)
            except Exception as e:
                logging.error(f"❌ Failed to click Tampilkan: {str(e)}")
                self._take_screenshot('tampilkan_button_error')
                raise
            
            # Step 5: Click Export button
            logging.info("📥 Clicking Export button")
            try:
                export_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(text(), 'Export') or contains(@class, 'export')]"
                    ))
                )
                export_button.click()
                logging.info("✅ Clicked Export button")
                time.sleep(2)  # Wait for download to start (reduced from 5s)
                
                # Wait for download to complete
                self._wait_for_download()
                
            except Exception as e:
                logging.error(f"❌ Failed to click Export: {str(e)}")
                self._take_screenshot('export_button_error')
                raise
            
            logging.info("=" * 70)
            logging.info("✅ Progres page processing completed")
            logging.info("=" * 70)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error processing Progres page: {str(e)}")
            self._take_screenshot('progres_process_error')
            raise
    
    def _wait_for_download(self, timeout=30):
        """
        Wait for download to complete (optimized)
        """
        logging.info("⏳ Waiting for download to complete...")
        
        download_path = Config.DOWNLOAD_PATH
        if not os.path.isabs(download_path):
            download_path = os.path.join(os.getcwd(), download_path)
        
        # Get initial files
        initial_files = set(os.listdir(download_path)) if os.path.exists(download_path) else set()
        
        start_time = time.time()
        check_interval = 0.5  # Check every 0.5s instead of 1s
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            
            if not os.path.exists(download_path):
                continue
            
            current_files = set(os.listdir(download_path))
            new_files = current_files - initial_files
            
            # Check if there are no .crdownload or .tmp files (download in progress)
            in_progress = any(f.endswith(('.crdownload', '.tmp', '.part')) for f in current_files)
            
            if new_files and not in_progress:
                downloaded_file = list(new_files)[0]
                logging.info(f"✅ Download completed: {downloaded_file}")
                return downloaded_file
        
        logging.warning(f"⚠️ Download timeout after {timeout}s")
        return None
    
    def download_file(self, download_url=None, download_button_xpath=None):
        """
        Download file dari website
        
        Args:
            download_url: URL halaman download (optional)
            download_button_xpath: XPath tombol download
        """
        try:
            # Navigate to download page if URL provided
            if download_url:
                logging.info(f"Navigating to download page: {download_url}")
                self.driver.get(download_url)
                time.sleep(2)
            
            # Click download button if XPath provided
            if download_button_xpath:
                logging.info("Clicking download button")
                download_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, download_button_xpath))
                )
                download_btn.click()
            
            # Wait for download to complete
            logging.info("Waiting for download to complete")
            time.sleep(5)
            
            # Check if file was downloaded
            downloaded_files = self._get_downloaded_files()
            
            if downloaded_files:
                logging.info(f"File downloaded successfully: {downloaded_files[-1]}")
                return {
                    'success': True,
                    'file': downloaded_files[-1],
                    'path': os.path.join(self.download_path, downloaded_files[-1])
                }
            else:
                logging.warning("No new files detected in download folder")
                return {
                    'success': False,
                    'message': 'Download mungkin gagal atau belum selesai'
                }
                
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            raise Exception(f"Download gagal: {str(e)}")
    
    def _get_downloaded_files(self):
        """Get list of files in download directory"""
        try:
            files = []
            for filename in os.listdir(self.download_path):
                filepath = os.path.join(self.download_path, filename)
                if os.path.isfile(filepath):
                    files.append(filename)
            return sorted(files, key=lambda x: os.path.getmtime(os.path.join(self.download_path, x)))
        except Exception as e:
            logging.error(f"Error getting downloaded files: {str(e)}")
            return []
    
    def navigate_to(self, url):
        """Navigate to specific URL"""
        try:
            logging.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(2)
            return True
        except Exception as e:
            logging.error(f"Navigation failed: {str(e)}")
            raise Exception(f"Navigasi gagal: {str(e)}")
    
    def _take_screenshot(self, name='screenshot'):
        """Take screenshot of current page (internal method)"""
        try:
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(Config.LOG_PATH, filename)
            self.driver.save_screenshot(filepath)
            logging.info(f"📸 Screenshot saved: {filepath}")
            return filename
            
        except Exception as e:
            logging.error(f"Screenshot failed: {str(e)}")
            return None
    
    def take_screenshot(self, filename=None):
        """Take screenshot of current page (public method for backward compatibility)"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = os.path.join(Config.LOG_PATH, filename)
            self.driver.save_screenshot(filepath)
            logging.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Screenshot failed: {str(e)}")
            return None
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed")
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")
    
    def run_full_crawl(self, target_url=None, download_url=None, username_field='username', 
                       password_field='password', submit_button='//button[@type="submit"]',
                       download_button_xpath=None):
        """
        Menjalankan full crawl: setup -> login -> navigate to progres -> download -> close
        
        Returns:
            dict: Status dan informasi hasil crawl
        """
        result = {
            'success': False,
            'message': '',
            'file': None,
            'screenshots': []
        }
        
        try:
            # Setup browser
            logging.info("=" * 70)
            logging.info("🚀 STARTING SERUTI CRAWL")
            logging.info("=" * 70)
            
            self.setup_driver()
            result['message'] = 'Browser initialized'
            
            # Login dengan flow Seruti spesifik
            logging.info("Step 1: Login to Seruti...")
            self.login_seruti(target_url=target_url)
            result['message'] = 'Login successful'
            
            # Wait for dashboard to load
            time.sleep(3)
            
            # Navigate to Progres page
            logging.info("Step 2: Navigate to Progres page...")
            self.navigate_to_progres()
            result['message'] = 'Navigated to Progres page'
            
            # Take screenshot of Progres page
            screenshot = self._take_screenshot('progres_page')
            if screenshot:
                result['screenshots'].append(screenshot)
            
            # Process Progres page: select table, triwulan, and export
            logging.info("Step 3: Processing Progres page (select & export)...")
            self.process_progres_page(override_triwulan=None)
            
            # Get the downloaded file
            downloaded_files = self._get_downloaded_files()
            if downloaded_files:
                latest_file = downloaded_files[-1]  # Get most recent file
                result['file'] = latest_file
                result['message'] = f'Crawl completed successfully. File: {latest_file}'
                result['success'] = True
            else:
                result['message'] = 'Export completed but no file found'
                result['success'] = True  # Still success, maybe download started
            
            logging.info("=" * 70)
            logging.info(f"✅ CRAWL RESULT: {result['message']}")
            logging.info("=" * 70)
            
            return result
            
        except Exception as e:
            error_msg = f"Crawl failed: {str(e)}"
            logging.error(f"❌ {error_msg}")
            
            # Take error screenshot
            screenshot = self._take_screenshot('error')
            if screenshot:
                result['screenshots'].append(screenshot)
            
            result['success'] = False
            result['message'] = error_msg
            
            return result
            
        finally:
            # Always close browser
            if not self.headless:
                # Keep browser open for a moment in non-headless mode
                logging.info("Keeping browser open for 3 seconds...")
                time.sleep(3)
            
            self.close()
