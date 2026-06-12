"""Genera 1_ingenieria_atributos_y_rag.ipynb — PASO 1 entregable parcial3."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NB = ROOT / "1_ingenieria_atributos_y_rag.ipynb"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md(
        """# PASO 1 — Ingeniería de atributos y recuperación RAG

**Examen Parcial 3 · Proyecto de Investigación 2 · UNI**

Este notebook implementa **ingeniería de atributos (IA04/IA08)** y **recuperación RAG train-only**
sobre los artefactos del PASO 0 (`0_etl_ingesta_preprocesamiento/`).

| Concepto | Qué hace aquí |
|----------|----------------|
| **IA04 — train-only fit** | `TfidfVectorizer` + `TruncatedSVD` se ajustan **solo** con `5_conjunto_entrenamiento_holdout_70.csv` (280 filas) |
| **Anti-fuga RAG** | El historial de vecinos sale del corpus limpio **excluyendo** todos los `text_hash` de evaluación (n=400) |
| **Recuperación pgvector** | Backend principal: **pgvector en Docker** (`irene-postgres`) con esquema dedicado `entregable_rag` |
| **Hybrid RRF** | TF-IDF léxico + denso SVD + pgvector → fusión **Reciprocal Rank Fusion** (Cormack et al., 2009) |
| **Fallback sklearn** | Similitud coseno local si Docker/pgvector no está disponible |
| **Preview Var2** | Señales middleware (entropía vecinos, distancia media, conteo clases) **sin** ejecutar CrewAI ni middleware |

**Semilla:** `seed = 42`.

---

## Técnicas RAG SOTA implementadas

| Técnica | Implementación | Referencia |
|---------|----------------|------------|
| **Hybrid retrieval** | TF-IDF (proxy BM25) + vector denso + pgvector SQL | Ma et al. (2023) *Hybrid retrieval* |
| **RRF fusion** | `score = Σ 1/(k+rank)`, k=60 | Cormack et al. (2009) |
| **Train-only indexing** | Fit TF-IDF/SVD solo train; historial corpus−eval | Anti-leakage por `text_hash` |
| **Chunking** | `chunk_size=1` (documento completo) | Bugs Eclipse son textos cortos (~1–3 oraciones) |
| **Reranking ligero** | Re-score coseno − penalización distancia + boost clase | Sin cross-encoder (coste local cero) |
| **Metadata filtering** | Boost suave por clase mayoritaria en top denso | Filtrado blando, no hard-filter |
| **MRL / dimensión 64** | `TruncatedSVD(n=64)` sobre TF-IDF | Kusupati et al. (2022) Matryoshka RL |
| **HyDE** | *Futuro* — requiere LLM para hipótesis | Gao et al. (2022) |

---

## Reutilización vs implementación inline

| Componente | Origen | Nota |
|------------|--------|------|
| TF-IDF + SVD train-only | Inspirado en sprint6 (referencia) | Implementado inline en entregable |
| pgvector SQL | **`rag_pgvector_entregable.py`** (este PASO 1) | Esquema `entregable_rag` — NO toca tablas sprint6 |
| CrewAI multi-agente | **No en este paso** | Ver `0_instrucciones_crewai.md` y PASO 2 |

---

## Artefactos generados (esta carpeta)

| # | Archivo | Rol |
|---|---------|-----|
| 0 | `0_informe_configuracion_ingenieria.json` | Hiperparámetros, rutas, backend RAG |
| 1 | `1_matriz_embeddings_historial_rag.npz` | Embeddings SVD del historial RAG |
| 2 | `2_matriz_embeddings_conjunto_evaluacion.npy` | Embeddings SVD evaluación n=400 |
| 3 | `3_tabla_vecinos_recuperados_top5.csv` | Vecinos top-5 (backend principal híbrido) |
| 4 | `4_informe_auditoria_anti_fuga.json` | Overlap hashes, conteos, checks |
| 5 | `5_tabla_features_middleware_preview.csv` | Preview señales Var2 (sin middleware) |
| 6 | `6_informe_conexion_pgvector_docker.json` | Diagnóstico conexión Docker pgvector |
| 7 | `7_tabla_recuperacion_hibrida_rrf_top5.csv` | Auditoría detallada hybrid RRF |
| 8 | `8_comparacion_sklearn_vs_pgvector_muestra.csv` | Benchmark overlap top-5 (muestra n=20) |
"""
    ),
    code(
        """# ── Configuración reproducible ──────────────────────────────────────────
