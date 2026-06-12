"""RAG con pgvector (Docker) — namespace dedicado entregable parcial3.

No importa ni modifica tablas de sprint6 ni otros esquemas del proyecto.
Esquema propio: ``entregable_rag`` con tabla ``chunks``.

Referencias SOTA (documentadas en notebook):
- Hybrid retrieval + RRF: Cormack et al. (2009); Lin & Ma (2021) fusion pipelines.
- pgvector ANN: Johnson et al. (2019) FAISS; pgvector HNSW/IVFFlat.
- MRL / dimensión reducida: Matryoshka Representation Learning (Kusupati et al., 2022).
- HyDE (Gao et al., 2022): documentado como trabajo futuro (requiere LLM).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

# ── Conexión Docker irene-postgres (pgvector/pgvector:pg15) ─────────────────
DEFAULT_PG = {
    "host": os.getenv("PGHOST", "127.0.0.1"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "irene"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "root"),
}

SCHEMA = "entregable_rag"
TABLE_CHUNKS = "chunks"
TABLE_META = "run_meta"
RRF_K = 60  # constante RRF estándar (Cormack et al., 2009)


def get_pg_config() -> dict[str, Any]:
    cfg = dict(DEFAULT_PG)
    cfg["password_present"] = bool(cfg.get("password"))
    return cfg


def _import_pg_driver():
    try:
        import psycopg2  # type: ignore

        return "psycopg2", psycopg2
    except ImportError:
        try:
            import psycopg  # type: ignore

            return "psycopg", psycopg
        except ImportError:
            return None, None


def connect():
    driver_name, driver = _import_pg_driver()
    if driver is None:
        raise RuntimeError("Instala psycopg2 o psycopg para usar pgvector")
    conn = driver.connect(
        host=DEFAULT_PG["host"],
        port=DEFAULT_PG["port"],
        dbname=DEFAULT_PG["dbname"],
        user=DEFAULT_PG["user"],
        password=DEFAULT_PG["password"],
        connect_timeout=5,
    )
    conn.autocommit = True
    return conn, driver_name


def check_pgvector_sql() -> tuple[bool, dict[str, Any]]:
    """Diagnóstico no destructivo de Postgres + extensión vector."""
    status: dict[str, Any] = {
        "pg_config": get_pg_config(),
        "available": False,
        "schema": SCHEMA,
        "tables": [f"{SCHEMA}.{TABLE_CHUNKS}", f"{SCHEMA}.{TABLE_META}"],
    }
    driver_name, _ = _import_pg_driver()
    if driver_name is None:
        status["reason"] = "driver_missing"
        return False, status
    status["driver"] = driver_name
    try:
        conn, _ = connect()
    except Exception as exc:
        status["reason"] = f"connection_error: {type(exc).__name__}: {exc}"
        return False, status
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            row = cur.fetchone()
            if not row:
                status["reason"] = "vector_extension_missing"
                return False, status
            status["vector_version"] = row[0]
            cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata WHERE schema_name = %s
                )
                """,
                (SCHEMA,),
            )
            status["schema_exists"] = bool(cur.fetchone()[0])
            cur.execute("SELECT 1")
            status["ping"] = cur.fetchone()[0] == 1
        status["available"] = True
        status["reason"] = "ok"
        return True, status
    except Exception as exc:
        status["reason"] = f"inspect_error: {type(exc).__name__}: {exc}"
        return False, status
    finally:
        conn.close()


