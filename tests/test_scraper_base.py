from decimal import Decimal

from medbis_price_intelligence.scrapers.base import BaseScraper


def test_parse_price_handles_uk_currency_text() -> None:
    assert BaseScraper.parse_price("£1,234.50 inc VAT") == Decimal("1234.50")


def test_clean_text_removes_extra_spacing() -> None:
    assert BaseScraper.clean_text("  Premier   Gauze   ") == "Premier Gauze"