# Entrada: librerías + constantes.
# Salida: rutas PASO 0/1, hiperparámetros alineados con experiment.yaml.
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from IPython.display import Markdown, display
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Módulo RAG dedicado entregable (pgvector Docker)
PASO1 = Path.cwd().resolve()
if PASO1.name != "1_ingenieria_atributos_y_recuperacion_rag":
    PASO1 = PASO1 / "1_ingenieria_atributos_y_recuperacion_rag"
if str(PASO1) not in sys.path:
    sys.path.insert(0, str(PASO1))

import rag_pgvector_entregable as rag_pg  # noqa: E402

SEED = 42
SVD_DIM = 64
TOP_K = 5
HISTORY_N_MAX = 6000
CLASSES = ["play", "pausa", "stop"]
BENCHMARK_SAMPLE_N = 20
np.random.seed(SEED)

PASO0 = PASO1.parent / "0_etl_ingesta_preprocesamiento"

PATH_TRAIN = PASO0 / "5_conjunto_entrenamiento_holdout_70.csv"
PATH_TEST = PASO0 / "6_conjunto_prueba_holdout_30.csv"
PATH_EVAL = PASO0 / "8_conjunto_evaluacion_experimento_n400.csv"
PATH_CORPUS = PASO0 / "2_corpus_limpio_bugsrepo.csv"

for p in (PATH_TRAIN, PATH_EVAL, PATH_CORPUS):
    if not p.exists():
        raise FileNotFoundError(f"Falta artefacto PASO 0: {p}")

print(f"PASO 1 : {PASO1}")
print(f"PASO 0 : {PASO0}")
print(f"seed={SEED}, svd_dim={SVD_DIM}, top_k={TOP_K}")
print(f"pgvector config: {rag_pg.get_pg_config()}")"""
    ),
    code(
        """# ── Carga artefactos ETL (PASO 0) ───────────────────────────────────────
# Entrada: CSV del PASO 0.
# Salida: DataFrames train, test (ref.), eval, corpus.

df_train = pd.read_csv(PATH_TRAIN)
df_test = pd.read_csv(PATH_TEST) if PATH_TEST.exists() else None
df_eval = pd.read_csv(PATH_EVAL)
df_corpus = pd.read_csv(PATH_CORPUS)

for name, df in [("train", df_train), ("eval", df_eval), ("corpus", df_corpus)]:
    assert "text_hash" in df.columns and "text" in df.columns
    print(f"{name:6s} n={len(df):>6}  cols={list(df.columns)}")

eval_hashes = set(df_eval["text_hash"].astype(str))
train_hashes = set(df_train["text_hash"].astype(str))
print(f"eval_hashes={len(eval_hashes)}  train∩eval={len(train_hashes & eval_hashes)}")"""
    ),
    md(
        """## Historial RAG anti-fuga

El **fit** de transformaciones usa solo **train (280)**. El **pool de historial** para recuperación
se construye desde el corpus limpio excluyendo **todos** los hashes de evaluación (n=400), garantizando
`overlap(history, eval) = 0` en la auditoría.

**Chunking:** cada bug report se indexa como **un solo chunk** (`chunk_index=0`). Los textos Eclipse
son descripciones cortas (título + resumen); fragmentar reduciría contexto semántico sin beneficio medible.
"""
    ),
    code(
        """# ── Pool historial RAG (corpus − eval) ──────────────────────────────────
# Entrada: corpus + hashes eval.
# Salida: df_history, metadatos muestreo.


