from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Runtime paths and configurable defaults."""

    app_name: str
    data_dir: Path
    database_url: str
    log_file: Path
    stale_product_days: int = 14

    @classmethod
    def default(cls) -> "AppConfig":
        local_app_data = os.getenv("LOCALAPPDATA")
        root = Path(local_app_data) / "MedBIS Price Intelligence" if local_app_data else Path.cwd()
        data_dir = root / "data"
        logs_dir = root / "logs"
        data_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        db_path = data_dir / "medbis_price_intelligence.sqlite3"
        return cls(
            app_name="MedBIS Price Intelligence",
            data_dir=data_dir,
            database_url=f"sqlite:///{db_path.as_posix()}",
            log_file=logs_dir / "app.log",
        )
