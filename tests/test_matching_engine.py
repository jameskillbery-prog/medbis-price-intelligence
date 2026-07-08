from medbis_price_intelligence.database.models import Product
from medbis_price_intelligence.matching.engine import MatchingEngine
from medbis_price_intelligence.matching.models import MatchCandidate, MatchDecision


def test_matching_engine_auto_matches_high_confidence_candidate() -> None:
    product = Product(
        sku="A1",
        product_name="Premier Sterile Gauze Swabs 10cm x 10cm",
        brand="Premier",
        pack_size="10cm x 10cm",
        quantity="Pack of 100",
        strength=None,
    )
    candidate = MatchCandidate(
        product_name="Premier Sterile Gauze Swabs 10cm x 10cm",
        brand="Premier",
        pack_size="10cm x 10cm",
        quantity="Pack of 100",
    )

    score = MatchingEngine().score(product, candidate)

    assert score.score >= 92
    assert score.decision == MatchDecision.AUTO_MATCH


def test_matching_engine_ignores_low_confidence_candidate() -> None:
    product = Product(product_name="Premier Gauze Swabs", brand="Premier")
    candidate = MatchCandidate(product_name="Disposable Nitrile Gloves", brand="Unigloves")

    score = MatchingEngine().score(product, candidate)

    assert score.score < 80
    assert score.decision == MatchDecision.IGNORE

