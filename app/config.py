import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Target Website Configuration
    TARGET_URL = os.getenv('TARGET_URL', '')
    DOWNLOAD_URL = os.getenv('DOWNLOAD_URL', '')
    
    # Login Credentials
    # Note: Use SERUTI_USERNAME instead of USERNAME to avoid conflict with Windows env var
    USERNAME = os.getenv('SERUTI_USERNAME') or os.getenv('USERNAME', '')
    PASSWORD = os.getenv('SERUTI_PASSWORD') or os.getenv('PASSWORD', '')
    
    # Download Settings
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOWNLOAD_PATH = os.path.join(BASE_DIR, os.getenv('DOWNLOAD_PATH', 'downloads'))
    LOG_PATH = os.path.join(BASE_DIR, 'logs')
    MAX_DOWNLOAD_WAIT = int(os.getenv('MAX_DOWNLOAD_WAIT', 30))
    
    # Browser Settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False') == 'True'
    BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', 30))
    
    # Ensure directories exist
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)
