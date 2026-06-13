-- 1. Create database (skip if already exists)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'HealthPredictionDB')
BEGIN
    CREATE DATABASE HealthPredictionDB;
END
GO

USE HealthPredictionDB;
GO

-- 2. Create patients table
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[patients]') AND type = 'U'
)
BEGIN
    CREATE TABLE dbo.patients (
        id              INT IDENTITY(1,1) PRIMARY KEY,
        full_name       NVARCHAR(150) NOT NULL,
        date_of_birth   DATE NOT NULL,
        email           NVARCHAR(255) NOT NULL,
        glucose         FLOAT NOT NULL,
        haemoglobin     FLOAT NOT NULL,
        cholesterol     FLOAT NOT NULL,
        remarks         NVARCHAR(MAX) NULL,
        created_at      DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO
