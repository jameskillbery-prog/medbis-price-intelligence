from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class CareSupplyStoreScraper(EcommerceSearchScraper):
    """Scraper for Care Supply Store search results."""

    name = "Care Supply Store"
    base_url = "https://www.caresupplystore.co.uk"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

