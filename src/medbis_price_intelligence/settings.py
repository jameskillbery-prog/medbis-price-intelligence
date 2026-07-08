from dataclasses import dataclass

from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import Setting


@dataclass(frozen=True)
class RuntimeSettings:
    """User-configurable runtime settings."""

    cache_days: int = 14
    scraper_concurrency: int = 4
    products_per_run: int = 3
    auto_match_threshold: int = 92
    review_match_threshold: int = 80


class SettingsService:
    """Loads and saves strongly-typed application settings."""

    DEFAULTS = RuntimeSettings()

    def __init__(self, session: Session) -> None:
        self.session = session

    def load(self) -> RuntimeSettings:
        values = {setting.key: setting.value for setting in self.session.query(Setting).all()}
        return RuntimeSettings(
            cache_days=self._int(values.get("cache_days"), self.DEFAULTS.cache_days),
            scraper_concurrency=self._int(
                values.get("scraper_concurrency"),
                self.DEFAULTS.scraper_concurrency,
            ),
            products_per_run=self._int(values.get("products_per_run"), self.DEFAULTS.products_per_run),
            auto_match_threshold=self._int(
                values.get("auto_match_threshold"),
                self.DEFAULTS.auto_match_threshold,
            ),
            review_match_threshold=self._int(
                values.get("review_match_threshold"),
                self.DEFAULTS.review_match_threshold,
            ),
        )

    def save(self, settings: RuntimeSettings) -> None:
        for key, value in settings.__dict__.items():
            setting = self.session.get(Setting, key)
            if setting is None:
                self.session.add(Setting(key=key, value=str(value)))
            else:
                setting.value = str(value)

    @staticmethod
    def _int(value: str | None, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

