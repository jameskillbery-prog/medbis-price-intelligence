from urllib.parse import quote_plus

from medbis_price_intelligence.scrapers.ecommerce import EcommerceSearchScraper


class EasyMedsHealthScraper(EcommerceSearchScraper):
    """Scraper for EasyMeds Health search results."""

    name = "EasyMeds Health"
    base_url = "https://www.easymedshealth.com"

    def build_search_url(self, search_term: str) -> str:
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