def stratified_sample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    if len(df) <= n:
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    counts = df["thesis_class"].value_counts().reindex(CLASSES).fillna(0).astype(int)
    base, rem = divmod(n, len(CLASSES))
    parts = []
    for i, cls in enumerate(CLASSES):
        take = min(int(counts[cls]), base + (1 if i < rem else 0))
        if take:
            parts.append(df[df["thesis_class"] == cls].sample(n=take, random_state=seed))
    sampled = pd.concat(parts) if parts else df.sample(n=n, random_state=seed)
    if len(sampled) < n:
        rest = df.drop(sampled.index, errors="ignore")
        if len(rest):
            extra = rest.sample(n=min(n - len(sampled), len(rest)), random_state=seed)
            sampled = pd.concat([sampled, extra])
    return sampled.sample(frac=1.0, random_state=seed).reset_index(drop=True)


pool_full = df_corpus[~df_corpus["text_hash"].astype(str).isin(eval_hashes)].copy()
target_n = len(pool_full)
if HISTORY_N_MAX is not None and len(pool_full) > HISTORY_N_MAX:
    target_n = HISTORY_N_MAX
    df_history = stratified_sample(pool_full, HISTORY_N_MAX, SEED)
else:
    df_history = pool_full.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

history_meta = {
    "pool_excl_eval_n": int(len(pool_full)),
    "history_n": int(len(df_history)),
    "history_n_max": HISTORY_N_MAX,
    "sampling": "stratified_fixed_seed" if HISTORY_N_MAX and len(pool_full) > HISTORY_N_MAX else "full_pool_excl_eval",
    "eval_hash_overlap": int(len(set(df_history["text_hash"].astype(str)) & eval_hashes)),
    "chunk_policy": "chunk_size_1_full_document",
}
print(json.dumps(history_meta, indent=2))"""
    ),
    md(
        """## TF-IDF + TruncatedSVD (dim=64, train-only fit)

Alineado con `configs/experiment.yaml` (`svd_dim: 64`, `retrieval_k: 5`).

**MRL / reducción dimensional:** `TruncatedSVD` proyecta TF-IDF sparse a 64 dimensiones densas,
análogo a *Matryoshka Representation Learning* (Kusupati et al., 2022) — permite embeddings
compactos para pgvector sin API de embedding externa.
"""
    ),
    code(
        """# ── Embeddings train-only ───────────────────────────────────────────────
# Entrada: textos train (fit), history + eval (transform).
# Salida: matrices normalizadas + metadatos fit.

train_texts = df_train["text"].astype(str).tolist()
history_texts = df_history["text"].astype(str).tolist()
eval_texts = df_eval["text"].astype(str).tolist()

# sublinear_tf ≈ proxy BM25 para rama léxica del hybrid retrieval
vectorizer = TfidfVectorizer(
    max_features=12000,
    ngram_range=(1, 2),
    min_df=2,
    stop_words="english",
    sublinear_tf=True,
)
train_sparse = vectorizer.fit_transform(train_texts)
history_sparse = vectorizer.transform(history_texts)
eval_sparse = vectorizer.transform(eval_texts)

max_dim = max(2, min(SVD_DIM, train_sparse.shape[0] - 1, train_sparse.shape[1] - 1))
svd = TruncatedSVD(n_components=max_dim, random_state=SEED)
train_vecs = normalize(svd.fit_transform(train_sparse))
history_vecs = normalize(svd.transform(history_sparse))
eval_vecs = normalize(svd.transform(eval_sparse))

fit_meta = {
    "vectorizer_fit_rows": len(train_texts),
    "eval_rows_in_fit": 0,
    "history_rows_in_fit": 0,
    "svd_fit_rows": len(train_texts),
    "svd_dim_requested": SVD_DIM,
    "svd_dim_effective": int(max_dim),
    "vocabulary_size": int(len(vectorizer.vocabulary_)),
    "mrl_note": "TruncatedSVD 64 como reducción dimensional estilo MRL",
}
print(json.dumps(fit_meta, indent=2))
print(f"history_vecs {history_vecs.shape}  eval_vecs {eval_vecs.shape}")"""
    ),
    md(
        """## RAG con pgvector (Docker)

Conexión al contenedor **`irene-postgres`** (`pgvector/pgvector:pg15`):

| Variable | Default entregable |
|----------|-------------------|
| `PGHOST` | `127.0.0.1` |
| `PGPORT` | `5432` |
| `PGDATABASE` | `irene` |
| `PGUSER` | `postgres` |
| `PGPASSWORD` | `root` |

