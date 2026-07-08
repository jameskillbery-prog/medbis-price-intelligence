from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class ESuppliesMedicalScraper(EcommerceSearchScraper):
    """Scraper for eSupplies Medical search results."""

    name = "eSupplies Medical"
    base_url = "https://www.esuppliesmedical.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

