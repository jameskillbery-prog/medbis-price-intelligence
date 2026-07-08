from decimal import Decimal

from medbis_price_intelligence.reports.intelligence import PriceIntelligenceService


def test_margin_opportunity_is_difference_between_suggested_and_current_price() -> None:
    assert PriceIntelligenceService._margin_opportunity(
        Decimal("10.00"),
        Decimal("11.25"),
    ) == Decimal("1.25")


def test_missing_competitors_are_classified_without_match() -> None:
    service = PriceIntelligenceService.__new__(PriceIntelligenceService)

    assert service._market_position(Decimal("10.00"), None, None) == "no_competitor_match"