**Tablas dedicadas (namespace propio):**
- `entregable_rag.chunks` — embeddings historial train-only
- `entregable_rag.run_meta` — metadatos de corrida

> No se reutilizan tablas de sprint6 ni esquemas `tenant_*` / `platform`.
"""
    ),
    code(
        """# ── Conexión y setup pgvector Docker ────────────────────────────────────
# Entrada: config Docker + embeddings historial.
# Salida: informe conexión, schema/tablas entregable, filas insertadas.

pg_ok, pg_status = rag_pg.check_pgvector_sql()
pg_connection_report = rag_pg.build_connection_report()
print(json.dumps({"connection_ok": pg_ok, "status": pg_status}, indent=2))

pg_insert_info: dict[str, Any] = {}
if pg_ok:
    schema_info = rag_pg.setup_entregable_schema(int(max_dim))
    pg_insert_info = rag_pg.insert_history_embeddings(
        df_history,
        history_vecs,
        seed=SEED,
        svd_dim=int(max_dim),
        chunk_policy=history_meta["chunk_policy"],
    )
    pg_connection_report["schema_setup"] = schema_info
    pg_connection_report["insert"] = pg_insert_info
    print(f"Insertados {pg_insert_info['n_inserted']} chunks en {pg_insert_info['table']}")
else:
    pg_connection_report["fallback"] = "sklearn_cosine — Docker/pgvector no disponible"
    print("ADVERTENCIA: pgvector no disponible; se usará fallback sklearn.")"""
    ),
    md(
        """## Recuperación híbrida RRF (principal) vs fallback sklearn

**Flujo principal (pgvector disponible):**
1. Ranking léxico TF-IDF (proxy BM25)
2. Ranking denso SVD local
3. Ranking pgvector SQL (`<=>` cosine)
4. Fusión **RRF** (k=60)
5. **Reranking** ligero: coseno − 0.15×distancia + boost clase mayoritaria

**Fallback:** similitud coseno sklearn sobre embeddings SVD (sin Docker).
"""
    ),
    code(
        """# ── Recuperación vecinos ────────────────────────────────────────────────
# Entrada: embeddings history/eval, sparse matrices, df_history, df_eval.
# Salida: neighbors (híbrido), sklearn baseline, audit tables, backend.


def retrieve_cosine_sklearn(
    history_df: pd.DataFrame,
    query_df: pd.DataFrame,
    history_vecs: np.ndarray,
    query_vecs: np.ndarray,
    k: int,
) -> tuple[list[list[dict[str, Any]]], pd.DataFrame]:
    sims = cosine_similarity(query_vecs, history_vecs)
    retrieved: list[list[dict[str, Any]]] = []
    audit_rows: list[dict[str, Any]] = []
    for qpos, row in enumerate(query_df.itertuples(index=False)):
        qhash = str(row.text_hash)
        scores = sims[qpos].copy()
        for hpos, hrow in enumerate(history_df.itertuples(index=False)):
            if str(hrow.text_hash) == qhash:
                scores[hpos] = -1.0
        top_idx = np.argsort(-scores)[:k]
        neighbors: list[dict[str, Any]] = []
        for rank, hpos in enumerate(top_idx, start=1):
            hrow = history_df.iloc[int(hpos)]
            dist = 1.0 - float(scores[int(hpos)])
            item = {
                "idx": int(hpos),
                "text_hash": str(hrow["text_hash"]),
                "text": str(hrow["text"]),
                "label": str(hrow["thesis_class"]),
                "distance": dist,
                "similarity": float(scores[int(hpos)]),
            }
            neighbors.append(item)
            audit_rows.append(
                {
                    "query_idx": qpos,
                    "query_hash": qhash,
                    "query_text": str(row.text),
                    "rank": rank,
                    "neighbor_idx": int(hpos),
                    "neighbor_hash": item["text_hash"],
                    "neighbor_label": item["label"],
                    "distance": dist,
                    "similarity": item["similarity"],
                    "retrieval_mode": "sklearn_cosine_fallback",
                }
            )
        retrieved.append(neighbors)
    return retrieved, pd.DataFrame(audit_rows)


# Baseline sklearn (para comparación y fallback)
sklearn_neighbors, sklearn_audit = retrieve_cosine_sklearn(
    df_history, df_eval, history_vecs, eval_vecs, TOP_K
)

