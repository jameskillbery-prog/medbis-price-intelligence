from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import Match, PriceHistory, Product, Run
from medbis_price_intelligence.database.repositories import CompetitorRepository, ProductRepository
from medbis_price_intelligence.matching.engine import MatchingEngine
from medbis_price_intelligence.matching.models import MatchCandidate
from medbis_price_intelligence.scrapers.models import ScraperQuery, ScraperResult
from medbis_price_intelligence.scrapers.registry import ALL_SCRAPERS, CORE_SCRAPERS
from medbis_price_intelligence.scrapers.runner import ScraperRunner
from medbis_price_intelligence.settings import SettingsService


class PriceSearchService:
    """Runs the first live competitor searches and persists price intelligence data."""

    def __init__(
        self,
        session: Session,
        matcher: MatchingEngine | None = None,
        runner: ScraperRunner | None = None,
        all_competitors: bool = False,
    ) -> None:
        self.session = session
        settings = SettingsService(session).load()
        self.matcher = matcher or MatchingEngine()
        self.runner = runner or ScraperRunner(
            scraper_factories=ALL_SCRAPERS if all_competitors else CORE_SCRAPERS,
            session=None,
            cache_days=settings.cache_days,
            concurrency_limit=settings.scraper_concurrency if all_competitors else min(2, settings.scraper_concurrency),
        )
        self.products_per_run = settings.products_per_run

    async def run_first_products(self, limit: int | None = None) -> int:
        """Search competitors for the first imported products and save accepted matches."""
        limit = limit or self.products_per_run
        run = Run(run_type="scrape", status="running", message=f"First {limit} products")
        self.session.add(run)
        self.session.flush()

        products = ProductRepository(self.session).first_products(limit)
        if not products:
            run.status = "completed"
            run.finished_at = datetime.utcnow()
            run.message = "No products available. Import products first."
            return 0

        saved = 0
        try:
            for product in products:
                saved += await self._search_product(product)
            run.status = "completed"
            run.finished_at = datetime.utcnow()
            run.message = f"Saved {saved} competitor matches"
            return saved
        except Exception as exc:
            run.status = "failed"
            run.finished_at = datetime.utcnow()
            run.message = str(exc)
            raise

    async def _search_product(self, product: Product) -> int:
        query = ScraperQuery(
            search_term=product.product_name,
            brand=product.brand,
            pack_size=product.pack_size,
            quantity=product.quantity,
            strength=product.strength,
        )
        grouped_results = await self.runner.run(query)
        saved = 0
        for competitor_name, results in grouped_results.items():
            saved += self._persist_best_result(product, competitor_name, results)
        return saved

    def _persist_best_result(
        self,
        product: Product,
        competitor_name: str,
        results: list[ScraperResult],
    ) -> int:
        competitor = CompetitorRepository(self.session).get_by_name(competitor_name)
        if competitor is None:
            return 0

        candidates = [
            MatchCandidate(
                product_name=result.product_name,
                brand=result.brand,
                pack_size=product.pack_size,
                quantity=product.quantity,
                strength=product.strength,
                url=result.url,
            )
            for result in results
        ]
        best = self.matcher.best_match(product, candidates)
        if best is None:
            return 0

        candidate, score = best
        self.session.add(
            Match(
                product_id=product.id,
                competitor_id=competitor.id,
                competitor_product_name=candidate.product_name,
                competitor_brand=candidate.brand,
                competitor_url=candidate.url,
                confidence_score=Decimal(str(score.score)),
                status=score.decision.value,
            )
        )

        result = self._result_for_candidate(candidate, results)
        if result and result.price is not None:
            self.session.add(
                PriceHistory(
                    product_id=product.id,
                    competitor_id=competitor.id,
                    price=result.price,
                    stock=result.stock,
                )
            )
        return 1

    @staticmethod
    def _result_for_candidate(
        candidate: MatchCandidate,
        results: list[ScraperResult],
    ) -> ScraperResult | None:
        for result in results:
            if result.url == candidate.url:
                return result
        return None
