from medbis_price_intelligence.scrapers.registry import ALL_SCRAPERS


def test_registry_contains_all_requested_competitors() -> None:
    names = {scraper.name for scraper in ALL_SCRAPERS}

    assert names == {
        "Medical World",
        "Medical Dressings",
        "Medisave",
        "Amazon UK",
        "Algeos",
        "Daylong",
        "MediSupplies",
        "Chemist.net",
        "eSupplies Medical",
        "Care Supply Store",
        "EasyMeds Health",
        "WMS",
    }