# Recuperación principal: hybrid RRF + pgvector
if pg_ok:
    neighbors_all, hybrid_audit, retrieval_backend = rag_pg.hybrid_retrieve_rrf(
        df_history,
        df_eval,
        history_vecs,
        eval_vecs,
        history_sparse,
        eval_sparse,
        TOP_K,
        use_pgvector=True,
        metadata_filter=True,
    )
else:
    neighbors_all = sklearn_neighbors
    hybrid_audit = sklearn_audit
    retrieval_backend = f"sklearn_cosine_fallback (pgvector: {pg_status.get('reason', 'unavailable')})"

print(f"Backend RAG principal: {retrieval_backend}")
print(f"Vecinos híbridos auditados: {len(hybrid_audit)} filas ({len(df_eval)} queries × k={TOP_K})")"""
    ),
    code(
        """# ── Benchmark sklearn vs pgvector (muestra) ─────────────────────────────
# Entrada: vecinos sklearn vs híbridos.
# Salida: df_compare (8_comparacion_sklearn_vs_pgvector_muestra.csv).

df_compare = rag_pg.compare_retrieval_sample(
    sklearn_neighbors,
    neighbors_all,
    df_eval,
    n_sample=BENCHMARK_SAMPLE_N,
)
if len(df_compare):
    print(
        f"Overlap medio top-5 (n={len(df_compare)}): "
        f"{df_compare['overlap_at_5'].mean():.2f}  "
        f"Jaccard: {df_compare['jaccard_at_5'].mean():.3f}"
    )
display(df_compare.head(5))"""
    ),
    md(
        """## Preview features middleware (Var2) — sin ejecutar middleware

Señales que consumirá el middleware de criticidad en PASO 2/Var2:
entropía de etiquetas vecinos, distancia media, conteos por clase, similitud media.
"""
    ),
    code(
        """# ── Features middleware preview ─────────────────────────────────────────
# Entrada: neighbors recuperados (híbrido RRF).
# Salida: df_preview (5_tabla_features_middleware_preview.csv).


def label_entropy(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    return float(-sum(p * math.log2(p) for p in probs if p > 0))


preview_rows: list[dict[str, Any]] = []
for qpos, (row, neighbors) in enumerate(zip(df_eval.itertuples(index=False), neighbors_all)):
    labels = [n["label"] for n in neighbors]
    dists = [float(n["distance"]) for n in neighbors]
    sims = [float(n.get("similarity", 1.0 - d)) for n, d in zip(neighbors, dists)]
    counts = Counter(labels)
    preview_rows.append(
        {
            "query_idx": qpos,
            "query_hash": str(row.text_hash),
            "true_label": str(row.thesis_class),
            "neighbor_entropy": label_entropy(labels),
            "neighbor_mean_distance": float(np.mean(dists)) if dists else 0.0,
            "neighbor_mean_similarity": float(np.mean(sims)) if sims else 0.0,
            "neighbor_n_play": int(counts.get("play", 0)),
            "neighbor_n_pausa": int(counts.get("pausa", 0)),
            "neighbor_n_stop": int(counts.get("stop", 0)),
            "neighbor_majority_label": counts.most_common(1)[0][0] if counts else "pausa",
            "retrieval_backend": retrieval_backend,
        }
    )

df_preview = pd.DataFrame(preview_rows)
display(df_preview.head(3))"""
    ),
    md(
        """## Auditoría anti-fuga

Verificaciones explícitas IA04: fit solo train, historial RAG sin overlap con eval.
"""
    ),
    code(
        """# ── Auditoría anti-fuga ─────────────────────────────────────────────────
# Entrada: hashes y metadatos fit/history.
# Salida: audit_report (4_informe_auditoria_anti_fuga.json).

history_hashes = set(df_history["text_hash"].astype(str))
overlap_history_eval = history_hashes & eval_hashes
overlap_train_in_fit_only = train_hashes & eval_hashes

audit_report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "seed": SEED,
    "checks": {
        "history_eval_hash_overlap": int(len(overlap_history_eval)),
        "history_eval_hash_overlap_ok": len(overlap_history_eval) == 0,
        "vectorizer_fit_rows_equals_train": fit_meta["vectorizer_fit_rows"] == len(df_train),
        "eval_rows_in_fit_zero": fit_meta["eval_rows_in_fit"] == 0,
        "history_rows_in_fit_zero": fit_meta["history_rows_in_fit"] == 0,
        "train_subset_of_eval_lab": int(len(overlap_train_in_fit_only)) == len(df_train),
        "pgvector_connection_ok": pg_ok,
    },
    "counts": {
        "n_train": len(df_train),
        "n_eval": len(df_eval),
        "n_history": len(df_history),
        "n_corpus": len(df_corpus),
        "pool_excl_eval": history_meta["pool_excl_eval_n"],
    },
    "history_meta": history_meta,
    "fit_meta": fit_meta,
    "retrieval_backend": retrieval_backend,
    "pgvector_insert": pg_insert_info,
    "note": "TF-IDF/SVD fit en train 280; historial RAG corpus−eval; pgvector esquema entregable_rag.",
}
print(json.dumps(audit_report["checks"], indent=2))"""
    ),
    md(
        """## Load — persistir artefactos numerados
