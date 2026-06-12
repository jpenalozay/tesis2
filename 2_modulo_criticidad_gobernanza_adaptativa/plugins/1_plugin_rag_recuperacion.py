"""
RagPlugin — consume recuperación híbrida del PASO 1 (sin re-indexar).

Lee `7_tabla_recuperacion_hibrida_rrf_top5.csv` con fallback a `3_tabla_vecinos_...`.
"""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

CLASSES = ("play", "pausa", "stop")


def _entropy(labels: list[str]) -> float:
    if not labels:
        return 1.0
    counts = Counter(labels)
    total = sum(counts.values())
    ent = -sum((c / total) * math.log(c / total) for c in counts.values())
    return ent / math.log(len(CLASSES))


def load_neighbors_table(path_primary: Path, path_fallback: Path | None = None) -> pd.DataFrame:
    """Carga tabla RAG; usa fallback si la principal no existe."""
    if path_primary.exists():
        return pd.read_csv(path_primary)
    if path_fallback and path_fallback.exists():
        return pd.read_csv(path_fallback)
    raise FileNotFoundError(f"No se encontró tabla RAG: {path_primary}")


def neighbors_by_hash(df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    """Agrupa vecinos por query_hash."""
    out: dict[str, list[dict[str, Any]]] = {}
    label_col = "neighbor_label" if "neighbor_label" in df.columns else "label"
    for qh, grp in df.groupby("query_hash", sort=False):
        rows = []
        for _, r in grp.sort_values("rank").iterrows():
            rows.append(
                {
                    "rank": int(r["rank"]),
                    "neighbor_hash": str(r.get("neighbor_hash", "")),
                    "label": str(r[label_col]),
                    "distance": float(r.get("distance", 1.0)),
                    "similarity": float(r.get("similarity", 0.0)),
                }
            )
        out[str(qh)] = rows
    return out


class RagPlugin:
    """Enriquece señales con métricas de recuperación RAG."""

    def __init__(self, neighbors_map: dict[str, list[dict[str, Any]]], conformal_qhat: float = 0.35):
        self.neighbors_map = neighbors_map
        self.conformal_qhat = conformal_qhat

    def enrich(self, text_hash: str, neighbors: list[dict[str, Any]] | None = None) -> dict[str, float | int]:
        ns = neighbors or self.neighbors_map.get(text_hash, [])
        labels = [str(n.get("label", n.get("neighbor_label", "pausa"))) for n in ns]
        distances = [float(n.get("distance", 1.0)) for n in ns]
        counts = Counter(labels)
        k = max(len(labels), 1)
        consensus = max(counts.values()) / k if counts else 0.0
        ent = _entropy(labels)
        mean_dist = float(sum(distances) / len(distances)) if distances else 1.0
        # Conformal-lite: clases con frecuencia relativa > qhat
        conformal_set = {lbl for lbl, c in counts.items() if c / k >= self.conformal_qhat}
        rag_unc = min(1.0, 0.5 * ent + 0.3 * mean_dist + 0.2 * (1.0 - consensus))
        return {
            "neighbor_entropy": ent,
            "mean_distance": mean_dist,
            "class_consensus": consensus,
            "conformal_set_size": len(conformal_set),
            "rag_uncertainty": rag_unc,
        }
