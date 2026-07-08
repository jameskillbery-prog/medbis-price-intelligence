from medbis_price_intelligence.scrapers.medical_world import MedicalWorldScraper
from medbis_price_intelligence.scrapers.medisave import MedisaveScraper


def test_medisave_search_url_encodes_query() -> None:
    scraper = MedisaveScraper(context=None)  # type: ignore[arg-type]

    assert scraper.build_search_url("gauze swabs") == "https://www.medisave.co.uk/search?q=gauze+swabs"


def test_medical_world_search_url_encodes_query() -> None:
    scraper = MedicalWorldScraper(context=None)  # type: ignore[arg-type]

    assert (
        scraper.build_search_url("gauze swabs")
        == "https://www.medical-world.co.uk/search?search=gauze+swabs"
    )

