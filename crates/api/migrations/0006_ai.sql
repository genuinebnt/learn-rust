-- The AI assistant (docs/AI.md).

-- Embeddings for retrieval: one row per item and embedding model. Vectors are plain float4 arrays, searched in memory
-- (a few thousand rows); content_hash says when an item changed and needs embedding again.
CREATE TABLE ai_embeddings (
    kind          text        NOT NULL CHECK (kind IN ('problem', 'attempt')),
    ref_id        text        NOT NULL,
    model         text        NOT NULL,
    content_hash  text        NOT NULL,
    embedding     real[]      NOT NULL,
    updated_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (kind, ref_id, model)
);

-- The assistant chat, kept per problem. `sources` lists what an answer was grounded in.
CREATE TABLE ai_messages (
    id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_id  text        NOT NULL,
    role        text        NOT NULL CHECK (role IN ('user', 'assistant')),
    content     text        NOT NULL,
    action      text,
    sources     jsonb       NOT NULL DEFAULT '[]',
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ai_messages_by_problem ON ai_messages (problem_id, id);

-- Generated reports, e.g. 'patterns'; the newest one per kind.
CREATE TABLE ai_reports (
    kind        text        PRIMARY KEY,
    content     jsonb       NOT NULL,
    model       text        NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);
