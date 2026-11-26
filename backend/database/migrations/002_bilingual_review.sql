-- Phase 2A: run once after 001. No legacy data is deleted.
USE gramai_db;
CREATE TABLE IF NOT EXISTS scheme_telugu (
    version_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    exclusions TEXT NOT NULL,
    required_documents TEXT NOT NULL,
    benefits TEXT NOT NULL,
    application_process TEXT NOT NULL,
    FOREIGN KEY (version_id) REFERENCES scheme_versions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS scheme_review_decisions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    version_id BIGINT NOT NULL,
    reviewer_id INT NOT NULL,
    decision ENUM('published','withdrawn') NOT NULL,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES scheme_versions(id),
    FOREIGN KEY (reviewer_id) REFERENCES admin_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
