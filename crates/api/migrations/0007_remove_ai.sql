-- The AI assistant was removed on 2026-10-07. 0006_ai.sql stays (migrations are append-only); this drops what it made,
-- and the API key the assistant's settings stored.
DROP TABLE IF EXISTS ai_embeddings;
DROP TABLE IF EXISTS ai_messages;
DROP TABLE IF EXISTS ai_reports;
DELETE FROM settings WHERE key = 'ai';