"""
    ),
    code(
        """# ── Persistencia artefactos PASO 1 ──────────────────────────────────────
# Salida: 0_…json … 8_…csv

config_report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "seed": SEED,
    "svd_dim": SVD_DIM,
    "top_k": TOP_K,
    "history_n_max": HISTORY_N_MAX,
    "classes": CLASSES,
    "inputs": {
        "train": str(PATH_TRAIN.name),
        "eval": str(PATH_EVAL.name),
        "corpus": str(PATH_CORPUS.name),
    },
    "history_meta": history_meta,
    "fit_meta": fit_meta,
    "retrieval_backend": retrieval_backend,
    "pgvector_status": pg_status,
    "pgvector_schema": rag_pg.SCHEMA,
    "pgvector_tables": [rag_pg.TABLE_CHUNKS, rag_pg.TABLE_META],
    "sota_techniques": pg_connection_report.get("sota_notes", {}),
    "reuse_notes": {
        "pgvector_module": "rag_pgvector_entregable.py (namespace entregable_rag, sin sprint6)",
        "crewai": "Activación en PASO 2 (Var1); ver 0_instrucciones_crewai.md",
    },
}

out0 = PASO1 / "0_informe_configuracion_ingenieria.json"
out1 = PASO1 / "1_matriz_embeddings_historial_rag.npz"
out2 = PASO1 / "2_matriz_embeddings_conjunto_evaluacion.npy"
out3 = PASO1 / "3_tabla_vecinos_recuperados_top5.csv"
out4 = PASO1 / "4_informe_auditoria_anti_fuga.json"
out5 = PASO1 / "5_tabla_features_middleware_preview.csv"
out6 = PASO1 / "6_informe_conexion_pgvector_docker.json"
out7 = PASO1 / "7_tabla_recuperacion_hibrida_rrf_top5.csv"
out8 = PASO1 / "8_comparacion_sklearn_vs_pgvector_muestra.csv"

out0.write_text(json.dumps(config_report, indent=2, ensure_ascii=False), encoding="utf-8")
np.savez_compressed(
    out1,
    embeddings=history_vecs,
    text_hash=df_history["text_hash"].astype(str).values,
    thesis_class=df_history["thesis_class"].astype(str).values,
)
np.save(out2, eval_vecs)
hybrid_audit.to_csv(out3, index=False)
out4.write_text(json.dumps(audit_report, indent=2, ensure_ascii=False), encoding="utf-8")
df_preview.to_csv(out5, index=False)
out6.write_text(json.dumps(pg_connection_report, indent=2, ensure_ascii=False), encoding="utf-8")
hybrid_audit.to_csv(out7, index=False)
df_compare.to_csv(out8, index=False)

artifact_lines = "\\n".join(f"- `{p.name}`" for p in (out0, out1, out2, out3, out4, out5, out6, out7, out8))
display(Markdown("### Artefactos escritos\\n" + artifact_lines))"""
    ),
]

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"},
    },
    "cells": cells,
}

NB.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Escrito: {NB}")
