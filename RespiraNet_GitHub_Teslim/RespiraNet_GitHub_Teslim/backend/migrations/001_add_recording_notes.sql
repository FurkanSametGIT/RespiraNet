-- Adapt the existing week-2 PostgreSQL design for week-5 recording notes CRUD.
-- Apply AFTER db/schema.sql. Safe to run twice.
ALTER TABLE recordings ADD COLUMN IF NOT EXISTS notes TEXT NOT NULL DEFAULT '';
