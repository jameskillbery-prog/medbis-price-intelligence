from dataclasses import dataclass
from enum import StrEnum


class MatchDecision(StrEnum):
    """Decision bands for competitor product matches."""

    AUTO_MATCH = "auto_match"
    REVIEW = "review"
    IGNORE = "ignore"


@dataclass(frozen=True)
class MatchCandidate:
    """Competitor product details used by the matching engine."""

    product_name: str
    brand: str | None = None
    pack_size: str | None = None
    quantity: str | None = None
    strength: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class MatchScore:
    """Weighted match score and decision."""

    score: float
    decision: MatchDecision
    brand_score: float
    name_score: float
    pack_score: float
    quantity_score: float
    strength_score: float

