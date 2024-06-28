import sqlite3

import config.db
from config.logger import logger


def init() -> None:
    """
    Connects to SQLite database and creates tables if they don't exist
    """
    conn = sqlite3.connect(config.db.db_file_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Acronyms (acronym VARCHAR(255) PRIMARY KEY, definition VARCHAR(255) NOT NULL);"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Messages (message_id INTEGER PRIMARY KEY, datetime INTEGER NOT NULL, user_id INTEGER NOT NULL, username VARCHAR(255), message TEXT NOT NULL, reply_to INTEGER);"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS AIRequests (request_id INTEGER PRIMARY KEY, datetime INTEGER NOT NULL, user_id INTEGER NOT NULL, username TEXT NOT NULL, model TEXT NOT NULL, input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL, input_price_per_m FLOAT NOT NULL, output_price_per_m FLOAT NOT NULL, cost FLOAT NOT NULL);"
    )
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
                "UPDATE Acronyms SET definition = ? WHERE acronym = ?",
                [definition, acronym],
            )
        else:
            cur.execute("INSERT INTO Acronyms VALUES (?, ?)", [acronym, definition])
        conn.commit()
        return old_acronym

    @staticmethod
    def get(acronym: str) -> str | None:
        """
        Gets the definition of an acronym. Returns None if it doesn't exist.
        """
        cur = connect().cursor()
        row = cur.execute(
            "SELECT definition FROM Acronyms WHERE acronym = ?", [acronym]
        ).fetchone()
        if row is None:
            return None
        return row[0]

    @staticmethod
    def list_all() -> list[tuple[str, str]]:
        """Lists all acronym definitions."""
        cur = connect().cursor()
        rows = cur.execute("SELECT * FROM Acronyms").fetchall()
        return rows

    @staticmethod
    def list_by_letter(let: str) -> list[tuple[str, str]]:
        """Lists all acronyms starting with a certain letter, and
        their definitions."""
        cur = connect().cursor()
        rows = cur.execute(
            f"SELECT * FROM Acronyms WHERE (acronym LIKE '{let}%')"
        ).fetchall()
        return rows


class Messages:
    @staticmethod
    def add(
        message_id: int,
        datetime: int,
        user_id: int,
        username: str,
        message: str,
        reply_to: int,
    ) -> None:
        """
        Adds a message to the database.
        """
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Messages VALUES (?, ?, ?, ?, ?, ?)",
            [message_id, datetime, user_id, username, message, reply_to],
        )
        conn.commit()

    @staticmethod
    def get(message_id: int) -> tuple[int, int, int, str, str, int] | None:
        """
        Gets a message from the database.
        """
        cur = connect().cursor()
        row = cur.execute(
            "SELECT * FROM Messages WHERE message_id = ?", [message_id]
        ).fetchone()
        return row

    @staticmethod
    def get_n(n: int, from_id: int | None = None) -> list[sqlite3.Row]:
        """
        Gets the last N messages from the database, starting from a given message_id
        """
        if 0 < n <= 1000:
            conn = connect()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            if from_id is None:
                rows = cur.execute(
                    "SELECT * FROM (SELECT * FROM Messages ORDER BY message_id DESC LIMIT ?) ORDER BY message_id ASC",
                    [n],
                ).fetchall()
            else:
                rows = cur.execute(
                    "SELECT * FROM (SELECT * FROM Messages WHERE message_id <= ? ORDER BY message_id DESC LIMIT ?) ORDER BY message_id ASC",
                    [from_id, n],
                ).fetchall()
            return [dict(row) for row in rows]


class AIRequests:
    @staticmethod
    def add(
        datetime: int,
        user_id: int,
        username: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        input_price_per_m: float,
        output_price_per_m: float,
        cost: float,
    ) -> None:
        """
        Adds an AI request to the database.
        """
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO AIRequests (datetime, user_id, username, model, input_tokens, output_tokens, input_price_per_m, output_price_per_m, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                datetime,
                user_id,
                username,
                model,
                input_tokens,
                output_tokens,
                input_price_per_m,
                output_price_per_m,
                cost,
            ],
        )
        conn.commit()

    @staticmethod
    def get(
        user_id: int = None,
        username: str = None,
        datetime_from: int = None,
        datetime_to: int = None,
    ) -> list[sqlite3.Row]:
        """
        Gets AI requests from the database.
        """
        conn = connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        query = "SELECT * FROM AIRequests"
        where = []
        params = []
        if user_id is not None:
            where.append("user_id = ?")
            params.append(user_id)
        if username is not None:
            where.append("username = ?")
        if datetime_from is not None:
            where.append("datetime >= ?")
            params.append(datetime_from)
        if datetime_to is not None:
            where.append("datetime <= ?")
            params.append(datetime_to)
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY datetime DESC"
        rows = cur.execute(query, params).fetchall()
        return rows
