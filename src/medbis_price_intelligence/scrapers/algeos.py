from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class AlgeosScraper(EcommerceSearchScraper):
    """Scraper for Algeos search results."""

    name = "Algeos"
    base_url = "https://www.algeos.com"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?query={quote_plus(search_term)}"

