import json
from decimal import Decimal
from typing import Any

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from medbis_price_intelligence.scrapers.base import BaseScraper
from medbis_price_intelligence.scrapers.models import ScraperQuery, ScraperResult


class EcommerceSearchScraper(BaseScraper):
    """Shared scraper for ecommerce search result pages."""

    product_selectors: tuple[str, ...] = (
        "[data-product-id]",
        ".product-item",
        ".product",
        ".grid__item",
        ".product-card",
        "li.product",
        "article",
    )
    name_selectors: tuple[str, ...] = (
        "[itemprop='name']",
        ".product-title",
        ".product-item-name",
        ".product-name",
        ".card-title",
        "h2",
        "h3",
        "a[title]",
    )
    price_selectors: tuple[str, ...] = (
        "[itemprop='price']",
        ".price",
        ".price-item",
        ".product-price",
        ".woocommerce-Price-amount",
    )
    stock_selectors: tuple[str, ...] = (
        ".stock",
        ".availability",
        ".product-stock",
        "[data-stock]",
    )

    async def search(self, query: ScraperQuery) -> list[ScraperResult]:
        """Search the site and parse product cards plus JSON-LD products."""
        page = await self.context.new_page()
        try:
            await page.goto(self.build_search_url(query.search_term), wait_until="domcontentloaded")
            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except PlaywrightTimeoutError:
                pass
            results = await self._parse_json_ld(page.content)
            results.extend(await self._parse_cards(page, query))
            return self._deduplicate(results)[:10]
        finally:
            await page.close()

    async def _parse_cards(self, page: Any, query: ScraperQuery) -> list[ScraperResult]:
        cards = []
        for selector in self.product_selectors:
            cards = await page.query_selector_all(selector)
            if cards:
                break

        results: list[ScraperResult] = []
        for card in cards[:20]:
            name = await self._first_text(card, self.name_selectors)
            href = await self._first_href(card)
            price_text = await self._first_text(card, self.price_selectors)
            stock = await self._first_text(card, self.stock_selectors)
            if not name or not href:
                continue
            results.append(
                ScraperResult(
                    product_name=name,
                    brand=query.brand,
                    price=self.parse_price(price_text),
                    stock=stock,
                    url=self._absolute_url(href),
                    confidence=0.0,
                )
            )
        return results

    async def _parse_json_ld(self, content_method: Any) -> list[ScraperResult]:
        html = await content_method()
        marker = '<script type="application/ld+json">'
        results: list[ScraperResult] = []
        start = 0
        while (start := html.find(marker, start)) != -1:
            start += len(marker)
            end = html.find("</script>", start)
            if end == -1:
                break
            results.extend(self._results_from_json(html[start:end].strip()))
            start = end
        return results

    def _results_from_json(self, raw_json: str) -> list[ScraperResult]:
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            return []

        results: list[ScraperResult] = []
        for product in self._flatten_products(payload):
            name = self.clean_text(str(product.get("name", "")))
            offers = product.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            url = product.get("url") or offers.get("url")
            if not name or not url:
                continue
            results.append(
                ScraperResult(
                    product_name=name,
                    brand=self._json_brand(product.get("brand")),
                    price=self._json_price(offers.get("price") or product.get("price")),
                    stock=self.clean_text(str(offers.get("availability", ""))),
                    url=self._absolute_url(str(url)),
                    confidence=0.0,
                )
            )
        return results

    def _flatten_products(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for value in payload for item in self._flatten_products(value)]
        if not isinstance(payload, dict):
            return []
        if payload.get("@type") == "Product":
            return [payload]
        graph = payload.get("@graph")
        if isinstance(graph, list):
            return [item for value in graph for item in self._flatten_products(value)]
        return []

    async def _first_text(self, element: Any, selectors: tuple[str, ...]) -> str | None:
        for selector in selectors:
            child = await element.query_selector(selector)
            if child is None:
                continue
            text = self.clean_text(await child.inner_text())
            if text:
                return text
        text = self.clean_text(await element.inner_text())
        return text[:180] if text else None

    async def _first_href(self, element: Any) -> str | None:
        link = await element.query_selector("a[href]")
        if link is None:
            return None
        return await link.get_attribute("href")

    def _absolute_url(self, href: str) -> str:
        if href.startswith("http"):
            return href
        if href.startswith("/"):
            return f"{self.base_url}{href}"
        return f"{self.base_url}/{href}"

    @staticmethod
    def _json_brand(value: Any) -> str | None:
        if isinstance(value, dict):
            return EcommerceSearchScraper.clean_text(str(value.get("name", "")))
        if value:
            return EcommerceSearchScraper.clean_text(str(value))
        return None

    @staticmethod
    def _json_price(value: Any) -> Decimal | None:
        if value is None:
            return None
        return EcommerceSearchScraper.parse_price(str(value))

    @staticmethod
    def _deduplicate(results: list[ScraperResult]) -> list[ScraperResult]:
        seen: set[str] = set()
        unique: list[ScraperResult] = []
        for result in results:
            key = result.url.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(result)
        return unique
