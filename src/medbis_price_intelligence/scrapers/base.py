from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from urllib.parse import quote_plus

from playwright.async_api import BrowserContext

from medbis_price_intelligence.scrapers.models import ScraperQuery, ScraperResult


class BaseScraper(ABC):
    """Base class for every competitor website scraper."""

    name: str
    base_url: str

    def __init__(self, context: BrowserContext) -> None:
        self.context = context

    @abstractmethod
    async def search(self, query: ScraperQuery) -> list[ScraperResult]:
        """Search a competitor website and return normalised product results."""

    def build_search_url(self, search_term: str) -> str:
        """Build a generic search URL. Override when a website needs custom behaviour."""
        return f"{self.base_url}/search?q={quote_plus(search_term)}"

    @staticmethod
    def clean_text(value: str | None) -> str | None:
        """Normalise scraped text."""
        if value is None:
            return None
        text = " ".join(value.strip().split())
        return text or None

    @staticmethod
    def parse_price(value: str | None) -> Decimal | None:
        """Parse common UK price text into Decimal."""
        if value is None:
            return None
        cleaned = value.replace("\u00a3", "").replace("GBP", "").replace(",", "").strip()
        cleaned = "".join(character for character in cleaned if character.isdigit() or character == ".")
        if not cleaned:
            return None
        try:
            return Decimal(cleaned).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None
