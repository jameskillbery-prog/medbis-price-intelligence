from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class MedisaveScraper(EcommerceSearchScraper):
    """Scraper for Medisave search results."""

    name = "Medisave"
    base_url = "https://www.medisave.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

