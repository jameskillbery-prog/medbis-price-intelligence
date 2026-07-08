from medbis_price_intelligence.scrapers.algeos import AlgeosScraper
from medbis_price_intelligence.scrapers.amazon_uk import AmazonUkScraper
from medbis_price_intelligence.scrapers.care_supply_store import CareSupplyStoreScraper
from medbis_price_intelligence.scrapers.chemist_net import ChemistNetScraper
from medbis_price_intelligence.scrapers.daylong import DaylongScraper
from medbis_price_intelligence.scrapers.easy_meds_health import EasyMedsHealthScraper
from medbis_price_intelligence.scrapers.esupplies_medical import ESuppliesMedicalScraper
from medbis_price_intelligence.scrapers.medical_dressings import MedicalDressingsScraper
from medbis_price_intelligence.scrapers.medical_world import MedicalWorldScraper
from medbis_price_intelligence.scrapers.medisave import MedisaveScraper
from medbis_price_intelligence.scrapers.medisupplies import MediSuppliesScraper
from medbis_price_intelligence.scrapers.runner import ScraperFactory
from medbis_price_intelligence.scrapers.wms import WmsScraper


CORE_SCRAPERS: list[ScraperFactory] = [MedisaveScraper, MedicalWorldScraper]

ALL_SCRAPERS: list[ScraperFactory] = [
    MedicalWorldScraper,
    MedicalDressingsScraper,
    MedisaveScraper,
    AmazonUkScraper,
    AlgeosScraper,
    DaylongScraper,
    MediSuppliesScraper,
    ChemistNetScraper,
    ESuppliesMedicalScraper,
    CareSupplyStoreScraper,
    EasyMedsHealthScraper,
    WmsScraper,
]