def setup_entregable_schema(svd_dim: int) -> dict[str, Any]:
    """Crea esquema/tablas dedicadas entregable (DROP+CREATE chunks por corrida)."""
    conn, driver = connect()
    info: dict[str, Any] = {"schema": SCHEMA, "svd_dim": svd_dim, "driver": driver}
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
            cur.execute(f"DROP TABLE IF EXISTS {SCHEMA}.{TABLE_CHUNKS} CASCADE")
            cur.execute(f"DROP TABLE IF EXISTS {SCHEMA}.{TABLE_META} CASCADE")
            cur.execute(
                f"""
                CREATE TABLE {SCHEMA}.{TABLE_CHUNKS} (
                    chunk_id SERIAL PRIMARY KEY,
                    text_hash TEXT NOT NULL UNIQUE,
                    text_content TEXT NOT NULL,
                    thesis_class TEXT NOT NULL,
                    embedding vector({svd_dim}) NOT NULL,
                    chunk_index INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                f"""
                CREATE TABLE {SCHEMA}.{TABLE_META} (
                    run_id SERIAL PRIMARY KEY,
                    seed INT,
                    svd_dim INT,
                    n_chunks INT,
                    chunk_policy TEXT,
                    anti_leakage TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLE_CHUNKS}_class
                ON {SCHEMA}.{TABLE_CHUNKS} (thesis_class)
                """
            )
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLE_CHUNKS}_embedding_hnsw
                ON {SCHEMA}.{TABLE_CHUNKS}
                USING hnsw (embedding vector_cosine_ops)
                """
            )
        info["status"] = "created"
        return info
    finally:
        conn.close()


def _vec_literal(vec: np.ndarray) -> str:
    return "[" + ",".join(f"{float(x):.8f}" for x in vec.tolist()) + "]"


