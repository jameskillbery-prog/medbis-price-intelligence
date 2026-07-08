from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class AmazonUkScraper(EcommerceSearchScraper):
    """Scraper for Amazon UK search results."""

    name = "Amazon UK"
    base_url = "https://www.amazon.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/s?k={quote_plus(search_term)}"

