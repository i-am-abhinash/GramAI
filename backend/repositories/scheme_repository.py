from backend.database.mysql_connection import db
from mysql.connector import Error


class SchemeRepository:
    """Citizen retrieval must never fall back to legacy imported_schemes."""

    def _fetch(self, where="", params=()):
        conn = db.connect()
        if not conn:
            return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM verified_scheme_answers " + where, params)
            return cursor.fetchall()
        except Error as exc:
            # Missing migration, unavailable DB or view: fail closed.
            print(f"Verified knowledge unavailable: {exc}")
            return []
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    def get_schemes_by_category(self, category):
        return self._fetch("WHERE LOWER(category) = %s", (category.lower(),))

    def get_all_schemes(self):
        return self._fetch()
