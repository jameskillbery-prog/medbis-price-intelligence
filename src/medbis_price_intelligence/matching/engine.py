from rapidfuzz import fuzz

from medbis_price_intelligence.database.models import Product
from medbis_price_intelligence.matching.models import MatchCandidate, MatchDecision, MatchScore


class MatchingEngine:
    """Scores MedBIS products against competitor candidates using weighted fuzzy matching."""

    AUTO_MATCH_THRESHOLD = 92.0
    REVIEW_THRESHOLD = 80.0

    WEIGHTS: dict[str, float] = {
        "brand": 0.20,
        "product_name": 0.45,
        "pack_size": 0.15,
        "quantity": 0.10,
        "strength": 0.10,
    }

    def score(self, product: Product, candidate: MatchCandidate) -> MatchScore:
        """Return a weighted score and decision for a single candidate."""
        brand_score = self._field_score(product.brand, candidate.brand)
        name_score = self._field_score(product.product_name, candidate.product_name)
        pack_score = self._field_score(product.pack_size, candidate.pack_size)
        quantity_score = self._field_score(product.quantity, candidate.quantity)
        strength_score = self._field_score(product.strength, candidate.strength)

        weighted_score = (
            brand_score * self.WEIGHTS["brand"]
            + name_score * self.WEIGHTS["product_name"]
            + pack_score * self.WEIGHTS["pack_size"]
            + quantity_score * self.WEIGHTS["quantity"]
            + strength_score * self.WEIGHTS["strength"]
        )

        return MatchScore(
            score=round(weighted_score, 2),
            decision=self._decision(weighted_score),
            brand_score=brand_score,
            name_score=name_score,
            pack_score=pack_score,
            quantity_score=quantity_score,
            strength_score=strength_score,
        )

    def best_match(
        self,
        product: Product,
        candidates: list[MatchCandidate],
    ) -> tuple[MatchCandidate, MatchScore] | None:
        """Return the highest scoring candidate unless every candidate is ignored."""
        scored = [(candidate, self.score(product, candidate)) for candidate in candidates]
        if not scored:
            return None

        candidate, score = max(scored, key=lambda item: item[1].score)
        if score.decision == MatchDecision.IGNORE:
            return None
        return candidate, score

    @classmethod
    def _decision(cls, score: float) -> MatchDecision:
        if score >= cls.AUTO_MATCH_THRESHOLD:
            return MatchDecision.AUTO_MATCH
        if score >= cls.REVIEW_THRESHOLD:
            return MatchDecision.REVIEW
        return MatchDecision.IGNORE

    @staticmethod
    def _field_score(left: str | None, right: str | None) -> float:
        left_value = MatchingEngine._normalise(left)
        right_value = MatchingEngine._normalise(right)

        if not left_value and not right_value:
            return 100.0
        if not left_value or not right_value:
            return 0.0
        return float(fuzz.token_set_ratio(left_value, right_value))

    @staticmethod
    def _normalise(value: str | None) -> str:
        if value is None:
            return ""
        return " ".join(value.lower().strip().split())

