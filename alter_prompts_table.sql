-- SQL script to add mode column to prompts table
ALTER TABLE prompts 
ADD COLUMN IF NOT EXISTS mode VARCHAR(20) DEFAULT 'chat';

-- Run this SQL script against your database
-- Example with PostgreSQL: 
-- psql -U your_username -d your_database_name -f alter_prompts_table.sql
-- 
-- Example with SQLite:
-- sqlite3 your_database.sqlite < alter_prompts_table.sql 