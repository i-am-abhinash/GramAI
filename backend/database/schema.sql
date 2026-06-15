CREATE DATABASE IF NOT EXISTS gramai_db;
USE gramai_db;

CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS government_schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    eligibility TEXT,
    required_documents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faq_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    frequency INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS unanswered_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text TEXT NOT NULL,
    frequency INT DEFAULT 1,
    last_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('pending', 'answered') DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text TEXT,
    response_text TEXT,
    is_successful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some mock data for FAQ and Schemes
INSERT IGNORE INTO faq_data (question, answer) VALUES
('How do I apply for the old-age pension?', 'Aadhaar card, income certificate, and age proof are required for the old-age pension.'),
('What documents are needed for a new ration card?', 'You need address proof, identity proof, and a passport-size photograph.'),
('When will the next farmer subsidy be released?', 'The next farmer subsidy (Rythu Bandhu) is scheduled to be released next month.');
