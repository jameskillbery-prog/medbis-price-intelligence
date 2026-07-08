from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class MedicalWorldScraper(EcommerceSearchScraper):
    """Scraper for Medical World search results."""

    name = "Medical World"
    base_url = "https://www.medical-world.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?search={quote_plus(search_term)}"

