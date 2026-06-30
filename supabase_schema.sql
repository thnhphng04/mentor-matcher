-- Run once in the Supabase SQL editor (Dashboard -> SQL).
-- Stores LLM enrichment tags so in-app enrichment persists across redeploys.

create table if not exists enrichment_tags (
    kind        text        not null,          -- 'student' | 'mentor'
    id          text        not null,          -- the row's UUID
    tags        jsonb       not null,          -- the structured enrichment record
    updated_at  timestamptz not null default now(),
    primary key (kind, id)
);

-- Raw dataset rows (original CSV data). Uploading new data in the app replaces
-- the rows here, so the dataset persists across redeploys.
create table if not exists dataset_rows (
    kind        text        not null,          -- 'student' | 'mentor'
    id          text        not null,          -- the row's ID
    data        jsonb       not null,          -- the full original CSV row
    updated_at  timestamptz not null default now(),
    primary key (kind, id)
);

-- The app uses the service-role key (server-side), which bypasses RLS, so no
-- policies are required. If you instead use the anon key, enable RLS and add
-- read/write policies for this table.
