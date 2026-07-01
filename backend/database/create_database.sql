/*
  Run this in SSMS (or it runs automatically - the app also creates the
  table on startup via SQLAlchemy). Kept here so the schema is documented
  and reviewable.
*/

-- 1. Create the database if it does not exist
IF DB_ID('HealthDB') IS NULL
    CREATE DATABASE HealthDB;
GO

USE HealthDB;
GO

-- 2. Patients table: one row per patient record
IF OBJECT_ID('dbo.patients', 'U') IS NULL
CREATE TABLE dbo.patients (
    id            INT IDENTITY(1,1) PRIMARY KEY,      -- auto-increment ID
    full_name     NVARCHAR(100) NOT NULL,
    date_of_birth DATE          NOT NULL,
    email         NVARCHAR(254) NOT NULL UNIQUE,      -- no duplicate patients
    glucose       FLOAT         NOT NULL,             -- mg/dL (fasting)
    haemoglobin   FLOAT         NOT NULL,             -- g/dL
    cholesterol   FLOAT         NOT NULL,             -- mg/dL (total)
    remarks       NVARCHAR(500) NOT NULL DEFAULT '',  -- filled by the AI model
    created_at    DATETIME      NOT NULL DEFAULT GETUTCDATE(),
    updated_at    DATETIME      NOT NULL DEFAULT GETUTCDATE(),
    is_deleted    BIT           NOT NULL DEFAULT 0,   -- soft delete flag
    deleted_at    DATETIME      NULL                  -- when removed from the app
);
GO

-- Useful queries for checking data in SSMS:
-- SELECT * FROM dbo.patients ORDER BY id DESC;
-- SELECT * FROM dbo.patients WHERE is_deleted = 0;           -- active in app
-- SELECT * FROM dbo.patients WHERE is_deleted = 1;           -- deleted (still in DB)
-- SELECT COUNT(*) AS total_patients FROM dbo.patients;
-- SELECT * FROM dbo.patients WHERE remarks LIKE '%High Risk%';
