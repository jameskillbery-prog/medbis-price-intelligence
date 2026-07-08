from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import Competitor, Match, PriceHistory, Product, Run


DEFAULT_COMPETITORS: tuple[tuple[str, str], ...] = (
    ("Medical World", "https://www.medical-world.co.uk"),
    ("Medical Dressings", "https://www.medicaldressings.co.uk"),
    ("Medisave", "https://www.medisave.co.uk"),
    ("Amazon UK", "https://www.amazon.co.uk"),
    ("Algeos", "https://www.algeos.com"),
    ("Daylong", "https://www.daylong.co.uk"),
    ("MediSupplies", "https://www.medisupplies.co.uk"),
    ("Chemist.net", "https://www.chemist.net"),
    ("eSupplies Medical", "https://www.esuppliesmedical.co.uk"),
    ("Care Supply Store", "https://www.caresupplystore.co.uk"),
    ("EasyMeds Health", "https://www.easymedshealth.com"),
    ("WMS", "https://www.wms.co.uk"),
)


class ProductRepository:
    """Persistence operations for products."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_many(self, products: Iterable[Product]) -> int:
        """Insert or update products by SKU when available."""
        changed = 0
        for product in products:
            existing = self._find_existing(product)
            if existing is None:
                self.session.add(product)
            else:
                self._copy_product_values(existing, product)
            changed += 1
        return changed

    def count(self) -> int:
        return self.session.scalar(select(func.count(Product.id))) or 0

    def first_products(self, limit: int = 5) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).order_by(Product.product_name.asc()).limit(limit)
            ).all()
        )

    def search(self, term: str, limit: int = 50) -> list[Product]:
        pattern = f"%{term.strip()}%"
        return list(
            self.session.scalars(
                select(Product)
                .where(
                    Product.product_name.ilike(pattern)
                    | Product.brand.ilike(pattern)
                    | Product.sku.ilike(pattern)
                )
                .order_by(Product.product_name.asc())
                .limit(limit)
            ).all()
        )

    def recent(self, limit: int = 20) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).order_by(Product.updated_at.desc()).limit(limit)
            ).all()
        )

    def _find_existing(self, product: Product) -> Product | None:
        if product.sku:
            return self.session.scalar(select(Product).where(Product.sku == product.sku))
        if product.barcode:
            return self.session.scalar(select(Product).where(Product.barcode == product.barcode))
        return None

    @staticmethod
    def _copy_product_values(target: Product, source: Product) -> None:
        target.product_name = source.product_name
        target.brand = source.brand
        target.pack_size = source.pack_size
        target.quantity = source.quantity
        target.strength = source.strength
        target.category = source.category
        target.barcode = source.barcode
        target.cost_price = source.cost_price
        target.selling_price = source.selling_price
        target.source_file = source.source_file


class CompetitorRepository:
    """Persistence operations for competitors."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_defaults(self) -> None:
        existing_names = set(self.session.scalars(select(Competitor.name)).all())
        for name, base_url in DEFAULT_COMPETITORS:
            if name not in existing_names:
                self.session.add(Competitor(name=name, base_url=base_url))

    def count_enabled(self) -> int:
        return self.session.scalar(
            select(func.count(Competitor.id)).where(Competitor.enabled == 1)
        ) or 0

    def get_by_name(self, name: str) -> Competitor | None:
        return self.session.scalar(select(Competitor).where(Competitor.name == name))


class RunRepository:
    """Read operations for historical application runs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def count_imports(self) -> int:
        return self.session.scalar(select(func.count(Run.id)).where(Run.run_type == "import")) or 0

    def count_scrapes(self) -> int:
        return self.session.scalar(select(func.count(Run.id)).where(Run.run_type == "scrape")) or 0

    def recent(self, limit: int = 15) -> list[Run]:
        return list(
            self.session.scalars(
                select(Run).order_by(Run.started_at.desc()).limit(limit)
            ).all()
        )


class MatchRepository:
    """Read operations for competitor matches."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def count(self) -> int:
        return self.session.scalar(select(func.count(Match.id))) or 0

    def status_counts(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Match.status, func.count(Match.id)).group_by(Match.status)
        ).all()
        return {str(status): int(count) for status, count in rows}

    def recent(self, limit: int = 15) -> list[dict[str, object]]:
        rows = self.session.execute(
            select(Product, Competitor, Match, PriceHistory)
            .join(Product, Match.product_id == Product.id)
            .join(Competitor, Match.competitor_id == Competitor.id)
            .outerjoin(
                PriceHistory,
                (PriceHistory.product_id == Product.id)
                & (PriceHistory.competitor_id == Competitor.id),
            )
            .order_by(Match.created_at.desc())
            .limit(limit)
        ).all()
        return [
            {
                "product": product.product_name,
                "competitor": competitor.name,
                "price": price.price if price else None,
                "confidence": match.confidence_score,
                "status": match.status,
            }
            for product, competitor, match, price in rows
        ]
