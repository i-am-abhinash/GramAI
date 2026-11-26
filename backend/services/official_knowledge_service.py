"""Import curated draft bundles and require an active admin's explicit review."""
import json
from pathlib import Path
from urllib.parse import urlparse
from backend.database.mysql_connection import db

FIELDS = ("description", "eligibility", "exclusions", "required_documents", "benefits", "application_process")
BUNDLE = Path(__file__).resolve().parents[1] / "knowledge" / "official_drafts.json"


class OfficialKnowledgeService:
    @staticmethod
    def _admin(cursor, user_id):
        if not user_id:
            raise ValueError("Sign in as an administrator first.")
        cursor.execute("SELECT id FROM admin_users WHERE id=%s AND is_active=1", (user_id,))
        if not cursor.fetchone():
            raise ValueError("An active administrator is required.")

    @staticmethod
    def _transaction(operation):
        conn = db.connect()
        if not conn:
            raise RuntimeError("Database connection unavailable.")
        cursor = None
        try:
            conn.autocommit = False
            cursor = conn.cursor(dictionary=True)
            result = operation(cursor)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    def import_drafts(self, user_id):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        def run(c):
            self._admin(c, user_id)
            source_ids = {}
            for host, name in bundle["sources"].items():
                c.execute("INSERT INTO government_sources (name,official_host,enabled) VALUES (%s,%s,TRUE) "
                          "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (name,host))
                source_ids[host] = c.lastrowid
            def source_id(url):
                parsed = urlparse(url)
                if parsed.scheme != "https" or parsed.netloc not in source_ids:
                    raise ValueError("Unregistered source URL")
                return source_ids[parsed.netloc]
            inserted = 0
            for item in bundle["schemes"]:
                c.execute("SELECT id FROM scheme_versions WHERE scheme_key=%s AND version_no=1 FOR UPDATE", (item["key"],))
                if c.fetchone():
                    continue
                for lang in ("en","te"):
                    if not all(str(item[lang].get(f,"")).strip() for f in ("name",)+FIELDS):
                        raise ValueError("Incomplete bilingual draft")
                if set(item["evidence"]) != set(FIELDS):
                    raise ValueError("Missing field evidence")
                sid = source_id(item["source_url"])
                payload = dict(item, research_date=bundle["research_date"])
                c.execute("INSERT INTO scheme_imports (source_id,source_url,payload) VALUES (%s,%s,%s)",
                          (sid,item["source_url"],json.dumps(payload,ensure_ascii=False)))
                import_id = c.lastrowid
                c.execute(
                    "INSERT INTO scheme_versions (scheme_key,version_no,import_id,source_id,name,category,jurisdiction,"
                    "description,eligibility,exclusions,required_documents,benefits,application_process,keywords,source_url) "
                    "VALUES (%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (item["key"],import_id,sid,item["en"]["name"],item["category"],item["jurisdiction"],
                     *[item["en"][f] for f in FIELDS]," ".join(a[1] for a in item["aliases"]),item["source_url"]))
                vid = c.lastrowid
                c.execute("INSERT INTO scheme_telugu (version_id,name,description,eligibility,exclusions,required_documents,benefits,application_process) "
                          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(vid,item["te"]["name"],*[item["te"][f] for f in FIELDS]))
                for language, alias in item["aliases"]:
                    c.execute("INSERT INTO scheme_aliases (version_id,alias_text,language_code) VALUES (%s,%s,%s)",(vid,alias,language))
                for field, e in item["evidence"].items():
                    c.execute("INSERT INTO scheme_evidence (version_id,source_id,field_name,evidence_url,evidence_excerpt,checked_at) "
                              "VALUES (%s,%s,%s,%s,%s,%s)",(vid,source_id(e["url"]),field,e["url"],e["note"],bundle["research_date"]+" 00:00:00"))
                inserted += 1
            return inserted
        return self._transaction(run)

    def list_versions(self, user_id):
        def run(c):
            self._admin(c,user_id)
            c.execute("SELECT id,name,category,status,verified_at,review_due_at FROM scheme_versions ORDER BY id")
            return c.fetchall()
        return self._transaction(run)

    def details(self, user_id, version_id):
        def run(c):
            self._admin(c,user_id)
            c.execute("SELECT * FROM scheme_versions WHERE id=%s",(version_id,))
            version = c.fetchone()
            if not version:
                raise ValueError("Draft not found.")
            c.execute("SELECT * FROM scheme_telugu WHERE version_id=%s",(version_id,))
            te = c.fetchone()
            c.execute("SELECT field_name,evidence_url,evidence_excerpt,checked_at FROM scheme_evidence WHERE version_id=%s ORDER BY field_name",(version_id,))
            return version,te,c.fetchall()
        return self._transaction(run)

    def decide(self, user_id, version_id, publish, reviewed):
        if publish and not reviewed:
            raise ValueError("Confirm both languages and all official evidence before publishing.")
        def run(c):
            self._admin(c,user_id)
            c.execute("SELECT id,import_id,status FROM scheme_versions WHERE id=%s FOR UPDATE",(version_id,))
            v = c.fetchone()
            if not v or v["status"] not in ("draft","published"):
                raise ValueError("This revision is no longer available for review.")
            if publish:
                if v["status"] != "draft":
                    raise ValueError("Only draft revisions may be published.")
                c.execute("SELECT * FROM scheme_telugu WHERE version_id=%s",(version_id,))
                te = c.fetchone()
                if not te or not all(str(te.get(f) or "").strip() for f in ("name",)+FIELDS):
                    raise ValueError("The Telugu version is incomplete.")
                # The administrator explicitly attests to checking the source and both texts now.
                c.execute("UPDATE scheme_evidence SET checked_at=NOW() WHERE version_id=%s",(version_id,))
                c.execute("UPDATE scheme_versions SET status='published',scheme_status='active',verified_by=%s,verified_at=NOW(),"
                          "review_due_at=DATE_ADD(NOW(),INTERVAL 30 DAY) WHERE id=%s",(user_id,version_id))
                c.execute("SELECT id FROM verified_scheme_answers WHERE id=%s",(version_id,))
                if not c.fetchone():
                    raise ValueError("Publication blocked by evidence, source or validity requirements.")
                status = "published"
            else:
                c.execute("UPDATE scheme_versions SET status='withdrawn' WHERE id=%s",(version_id,))
                status = "withdrawn"
            c.execute("INSERT INTO scheme_review_decisions (version_id,reviewer_id,decision) VALUES (%s,%s,%s)",(version_id,user_id,status))
            if v["import_id"]:
                c.execute("UPDATE scheme_imports SET status=%s WHERE id=%s",("reviewed" if publish else "rejected",v["import_id"]))
            return status
        return self._transaction(run)
