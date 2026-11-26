from backend.database.mysql_connection import db
from mysql.connector import Error


class SchemeRepository:
    """Publication-only, bilingual retrieval; no fallback to legacy rows."""
    def _fetch(self, where="", params=()):
        conn = db.connect()
        if not conn:
            return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT v.*, t.name AS te_name, t.description AS te_description, "
                "CONCAT(t.eligibility,'\\n',t.exclusions) AS te_eligibility, "
                "t.required_documents AS te_required_documents, t.benefits AS te_benefits, "
                "t.application_process AS te_application_process "
                "FROM verified_scheme_answers v JOIN scheme_telugu t ON t.version_id=v.id "
                "WHERE LENGTH(TRIM(t.name))>0 AND LENGTH(TRIM(t.description))>0 "
                "AND LENGTH(TRIM(t.eligibility))>0 AND LENGTH(TRIM(t.exclusions))>0 "
                "AND LENGTH(TRIM(t.required_documents))>0 AND LENGTH(TRIM(t.benefits))>0 "
                "AND LENGTH(TRIM(t.application_process))>0 " + where, params)
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute("SELECT alias_text FROM scheme_aliases WHERE version_id=%s",(row["id"],))
                row["aliases"] = [a["alias_text"] for a in cursor.fetchall()]
            return rows
        except Error as exc:
            print(f"Verified knowledge unavailable: {exc}")
            return []
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    def get_schemes_by_category(self, category):
        return self._fetch("AND LOWER(v.category) = %s", (category.lower(),))

    def get_all_schemes(self):
        return self._fetch()
