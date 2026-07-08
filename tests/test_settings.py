from medbis_price_intelligence.settings import RuntimeSettings


def test_runtime_settings_defaults_are_production_safe() -> None:
    settings = RuntimeSettings()

    assert settings.cache_days == 14
    assert settings.scraper_concurrency == 4
    assert settings.products_per_run == 3

