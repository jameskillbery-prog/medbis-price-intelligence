from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class DaylongScraper(EcommerceSearchScraper):
    """Scraper for Daylong search results."""

    name = "Daylong"
    base_url = "https://www.daylong.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

