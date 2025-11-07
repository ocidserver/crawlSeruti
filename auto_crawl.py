"""
Auto Crawl Script - Standalone
Jalankan crawler secara otomatis tanpa Flask

Usage:
    python auto_crawl.py              # Run once
    python auto_crawl.py --loop       # Run continuous loop
    python auto_crawl.py --interval 30 # Run every 30 minutes
"""
from app.crawler import SerutiCrawler
from app.config import Config
import logging
import argparse
from datetime import datetime
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_crawl.log'),
        logging.StreamHandler()
    ]
)

def run_crawl():
    """Execute single crawl"""
    logging.info("=" * 70)
    logging.info("🤖 AUTO CRAWL STARTED")
    logging.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"🎯 Target: {Config.TARGET_URL}")
    logging.info(f"👤 Username: {Config.USERNAME}")
    logging.info("=" * 70)
    
    try:
        # Initialize crawler
        crawler = SerutiCrawler(
            username=Config.USERNAME,
            password=Config.PASSWORD,
            headless=True  # Always headless for automation
        )
        
        # Run full crawl process
        result = crawler.run_full_crawl(
            target_url=Config.TARGET_URL,
            download_url=Config.DOWNLOAD_URL
        )
        
        # Log result
        if result['success']:
            logging.info(f"✅ CRAWL SUCCESS: {result['message']}")
            if result.get('file'):
                logging.info(f"📄 File downloaded: {result['file']}")
                logging.info(f"💾 Saved to: downloads/{result['file']}")
        else:
            logging.warning(f"⚠️ CRAWL FAILED: {result['message']}")
        
        return result
        
    except Exception as e:
        logging.error(f"❌ CRAWL ERROR: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}
    
    finally:
        logging.info("=" * 70)
        logging.info("🏁 AUTO CRAWL FINISHED")
        logging.info("=" * 70)

def run_continuous(interval_minutes=30):
    """Run crawl in continuous loop"""
    logging.info(f"🔄 Starting continuous mode (every {interval_minutes} minutes)")
    logging.info("Press Ctrl+C to stop")
    
    try:
        while True:
            run_crawl()
            
            # Wait for next run
            next_run = datetime.now().timestamp() + (interval_minutes * 60)
            next_run_time = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
            
            logging.info(f"⏳ Sleeping {interval_minutes} minutes...")
            logging.info(f"⏰ Next run: {next_run_time}")
            logging.info("-" * 70)
            
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        logging.info("\n🛑 Stopped by user (Ctrl+C)")
        logging.info("👋 Goodbye!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Auto Crawl Script for Seruti BPS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_crawl.py                    # Run once
  python auto_crawl.py --loop             # Run every 30 minutes (default)
  python auto_crawl.py --loop --interval 60  # Run every 60 minutes
  python auto_crawl.py --test             # Test mode (show config only)
        """
    )
    
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Run in continuous loop mode'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Interval in minutes for loop mode (default: 30)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - show configuration only'
    )
    
    args = parser.parse_args()
    
    # Test mode - show config
    if args.test:
        print("\n" + "=" * 70)
        print("📋 CURRENT CONFIGURATION")
        print("=" * 70)
        print(f"Target URL    : {Config.TARGET_URL}")
        print(f"Download URL  : {Config.DOWNLOAD_URL}")
        print(f"Username      : {Config.USERNAME}")
        print(f"Password      : {'*' * len(Config.PASSWORD)}")
        print(f"Headless Mode : True (forced for automation)")
        print(f"Download Path : {Config.DOWNLOAD_PATH}")
        print(f"Timeout       : {Config.BROWSER_TIMEOUT}s")
        print("=" * 70)
        print("\n✅ Configuration loaded successfully!")
        print("\n💡 Tips:")
        print("   - Make sure DOWNLOAD_URL is configured in .env")
        print("   - Test with: python auto_crawl.py (run once)")
        print("   - Auto mode: python auto_crawl.py --loop")
        print("\n")
        return
    
    # Run mode
    if args.loop:
        run_continuous(interval_minutes=args.interval)
    else:
        run_crawl()

if __name__ == "__main__":
    main()
