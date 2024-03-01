CREATE DATABASE autospatialqc;
USE autospatialqc;

-- Create users table
CREATE TABLE users (
    internal_id     INT AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    first_name      VARCHAR(255) NOT NULL,
    last_name       VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX (email)
);

-- Create permissions table
CREATE TABLE permissions (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    permission_name     VARCHAR(255) NOT NULL,
    description         VARCHAR(255)
);

-- Populate permissions
INSERT INTO permissions (permission_name, description) VALUES
    ('get_sample', 'Allows getting a sample'),
    ('post_sample', 'Allows posting a sample'),
    ('delete_sample', 'Allows deleting a sample'),
    ('change_password', 'Allows a user to change their own password');

-- Create user to permissions table
CREATE TABLE user_permissions (
    user_id         INT NOT NULL,
    permission_id   INT NOT NULL,
    PRIMARY KEY (user_id, permission_id),
    FOREIGN KEY (user_id)       REFERENCES users(internal_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- Create samples table
CREATE TABLE samples (
    id INT AUTO_INCREMENT PRIMARY KEY,

    assay                   VARCHAR(255) NOT NULL,
    tissue                  VARCHAR(255) NOT NULL,
    UNIQUE (assay, tissue),
    INDEX assay_tissue (assay, tissue),

    area                    DOUBLE NOT NULL,
    assigned_transcripts    DOUBLE NOT NULL,
    cell_count              INT    NOT NULL,
    cell_over25_count       INT    NOT NULL,
    complexity              DOUBLE NOT NULL,
    false_discovery_rate    DOUBLE NOT NULL,
    median_counts           DOUBLE NOT NULL,
    median_genes            DOUBLE NOT NULL,
    reference_correlation   DOUBLE NOT NULL,
    sparsity                DOUBLE NOT NULL,
    volume                  DOUBLE NOT NULL,
    x_transcript_count      INT    NOT NULL,
    y_transcript_count      INT    NOT NULL,

    -- these two *might* be inferrable, but none of the equations that pop
    -- into mind immediately yield precise results
    transcripts_per_area    DOUBLE NOT NULL,
    transcripts_per_feature DOUBLE NOT NULL,

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
