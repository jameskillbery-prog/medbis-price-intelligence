from multiprocessing import freeze_support

from medbis_price_intelligence.app import run


def main() -> None:
    """Frozen application entry point."""
    freeze_support()
    run()


if __name__ == "__main__":
    main()

