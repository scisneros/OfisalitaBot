import config.db
import sqlite3
from config.logger import logger


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
    @ staticmethod
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

    @ staticmethod
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

class Users:
    pass