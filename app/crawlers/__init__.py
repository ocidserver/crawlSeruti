"""
Crawlers Package
"""
from app.crawlers.seruti_crawler import SerutiCrawler
from app.crawlers.susenas_crawler import SusenasCrawler

__all__ = ['SerutiCrawler', 'SusenasCrawler']

# Crawler registry
CRAWLERS = {
    'seruti': SerutiCrawler,
    'susenas': SusenasCrawler
}

def get_crawler(crawler_type):
    """
    Get crawler class by type
    
    Args:
        crawler_type: 'seruti' atau 'susenas'
        
    Returns:
        Crawler class
    """
    return CRAWLERS.get(crawler_type.lower())
