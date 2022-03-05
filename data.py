import config.db
import sqlite3
from config.logger import logger
from typing import Optional
import sqlalchemy as sql

def init() -> None:
    """
    Connects to SQLite database and creates tables if they don't exist
    """
    conn = sqlite3.connect(config.db.db_file_path)
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS Acronyms (acronym VARCHAR(255) PRIMARY KEY, \
        definition VARCHAR(255) NOT NULL)')
    logger.info("SQLite initialized")


def connect() -> sqlite3.Connection:
    """
    Connects to SQLite database and returns the connection
    """
    return sqlite3.connect(config.db.db_file_path)


class Acronyms:
    @staticmethod
    def set(acronym: str, definition: str) -> str | None:
        """
        Updates/inserts acronym=definition and returns the old acronym or None.
        """
        conn = connect()
        cur = conn.cursor()
        old_acronym = Acronyms.get(acronym)
        if old_acronym is not None:
            cur.execute(
                'UPDATE Acronyms SET definition = ? WHERE acronym = ?',
                [definition, acronym])
        else:
            cur.execute('INSERT INTO Acronyms VALUES (?, ?)',
                        [acronym, definition])
        conn.commit()
        return old_acronym

    @staticmethod
    def get(acronym: str) -> str | None:
        """
        Gets the definition of an acronym. Returns None if it doesn't exist.
        """
        cur = connect().cursor()
        row = cur.execute(
            'SELECT definition FROM Acronyms WHERE acronym = ?',
            [acronym]).fetchone()
        if row is None:
            return None
        return row[0]


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

    def create_user(self, acronym: str) -> Optional[str]:
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


class Users(Base):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True)
    username = sql.Column(sql.String(255), nullable=False)
    funas_realizadas = sql.Column(sql.Integer())
    funas_recibidas = sql.Column(sql.Integer())

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.username!r}"
