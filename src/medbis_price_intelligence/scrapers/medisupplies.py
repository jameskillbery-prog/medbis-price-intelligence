from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class MediSuppliesScraper(EcommerceSearchScraper):
    """Scraper for MediSupplies search results."""

    name = "MediSupplies"
    base_url = "https://www.medisupplies.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

