-- GramAI phase 1. Run against gramai_db using MySQL 8.0.
-- Keep the original backup. DDL implicitly commits in MySQL.
-- This migration is additive and repeatable; no legacy rows are deleted,
-- copied into published knowledge, or automatically marked verified.
USE gramai_db;

CREATE TABLE IF NOT EXISTS government_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    official_host VARCHAR(255) NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scheme_imports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_id INT NULL,
    legacy_scheme_id INT NULL,
    source_url TEXT NULL,
    payload JSON NOT NULL,
    status ENUM('pending','rejected','reviewed') NOT NULL DEFAULT 'pending',
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES government_sources(id),
    UNIQUE KEY uq_legacy_import (legacy_scheme_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scheme_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    scheme_key VARCHAR(150) NOT NULL,
    version_no INT NOT NULL,
    import_id BIGINT NULL,
    source_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    jurisdiction VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    exclusions TEXT NOT NULL,
    required_documents TEXT NOT NULL,
    benefits TEXT NOT NULL,
    application_process TEXT NOT NULL,
    keywords TEXT,
    source_url TEXT NOT NULL,
    status ENUM('draft','published','superseded','withdrawn') NOT NULL DEFAULT 'draft',
    scheme_status ENUM('unknown','active','closed','suspended') NOT NULL DEFAULT 'unknown',
    verified_by INT NULL,
    verified_at DATETIME NULL,
    review_due_at DATETIME NULL,
    effective_from DATE NULL,
    effective_until DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_key VARCHAR(150) GENERATED ALWAYS AS
        (CASE WHEN status='published' THEN scheme_key ELSE NULL END) STORED,
    UNIQUE KEY uq_scheme_revision (scheme_key, version_no),
    UNIQUE KEY uq_current_publication (published_key),
    FOREIGN KEY (import_id) REFERENCES scheme_imports(id),
    FOREIGN KEY (source_id) REFERENCES government_sources(id),
    FOREIGN KEY (verified_by) REFERENCES admin_users(id),
    CHECK (version_no > 0),
    CHECK (effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from),
    CHECK (status <> 'published' OR
        (verified_by IS NOT NULL AND verified_at IS NOT NULL AND
         review_due_at IS NOT NULL AND review_due_at > verified_at AND
         scheme_status='active'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scheme_evidence (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    version_id BIGINT NOT NULL,
    source_id INT NOT NULL,
    field_name ENUM('description','eligibility','exclusions','required_documents','benefits','application_process') NOT NULL,
    evidence_url TEXT NOT NULL,
    evidence_excerpt TEXT NOT NULL,
    checked_at DATETIME NOT NULL,
    FOREIGN KEY (version_id) REFERENCES scheme_versions(id),
    FOREIGN KEY (source_id) REFERENCES government_sources(id),
    KEY ix_evidence_field (version_id, field_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scheme_aliases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    version_id BIGINT NOT NULL,
    alias_text VARCHAR(255) NOT NULL,
    language_code VARCHAR(12) NOT NULL,
    UNIQUE KEY uq_version_alias (version_id, alias_text, language_code),
    FOREIGN KEY (version_id) REFERENCES scheme_versions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Snapshot existing records for review. Existing tables and original timestamps remain intact.
INSERT INTO scheme_imports (legacy_scheme_id, source_url, payload)
SELECT s.id, s.source_url, JSON_OBJECT(
    'name', s.name, 'category', s.category, 'description', s.description,
    'eligibility', s.eligibility, 'required_documents', s.required_documents,
    'benefits', s.benefits, 'application_process', s.application_process,
    'keywords', s.keywords, 'source_name', s.source_name,
    'legacy_last_verified_date', s.last_verified_date, 'legacy_last_sync_date', s.last_sync_date)
FROM imported_schemes s
WHERE NOT EXISTS (SELECT 1 FROM scheme_imports i WHERE i.legacy_scheme_id=s.id);

-- Reopen legacy reviews for every unverified record without changing old decisions.
INSERT INTO pending_reviews (imported_scheme_id, issue_reason, status)
SELECT s.id, 'Legacy information: official evidence and full verification required.', 'Pending Review'
FROM imported_schemes s
JOIN scheme_imports i ON i.legacy_scheme_id=s.id AND i.status='pending'
WHERE NOT EXISTS (SELECT 1 FROM pending_reviews p
                  WHERE p.imported_scheme_id=s.id AND p.status='Pending Review');

-- Only the publication layer is readable by the citizen answer repository.
-- Evidence completeness is a structural gate, not proof that claims are true.
CREATE OR REPLACE SQL SECURITY INVOKER VIEW verified_scheme_answers AS
SELECT v.id, v.name, v.category, v.description,
       CONCAT(v.eligibility, '\n', v.exclusions) AS eligibility,
       v.required_documents, v.benefits, v.application_process,
       v.keywords, g.name AS source_name, v.source_url,
       v.verified_at AS last_verified_date
FROM scheme_versions v
JOIN government_sources g ON g.id=v.source_id AND g.enabled=TRUE
WHERE v.status='published' AND v.scheme_status='active'
  AND v.verified_by IS NOT NULL AND v.verified_at <= NOW()
  AND v.review_due_at > NOW()
  AND (v.effective_from IS NULL OR v.effective_from <= CURRENT_DATE)
  AND (v.effective_until IS NULL OR v.effective_until >= CURRENT_DATE)
  AND LENGTH(TRIM(v.name))>0 AND LENGTH(TRIM(v.category))>0
  AND LENGTH(TRIM(v.jurisdiction))>0
  AND LENGTH(TRIM(v.description))>0 AND LENGTH(TRIM(v.eligibility))>0
  AND LENGTH(TRIM(v.exclusions))>0 AND LENGTH(TRIM(v.required_documents))>0
  AND LENGTH(TRIM(v.benefits))>0 AND LENGTH(TRIM(v.application_process))>0
  AND LOWER(LEFT(v.source_url,8))='https://' AND LOWER(SUBSTRING_INDEX(SUBSTRING(v.source_url,9),'/',1))=LOWER(g.official_host)
  AND (SELECT COUNT(DISTINCT e.field_name) FROM scheme_evidence e
       JOIN government_sources es ON es.id=e.source_id AND es.enabled=TRUE
       WHERE e.version_id=v.id AND LENGTH(TRIM(e.evidence_excerpt))>0
       AND e.checked_at <= v.verified_at
       AND LOWER(LEFT(e.evidence_url,8))='https://' AND LOWER(SUBSTRING_INDEX(SUBSTRING(e.evidence_url,9),'/',1))=LOWER(es.official_host))=6;

-- Expected on the supplied dump: 13 pending imports and 0 published answers.
SELECT COUNT(*) AS legacy_schemes FROM imported_schemes;
SELECT COUNT(*) AS pending_imports FROM scheme_imports WHERE status='pending';
SELECT COUNT(*) AS available_verified_schemes FROM verified_scheme_answers;
