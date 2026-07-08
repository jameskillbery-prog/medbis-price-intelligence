from medbis_price_intelligence.config import AppConfig
from medbis_price_intelligence.database.session import Database
from medbis_price_intelligence.ui.main_window import MainWindow
from medbis_price_intelligence.utils.logging import configure_logging


def run() -> None:
    """Start the desktop application."""
    config = AppConfig.default()
    configure_logging(config.log_file)

    database = Database(config.database_url)
    database.create_schema()

    app = MainWindow(config=config, database=database)
    app.mainloop()

