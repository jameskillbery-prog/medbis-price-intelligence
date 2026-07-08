from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import Competitor, Match, PriceHistory, Product


@dataclass(frozen=True)
class ProductPriceInsight:
    """Calculated market position for a MedBIS product."""

    sku: str | None
    product_name: str
    brand: str | None
    medbis_price: Decimal | None
    lowest_competitor_price: Decimal | None
    average_competitor_price: Decimal | None
    competitor_count: int
    market_position: str
    suggested_price: Decimal | None
    margin_opportunity: Decimal | None


class PriceIntelligenceService:
    """Builds commercial pricing insights from product and competitor history."""

    UNDER_MARKET_THRESHOLD = Decimal("0.90")
    ABOVE_MARKET_THRESHOLD = Decimal("1.03")

    def __init__(self, session: Session) -> None:
        self.session = session

    def calculate(self) -> list[ProductPriceInsight]:
        """Return pricing insight rows for every imported product."""
        products = list(self.session.scalars(select(Product).order_by(Product.product_name)).all())
        return [self._insight_for_product(product) for product in products]

    def _insight_for_product(self, product: Product) -> ProductPriceInsight:
        competitor_prices = self._latest_competitor_prices(product.id)
        lowest = min(competitor_prices) if competitor_prices else None
        average = self._average(competitor_prices)
        position = self._market_position(product.selling_price, lowest, average)
        suggested_price = self._suggested_price(product.selling_price, average, position)
        opportunity = self._margin_opportunity(product.selling_price, suggested_price)

        return ProductPriceInsight(
            sku=product.sku,
            product_name=product.product_name,
            brand=product.brand,
            medbis_price=product.selling_price,
            lowest_competitor_price=lowest,
            average_competitor_price=average,
            competitor_count=len(competitor_prices),
            market_position=position,
            suggested_price=suggested_price,
            margin_opportunity=opportunity,
        )

    def _latest_competitor_prices(self, product_id: int) -> list[Decimal]:
        rows = self.session.execute(
            select(PriceHistory.price)
            .join(Competitor, PriceHistory.competitor_id == Competitor.id)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.captured_at.desc())
        ).all()
        return [row[0] for row in rows if row[0] is not None]

    @staticmethod
    def _average(values: list[Decimal]) -> Decimal | None:
        if not values:
            return None
        return (sum(values) / Decimal(len(values))).quantize(Decimal("0.01"))

    def _market_position(
        self,
        medbis_price: Decimal | None,
        lowest: Decimal | None,
        average: Decimal | None,
    ) -> str:
        if medbis_price is None:
            return "missing_medbis_price"
        if lowest is None or average is None:
            return "no_competitor_match"
        if medbis_price < average * self.UNDER_MARKET_THRESHOLD:
            return "significantly_below_market"
        if medbis_price > average * self.ABOVE_MARKET_THRESHOLD:
            return "above_market_average"
        if medbis_price <= lowest:
            return "medbis_cheapest"
        if medbis_price > lowest:
            return "above_competitor"
        return "within_market_range"

    def _suggested_price(
        self,
        medbis_price: Decimal | None,
        average: Decimal | None,
        position: str,
    ) -> Decimal | None:
        if medbis_price is None or average is None:
            return None
        if position in {"medbis_cheapest", "significantly_below_market"}:
            target = average * Decimal("0.97")
            if target > medbis_price:
                return target.quantize(Decimal("0.01"))
        return None

    @staticmethod
    def _margin_opportunity(
        medbis_price: Decimal | None,
        suggested_price: Decimal | None,
    ) -> Decimal | None:
        if medbis_price is None or suggested_price is None:
            return None
        return (suggested_price - medbis_price).quantize(Decimal("0.01"))


class MatchDataService:
    """Read model for report worksheets."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def competitor_price_rows(self) -> list[dict[str, object]]:
        rows = self.session.execute(
            select(Product, Competitor, Match, PriceHistory)
            .join(Match, Product.id == Match.product_id)
            .join(Competitor, Match.competitor_id == Competitor.id)
            .outerjoin(
                PriceHistory,
                (PriceHistory.product_id == Product.id)
                & (PriceHistory.competitor_id == Competitor.id),
            )
            .order_by(Product.product_name, Competitor.name)
        ).all()
        return [
            {
                "SKU": product.sku,
                "Product": product.product_name,
                "Brand": product.brand,
                "MedBIS Price": product.selling_price,
                "Competitor": competitor.name,
                "Competitor Product": match.competitor_product_name,
                "Competitor Price": price.price if price else None,
                "Stock": price.stock if price else None,
                "Confidence": match.confidence_score,
                "Status": match.status,
                "URL": match.competitor_url,
            }
            for product, competitor, match, price in rows
        ]

    def historical_price_rows(self) -> list[dict[str, object]]:
        rows = self.session.execute(
            select(Product, Competitor, PriceHistory)
            .outerjoin(Competitor, PriceHistory.competitor_id == Competitor.id)
            .join(Product, PriceHistory.product_id == Product.id)
            .order_by(PriceHistory.captured_at.desc())
        ).all()
        return [
            {
                "SKU": product.sku,
                "Product": product.product_name,
                "Competitor": competitor.name if competitor else "MedBIS",
                "Price": price.price,
                "Stock": price.stock,
                "Captured At": price.captured_at,
            }
            for product, competitor, price in rows
        ]
