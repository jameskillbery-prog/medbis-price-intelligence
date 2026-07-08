import asyncio
import json
import logging
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from playwright.async_api import async_playwright
from playwright.async_api import Error as PlaywrightError
from sqlalchemy.orm import Session

from medbis_price_intelligence.scrapers.base import BaseScraper
from medbis_price_intelligence.scrapers.cache import ScrapeCacheRepository
from medbis_price_intelligence.scrapers.models import ScraperQuery, ScraperResult

ScraperFactory = Callable[..., BaseScraper]
logger = logging.getLogger(__name__)


class ScraperRunner:
    """Runs multiple Playwright scrapers concurrently."""

    def __init__(
        self,
        scraper_factories: list[ScraperFactory],
        session: Session | None = None,
        cache_days: int = 14,
        concurrency_limit: int = 4,
        browser_channels: tuple[str | None, ...] = ("msedge", "chrome", None),
    ) -> None:
        self.scraper_factories = scraper_factories
        self.session = session
        self.cache_days = cache_days
        self.concurrency_limit = concurrency_limit
        self.browser_channels = browser_channels

    async def run(self, query: ScraperQuery) -> dict[str, list[ScraperResult]]:
        """Run all configured scrapers and return results grouped by competitor."""
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        async with async_playwright() as playwright:
            browser = await self._launch_browser(playwright)
            try:
                context = await browser.new_context()
                scrapers = [factory(context) for factory in self.scraper_factories]
                tasks = [self._run_one(scraper, query, semaphore) for scraper in scrapers]
                scraper_results = await asyncio.gather(*tasks)
                return dict(scraper_results)
            finally:
                await browser.close()

    async def _launch_browser(self, playwright: object) -> object:
        """Launch an installed browser without downloading Playwright Chromium."""
        last_error: Exception | None = None
        for channel in self.browser_channels:
            try:
                launch_options = {"headless": True}
                if channel is not None:
                    launch_options["channel"] = channel
                return await playwright.chromium.launch(**launch_options)
            except PlaywrightError as exc:
                last_error = exc
        raise RuntimeError(
            "Could not launch Microsoft Edge or Chrome. Install one of them before running scrapers."
        ) from last_error

    async def _run_one(
        self,
        scraper: BaseScraper,
        query: ScraperQuery,
        semaphore: asyncio.Semaphore,
    ) -> tuple[str, list[ScraperResult]]:
        async with semaphore:
            try:
                cached = self._get_cached(scraper.name, query.search_term)
                if cached is not None:
                    return scraper.name, cached

                results = await scraper.search(query)
                self._set_cached(scraper.name, query.search_term, results)
                return scraper.name, results
            except Exception:
                logger.exception("Scraper failed: %s", scraper.name)
                return scraper.name, []

    def _get_cached(self, competitor_name: str, search_term: str) -> list[ScraperResult] | None:
        if self.session is None:
            return None
        payload = ScrapeCacheRepository(self.session).get_fresh(
            competitor_name,
            search_term,
            self.cache_days,
        )
        if payload is None:
            return None
        values = json.loads(payload)
        return [self._deserialise_result(value) for value in values]

    def _set_cached(
        self,
        competitor_name: str,
        search_term: str,
        results: list[ScraperResult],
    ) -> None:
        if self.session is None:
            return
        payload = json.dumps([self._serialise_result(result) for result in results])
        ScrapeCacheRepository(self.session).set(competitor_name, search_term, payload)

    @staticmethod
    def _serialise_result(result: ScraperResult) -> dict[str, object]:
        return {
            "product_name": result.product_name,
            "brand": result.brand,
            "price": str(result.price) if result.price is not None else None,
            "stock": result.stock,
            "url": result.url,
            "confidence": result.confidence,
            "timestamp": result.timestamp.isoformat(),
        }

    @staticmethod
    def _deserialise_result(value: dict[str, object]) -> ScraperResult:
        price = value.get("price")
        timestamp = value.get("timestamp")
        return ScraperResult(
            product_name=str(value["product_name"]),
            brand=str(value["brand"]) if value.get("brand") is not None else None,
            price=Decimal(str(price)) if price is not None else None,
            stock=str(value["stock"]) if value.get("stock") is not None else None,
            url=str(value["url"]),
            confidence=float(value["confidence"]),
            timestamp=datetime.fromisoformat(str(timestamp)) if timestamp else datetime.utcnow(),
        )
