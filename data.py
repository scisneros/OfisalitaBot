import sqlite3
from typing import Optional

import config.db
from typing import Optional

import sqlalchemy as sql
from sqlalchemy import select
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import registry, declarative_base, Session, session

import config.db
from config.logger import logger

Base = declarative_base()


class DataBaseDriver:
    """
    Basic driver for the bot database.
    """
    _registry: registry
    _engine: Engine
    _conn: Connection
    _metadata: sql.MetaData

    def __init__(self) -> None:
        """
        Connects to SQLite database and creates tables if they don't exist
        """
        self._registry = registry()

        self._engine = sql.create_engine(f"sqlite+pysqlite:///{config.db.db_file_path}", echo=True, future=True)
        Base.metadata.create_all(self._engine)

        logger.info("SQLite initialized")

    def insert_acronym(self, acronym: str, definition: str) -> Optional[str]:
        """Inserts a new acronym into de database. If the value already exists it is replaced.

        Args:
            acronym:
                the acronym representation of a phrase.
            definition:
                the acronym definition.
        Returns:
            the old acronym if it was already present in the database (before replacing), ```None```otherwise.
        """
        with self.session as sess:
            try:
                old_acronym = sess.execute(
                    select(Acronyms).filter_by(acronym=definition.lower())).scalar_one().definition
            except NoResultFound:
                old_acronym = None
            row = Acronyms(acronym=acronym, definition=definition)
            sess.add(row)
            sess.commit()
        return old_acronym

    def get_acronym(self, acronym: str) -> Optional[str]:
        """Queries the database for a particular acronym.

        Args:
            acronym:
                the acronym to search.
        Returns:
            the acronym definition if found or `None` if it was not found.
        """
        with self.session as sess:
            try:
                acronym = sess.execute(select(Acronyms).filter_by(acronym=acronym.lower())).scalar_one()
                return acronym.definition
            except NoResultFound:
                return None

    @property
    def session(self) -> session:
        """This creates and returns a session to connect to the database.

        Use this only if necessary.
        If this is used, the session should be manually closed.

            Usage example:
            >>> db = DataBaseDriver()
            >>> with db.session as sess:
            >>>     ...
            >>>     sess.commit()
        """
        return Session(self._engine)


class Acronyms(Base):
    __tablename__ = 'acronyms'

    acronym = sql.Column(sql.String(255), primary_key=True)
    definition = sql.Column(sql.String(255), nullable=False)

    def __repr__(self):
        return f"Acronyms(acronym={self.acronym!r}, definition={self.definition!r}"
