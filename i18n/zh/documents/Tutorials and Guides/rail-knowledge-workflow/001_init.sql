-- PostgreSQL 初始化脚本（最小可用）

CREATE TABLE IF NOT EXISTS sources (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  source_type   TEXT NOT NULL,
  entry_url     TEXT NOT NULL,
  access_mode   TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'active',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
  id                BIGSERIAL PRIMARY KEY,
  source_id         TEXT NOT NULL REFERENCES sources(id),
  source_record_id  TEXT,
  doi               TEXT,
  title             TEXT NOT NULL,
  authors           JSONB NOT NULL DEFAULT '[]'::jsonb,
  abstract          TEXT,
  doc_type          TEXT NOT NULL,
  language          TEXT,
  published_at      DATE,
  source_url        TEXT NOT NULL,
  file_url          TEXT,
  quality_status    TEXT NOT NULL DEFAULT 'pending',
  collected_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_doi_unique
  ON documents ((LOWER(doi)))
  WHERE doi IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_documents_title_trgm ON documents (title);
CREATE INDEX IF NOT EXISTS idx_documents_published_at ON documents (published_at);
CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents (doc_type);

INSERT INTO sources (id, name, source_type, entry_url, access_mode, status)
VALUES ('src_crossref', 'Crossref', 'api', 'https://api.crossref.org/works', 'api', 'active')
ON CONFLICT (id) DO NOTHING;
