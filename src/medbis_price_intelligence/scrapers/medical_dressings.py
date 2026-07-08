from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class MedicalDressingsScraper(EcommerceSearchScraper):
    """Scraper for Medical Dressings search results."""

    name = "Medical Dressings"
    base_url = "https://www.medicaldressings.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

