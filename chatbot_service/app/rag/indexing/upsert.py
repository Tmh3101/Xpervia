import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from sqlalchemy import select, text as sql_text
from app.core.schemas import RagDocs, Users, Courses
from app.rag.embedding.embedder import embed_docs
from app.rag.indexing.build_docs import fetch_course_block, build_document_text

def _full_name(u: Optional[Users]) -> str:
    if not u:
        return ""
    return f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip()

def _sha256(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def get_existing_checksum(session: Session, course_id: int) -> Optional[str]:
    row = session.execute(
        select(RagDocs.checksum).where(
            RagDocs.course_id == course_id,
            RagDocs.doc_type == "course_overview"
        )
    ).first()
    return row[0] if row else None

def embed_course(course_id: int):
    with SessionLocal() as session:
        block = fetch_course_block(session, course_id)
        if not block:
            print(f"[embed_course] Course {course_id} not found.")
            return

        text, meta = build_document_text(block)
        checksum = _sha256(text)
        existing = get_existing_checksum(session, course_id)
        if existing == checksum:
            print(f"[embed_course] Course {course_id} is up-to-date.")
            return

        emb = embed_docs([text])[0]
        upsert_document(session, course_id=course_id, text=text, meta=meta, embedding=emb, checksum=checksum)
        session.commit()
        print(f"[embed_course] Upserted document for course_id={course_id}.")

def embed_all_courses():
    with SessionLocal() as session:
        course_ids = [r[0] for r in session.execute(select(Courses.id)).all()]
        if not course_ids:
            print("[embed_all_courses] No courses found.")
            return

        to_embed = []
        for cid in course_ids:
            block = fetch_course_block(session, cid)
            if not block:
                continue
            text, meta = build_document_text(block)
            checksum = _sha256(text)
            existing = get_existing_checksum(session, cid)
            if existing == checksum:
                continue
            to_embed.append((cid, text, meta, checksum))

        if not to_embed:
            print("[embed_all_courses] All documents are up-to-date.")
            return

        texts = [t[1] for t in to_embed]
        embs = embed_docs(texts)
        for (cid, text, meta, chksum), emb in zip(to_embed, embs):
            upsert_document(session, course_id=cid, text=text, meta=meta, embedding=emb, checksum=chksum)

        session.commit()
        print(f"[embed_all_courses] Upserted {len(to_embed)} documents.")


def upsert_document(session: Session, *, course_id: int, text: str, meta: dict, embedding: List[float], checksum: str):
    print("[Upsert Document] Course Meta:", meta)
    updated = session.execute(
        sql_text("""
            update rag_docs
            set lang = :lang,
                text = :text,
                embedding = :embedding,
                meta = CAST(:meta AS JSONB),
                checksum = :checksum,
                updated_at = now()
            where course_id = :course_id and doc_type = 'course_overview' and checksum <> :checksum
        """),
        {
            "lang": "multi",
            "text": text,
            "embedding": list(map(float, embedding)),
            "meta": json.dumps(meta, ensure_ascii=False),
            "checksum": checksum,
            "course_id": course_id
        }
    ).rowcount

    print("[Upsert Document] Rows updated:", updated)

    if updated == 0:
        session.execute(
            sql_text("""
                insert into rag_docs (course_id, doc_type, lang, text, embedding, meta, checksum, updated_at)
                values (:course_id, 'course_overview', :lang, :text, :embedding, CAST(:meta AS JSONB), :checksum, now())
                on conflict (course_id, doc_type) do update set
                    lang = EXCLUDED.lang,
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding,
                    meta = EXCLUDED.meta,
                    checksum = EXCLUDED.checksum,
                    updated_at = now()
            """),
            {
                "course_id": course_id,
                "lang": "multi",
                "text": text,
                "embedding": list(map(float, embedding)),
                "meta": json.dumps(meta, ensure_ascii=False),
                "checksum": checksum
            }
        )