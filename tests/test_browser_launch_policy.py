from medbis_price_intelligence.scrapers.runner import ScraperRunner


def test_scraper_runner_prefers_installed_browsers() -> None:
    runner = ScraperRunner(scraper_factories=[])

    assert runner.browser_channels[:2] == ("msedge", "chrome")

