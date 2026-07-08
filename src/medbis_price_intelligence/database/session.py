from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from medbis_price_intelligence.database.base import Base
from medbis_price_intelligence.database import models  # noqa: F401


class Database:
    """Owns the SQLAlchemy engine and session factory."""

    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, future=True)
        self._session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )

    def create_schema(self) -> None:
        """Create database tables if they do not already exist."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Open a transaction-scoped session."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

