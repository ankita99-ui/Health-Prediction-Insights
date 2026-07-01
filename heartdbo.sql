SELECT * FROM [HealthDB].[dbo].[patients];
-- Active patients only:
-- SELECT * FROM [HealthDB].[dbo].[patients] WHERE is_deleted = 0;
-- Deleted patients (still in DB):
-- SELECT * FROM [HealthDB].[dbo].[patients] WHERE is_deleted = 1;

-- ⚠️ DELETE ALL DATA + restart IDs from 1 (cannot undo)

DELETE FROM dbo.patient_history;
DELETE FROM dbo.patients;
DBCC CHECKIDENT ('dbo.patient_history', RESEED, 0);
DBCC CHECKIDENT ('dbo.patients', RESEED, 0);
