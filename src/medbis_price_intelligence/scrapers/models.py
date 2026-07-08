from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ScraperQuery:
    """Search input for a competitor scraper."""

    search_term: str
    brand: str | None = None
    pack_size: str | None = None
    quantity: str | None = None
    strength: str | None = None


@dataclass(frozen=True)
class ScraperResult:
    """Normalised competitor product result."""

    product_name: str
    brand: str | None
    price: Decimal | None
    stock: str | None
    url: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

