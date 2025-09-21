-- Bật pgvector nếu chưa có
create extension if not exists vector;
create extension if not exists pg_trgm;

-- Tạo bảng rag_chunks
create table if not exists public.rag_chunks (
  id bigserial primary key,
  chunk_uid varchar(64) unique not null,
  course_id bigint,
  doc_type varchar(64) not null,
  lang varchar(8) not null default 'vi',
  content text not null,
  content_tokens int,
  embedding vector(768) not null,
  metadata jsonb not null default '{}',
  created_at timestamptz not null,
  updated_at timestamptz not null
);

-- Tạo cột tsvector (nếu chưa có)
alter table public.rag_chunks
  add column if not exists content_tsv tsvector;

-- Trigger cập nhật content_tsv
create or replace function public.rag_chunks_tsv_trigger()
returns trigger as $$
begin
  new.content_tsv :=
    setweight(to_tsvector('simple', coalesce(new.doc_type,'')), 'A') ||
    setweight(to_tsvector('simple', coalesce(new.content,'')), 'B');
  return new;
end $$ language plpgsql;

drop trigger if exists trg_rag_chunks_tsv on public.rag_chunks;
create trigger trg_rag_chunks_tsv
before insert or update on public.rag_chunks
for each row execute procedure public.rag_chunks_tsv_trigger();

-- Index vector cosine (approximate search)
create index if not exists idx_rag_chunks_embedding_ivfflat
on public.rag_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Index cho full-text search
create index if not exists idx_rag_chunks_tsv
on public.rag_chunks using gin (content_tsv);

-- Index phụ
create index if not exists idx_rag_chunks_course_doc
on public.rag_chunks(course_id, doc_type);

-- Phân tích thống kê
analyze public.rag_chunks;