def insert_history_embeddings(
    df_history: pd.DataFrame,
    history_vecs: np.ndarray,
    *,
    seed: int,
    svd_dim: int,
    chunk_policy: str = "chunk_size_1_full_document",
) -> dict[str, Any]:
    """Inserta embeddings train-only del historial RAG en tabla dedicada."""
    if len(df_history) != len(history_vecs):
        raise ValueError("df_history y history_vecs deben tener la misma longitud")
    conn, driver = connect()
    inserted = 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.{TABLE_META}
                    (seed, svd_dim, n_chunks, chunk_policy, anti_leakage)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING run_id
                """,
                (seed, svd_dim, len(df_history), chunk_policy, "corpus_minus_eval_hashes"),
            )
            run_id = cur.fetchone()[0]
            for i, row in enumerate(df_history.itertuples(index=False)):
                cur.execute(
                    f"""
                    INSERT INTO {SCHEMA}.{TABLE_CHUNKS}
                        (text_hash, text_content, thesis_class, embedding, chunk_index)
                    VALUES (%s, %s, %s, %s::vector, %s)
                    ON CONFLICT (text_hash) DO UPDATE SET
                        text_content = EXCLUDED.text_content,
                        thesis_class = EXCLUDED.thesis_class,
                        embedding = EXCLUDED.embedding,
                        chunk_index = EXCLUDED.chunk_index
                    """,
                    (
                        str(row.text_hash),
                        str(row.text),
                        str(row.thesis_class),
                        _vec_literal(history_vecs[i]),
                        0,
                    ),
                )
                inserted += 1
        return {
            "run_id": int(run_id),
            "n_inserted": inserted,
            "driver": driver,
            "table": f"{SCHEMA}.{TABLE_CHUNKS}",
        }
    finally:
        conn.close()


def retrieve_vector_pgvector(
    query_vecs: np.ndarray,
    k: int,
    exclude_hashes: set[str] | None = None,
    filter_class: str | None = None,
) -> list[list[dict[str, Any]]]:
    """Top-k por distancia coseno en pgvector (<=> operador cosine)."""
    exclude_hashes = exclude_hashes or set()
    conn, _ = connect()
    results: list[list[dict[str, Any]]] = []
    try:
        with conn.cursor() as cur:
            for qpos, qvec in enumerate(query_vecs):
                vec_lit = _vec_literal(qvec)
                limit = k + len(exclude_hashes) + 5
                if filter_class:
                    sql = f"""
                        SELECT text_hash, text_content, thesis_class,
                               embedding <=> %s::vector AS distance
                        FROM {SCHEMA}.{TABLE_CHUNKS}
                        WHERE thesis_class = %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """
                    cur.execute(sql, (vec_lit, filter_class, vec_lit, limit))
                else:
                    sql = f"""
                        SELECT text_hash, text_content, thesis_class,
                               embedding <=> %s::vector AS distance
                        FROM {SCHEMA}.{TABLE_CHUNKS}
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """
                    cur.execute(sql, (vec_lit, vec_lit, limit))
                rows = cur.fetchall()
                neighbors: list[dict[str, Any]] = []
                for text_hash, text_content, thesis_class, distance in rows:
                    if str(text_hash) in exclude_hashes:
                        continue
                    dist = float(distance)
                    neighbors.append(
                        {
                            "text_hash": str(text_hash),
                            "text": str(text_content),
                            "label": str(thesis_class),
                            "distance": dist,
                            "similarity": 1.0 - dist,
                            "source": "pgvector",
                            "query_idx": qpos,
                        }
                    )
                    if len(neighbors) >= k:
                        break
                results.append(neighbors)
        return results
    finally:
        conn.close()


def sparse_tfidf_ranking(
    history_sparse: csr_matrix,
    query_sparse: csr_matrix,
    history_df: pd.DataFrame,
    k: int,
    exclude_hashes: set[str] | None = None,
) -> list[list[tuple[int, float]]]:
    """Ranking léxico TF-IDF (proxy BM25 con sublinear_tf en fit del vectorizer)."""
    exclude_hashes = exclude_hashes or set()
    sims = cosine_similarity(query_sparse, history_sparse)
    rankings: list[list[tuple[int, float]]] = []
    for qpos in range(sims.shape[0]):
        scores = sims[qpos].copy()
        for hpos, hrow in enumerate(history_df.itertuples(index=False)):
            if str(hrow.text_hash) in exclude_hashes:
                scores[hpos] = -1.0
        top_idx = np.argsort(-scores)[: k + 5]
        ranked = [(int(i), float(scores[i])) for i in top_idx if scores[i] > -0.5][:k]
        rankings.append(ranked)
    return rankings


def vector_ranking_local(
    history_vecs: np.ndarray,
    query_vecs: np.ndarray,
    history_df: pd.DataFrame,
    k: int,
    exclude_hashes: set[str] | None = None,
) -> list[list[tuple[int, float]]]:
    """Ranking denso local (sklearn cosine) para RRF híbrido."""
    exclude_hashes = exclude_hashes or set()
    sims = cosine_similarity(query_vecs, history_vecs)
    rankings: list[list[tuple[int, float]]] = []
    for qpos in range(sims.shape[0]):
        scores = sims[qpos].copy()
        for hpos, hrow in enumerate(history_df.itertuples(index=False)):
            if str(hrow.text_hash) in exclude_hashes:
                scores[hpos] = -1.0
        top_idx = np.argsort(-scores)[: k + 5]
        ranked = [(int(i), float(scores[i])) for i in top_idx if scores[i] > -0.5][:k]
        rankings.append(ranked)
    return rankings


def reciprocal_rank_fusion(
    rank_lists: list[list[tuple[int, float]]],
    k_out: int,
    rrf_k: int = RRF_K,
) -> list[list[tuple[int, float]]]:
    """Fusión RRF sobre múltiples listas rankeadas (índice historial, score auxiliar)."""
    n_queries = len(rank_lists[0])
    fused: list[list[tuple[int, float]]] = []
    for qpos in range(n_queries):
        scores: dict[int, float] = {}
        for retriever_ranks in rank_lists:
            for rank, (idx, _aux) in enumerate(retriever_ranks[qpos], start=1):
                scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank)
        ordered = sorted(scores.items(), key=lambda x: -x[1])[:k_out]
        fused.append([(idx, sc) for idx, sc in ordered])
    return fused


def light_rerank(
    neighbors: list[dict[str, Any]],
    query_vec: np.ndarray,
    history_vecs: np.ndarray,
    history_df: pd.DataFrame,
    *,
    distance_penalty: float = 0.15,
    class_boost: float = 0.05,
    majority_class: str | None = None,
) -> list[dict[str, Any]]:
    """Re-score ligero: coseno + penalización distancia + boost metadata clase."""
    reranked: list[tuple[float, dict[str, Any]]] = []
    hash_to_pos = {
        str(r.text_hash): i for i, r in enumerate(history_df.itertuples(index=False))
    }
    for n in neighbors:
        hpos = hash_to_pos.get(n["text_hash"])
        if hpos is None:
            reranked.append((n.get("similarity", 0.0), n))
            continue
        cos = float(cosine_similarity(query_vec.reshape(1, -1), history_vecs[hpos].reshape(1, -1))[0, 0])
        dist = float(n.get("distance", 1.0 - cos))
        score = cos - distance_penalty * dist
        if majority_class and n.get("label") == majority_class:
            score += class_boost
        item = dict(n)
        item["rerank_score"] = score
        item["similarity"] = cos
        item["distance"] = dist
        reranked.append((score, item))
    reranked.sort(key=lambda x: -x[0])
    out = []
    for rank, (_, item) in enumerate(reranked, start=1):
        item["rank"] = rank
        out.append(item)
    return out


def hybrid_retrieve_rrf(
    history_df: pd.DataFrame,
    query_df: pd.DataFrame,
    history_vecs: np.ndarray,
    query_vecs: np.ndarray,
    history_sparse: csr_matrix,
    query_sparse: csr_matrix,
    k: int,
    *,
    use_pgvector: bool = True,
    metadata_filter: bool = True,
) -> tuple[list[list[dict[str, Any]]], pd.DataFrame, str]:
    """Hybrid retrieval: TF-IDF + vector (+ pgvector) → RRF → rerank ligero."""
    exclude = {str(h) for h in query_df["text_hash"].astype(str)}
    tfidf_ranks = sparse_tfidf_ranking(history_sparse, query_sparse, history_df, k * 2, exclude)
    dense_ranks = vector_ranking_local(history_vecs, query_vecs, history_df, k * 2, exclude)

    rank_inputs = [tfidf_ranks, dense_ranks]
    backend_parts = ["tfidf_lexical", "svd_dense_local"]

    if use_pgvector:
        ok, _ = check_pgvector_sql()
        if ok:
            pg_neighbors = retrieve_vector_pgvector(
                query_vecs, k * 2, exclude_hashes=exclude, filter_class=None
            )
            pg_ranks: list[list[tuple[int, float]]] = []
            hash_to_pos = {
                str(r.text_hash): i for i, r in enumerate(history_df.itertuples(index=False))
            }
            for q_neighbors in pg_neighbors:
                ranked = []
                for rank, n in enumerate(q_neighbors, start=1):
                    hpos = hash_to_pos.get(n["text_hash"])
                    if hpos is not None:
                        ranked.append((hpos, n.get("similarity", 0.0)))
                pg_ranks.append(ranked)
            rank_inputs.append(pg_ranks)
            backend_parts.append("pgvector_sql")

    fused = reciprocal_rank_fusion(rank_inputs, k)

    all_neighbors: list[list[dict[str, Any]]] = []
    audit_rows: list[dict[str, Any]] = []

    for qpos, row in enumerate(query_df.itertuples(index=False)):
        qhash = str(row.text_hash)
        qvec = query_vecs[qpos]
        majority_class = None
        if metadata_filter:
            # filtro suave: clase mayoritaria en top denso guía rerank (no hard-filter)
            top_dense = dense_ranks[qpos][:3]
            if top_dense:
                labels = [str(history_df.iloc[i]["thesis_class"]) for i, _ in top_dense]
                majority_class = max(set(labels), key=labels.count)

        candidates: list[dict[str, Any]] = []
        for idx, rrf_score in fused[qpos]:
            hrow = history_df.iloc[int(idx)]
            cos = float(
                cosine_similarity(qvec.reshape(1, -1), history_vecs[int(idx)].reshape(1, -1))[0, 0]
            )
            candidates.append(
                {
                    "idx": int(idx),
                    "text_hash": str(hrow["text_hash"]),
                    "text": str(hrow["text"]),
                    "label": str(hrow["thesis_class"]),
                    "distance": 1.0 - cos,
                    "similarity": cos,
                    "rrf_score": float(rrf_score),
                    "source": "hybrid_rrf",
                }
            )

        reranked = light_rerank(
            candidates,
            qvec,
            history_vecs,
            history_df,
            majority_class=majority_class,
        )

        all_neighbors.append(reranked[:k])
        for n in reranked[:k]:
            audit_rows.append(
                {
                    "query_idx": qpos,
                    "query_hash": qhash,
                    "query_text": str(row.text),
                    "rank": n.get("rank"),
                    "neighbor_idx": n.get("idx"),
                    "neighbor_hash": n["text_hash"],
                    "neighbor_label": n["label"],
                    "distance": n.get("distance"),
                    "similarity": n.get("similarity"),
                    "rrf_score": n.get("rrf_score"),
                    "rerank_score": n.get("rerank_score"),
                    "retrieval_mode": "hybrid_rrf_pgvector" if use_pgvector else "hybrid_rrf_local",
                }
            )

    backend = "+".join(backend_parts) + "→rrf→rerank"
    return all_neighbors, pd.DataFrame(audit_rows), backend


def build_connection_report(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    ok, status = check_pgvector_sql()
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "connection_ok": ok,
        "docker_hint": "irene-postgres (pgvector/pgvector:pg15) @ 127.0.0.1:5432",
        "pg_config": get_pg_config(),
        "status": status,
        "dedicated_schema": SCHEMA,
        "dedicated_tables": [f"{SCHEMA}.{TABLE_CHUNKS}", f"{SCHEMA}.{TABLE_META}"],
        "sota_notes": {
            "hybrid": "TF-IDF léxico + denso SVD + pgvector con fusión RRF (k=60)",
            "chunking": "chunk_size=1 (bug report completo; textos cortos)",
            "mrl_dim": "TruncatedSVD 64 como reducción dimensional (estilo MRL)",
            "rerank": "coseno - penalización distancia + boost clase mayoritaria",
            "hyde": "futuro — requiere LLM para hipótesis de documento",
        },
    }
    if extra:
        report.update(extra)
    return report


def compare_retrieval_sample(
    sklearn_neighbors: list[list[dict[str, Any]]],
    hybrid_neighbors: list[list[dict[str, Any]]],
    query_df: pd.DataFrame,
    n_sample: int = 20,
) -> pd.DataFrame:
    """Benchmark pequeño: overlap top-5 sklearn vs híbrido pgvector."""
    rows: list[dict[str, Any]] = []
    n = min(n_sample, len(query_df))
    for qpos in range(n):
        sk_hashes = {n["text_hash"] for n in sklearn_neighbors[qpos]}
        hy_hashes = {n["text_hash"] for n in hybrid_neighbors[qpos]}
        overlap = len(sk_hashes & hy_hashes)
        rows.append(
            {
                "query_idx": qpos,
                "query_hash": str(query_df.iloc[qpos]["text_hash"]),
                "sklearn_top5": "|".join(sorted(sk_hashes)),
                "hybrid_top5": "|".join(sorted(hy_hashes)),
                "overlap_at_5": overlap,
                "jaccard_at_5": overlap / max(len(sk_hashes | hy_hashes), 1),
            }
        )
    return pd.DataFrame(rows)
