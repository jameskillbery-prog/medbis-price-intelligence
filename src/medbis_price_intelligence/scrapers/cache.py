from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import ScrapeCache


class ScrapeCacheRepository:
    """SQLite-backed cache for competitor searches."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_fresh(self, competitor_name: str, search_term: str, max_age_days: int) -> str | None:
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        return self.session.scalar(
            select(ScrapeCache.payload_json).where(
                ScrapeCache.competitor_name == competitor_name,
                ScrapeCache.search_term == search_term,
                ScrapeCache.created_at >= cutoff,
            )
        )

    def set(self, competitor_name: str, search_term: str, payload_json: str) -> None:
        cache = self.session.scalar(
            select(ScrapeCache).where(
                ScrapeCache.competitor_name == competitor_name,
                ScrapeCache.search_term == search_term,
            )
        )
        if cache is None:
            self.session.add(
                ScrapeCache(
                    competitor_name=competitor_name,
                    search_term=search_term,
                    payload_json=payload_json,
                )
            )
            return

        cache.payload_json = payload_json
        cache.created_at = datetime.utcnow()

