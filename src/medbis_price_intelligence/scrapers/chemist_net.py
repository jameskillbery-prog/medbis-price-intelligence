from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class ChemistNetScraper(EcommerceSearchScraper):
    """Scraper for Chemist.net search results."""

    name = "Chemist.net"
    base_url = "https://www.chemist.net"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?search={quote_plus(search_term)}"

