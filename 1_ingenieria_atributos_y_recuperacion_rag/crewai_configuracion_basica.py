"""
CrewAI básico — smoke test Var1 (PASO 2).

Dos agentes (Analyst + Reviewer), DeepSeek API, SIN ejecutar 400 tickets.
Uso:
  python crewai_configuracion_basica.py --dry-run
  python crewai_configuracion_basica.py --smoke
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PASO1 = Path(__file__).resolve().parent
PASO0 = PASO1.parent / "0_etl_ingesta_preprocesamiento"
DEFAULT_EVAL = PASO0 / "8_conjunto_evaluacion_experimento_n400.csv"
DEFAULT_NEIGHBORS = PASO1 / "3_tabla_vecinos_recuperados_top5.csv"


def load_sample_ticket(eval_csv: Path, neighbors_csv: Path, query_idx: int = 0) -> dict[str, Any]:
    import pandas as pd

    df_eval = pd.read_csv(eval_csv)
    row = df_eval.iloc[query_idx]
    neighbors: list[dict[str, Any]] = []
    if neighbors_csv.exists():
        df_n = pd.read_csv(neighbors_csv)
        qhash = str(row["text_hash"])
        sub = df_n[df_n["query_hash"].astype(str) == qhash].sort_values("rank")
        for _, n in sub.iterrows():
            neighbors.append(
                {
                    "rank": int(n["rank"]),
                    "label": str(n["neighbor_label"]),
                    "distance": float(n["distance"]),
                    "text": str(n.get("query_text", ""))[:120],
                }
            )
    return {
        "text": str(row["text"]),
        "true_label": str(row["thesis_class"]),
        "text_hash": str(row["text_hash"]),
        "neighbors": neighbors[:5],
    }


def format_neighbors_context(neighbors: list[dict[str, Any]]) -> str:
    if not neighbors:
        return "Sin vecinos RAG (ejecutar PASO 1 primero)."
    lines = []
    for n in neighbors:
        lines.append(f"  rank={n.get('rank')}: label={n.get('label')} dist={n.get('distance')}")
    return "\n".join(lines)


def run_dry_run(sample: dict[str, Any]) -> dict[str, Any]:
    majority = "pausa"
    labels = [n.get("label") for n in sample["neighbors"]]
    if labels:
        from collections import Counter

        majority = Counter(labels).most_common(1)[0][0]
    return {
        "mode": "dry-run",
        "ticket_hash": sample["text_hash"],
        "true_label": sample["true_label"],
        "simulated_analyst_label": majority,
        "simulated_reviewer_label": majority,
        "note": "Sin llamadas API. Ejecutar --smoke con DEEPSEEK_API_KEY para 1 ticket real.",
    }


def run_smoke(sample: dict[str, Any]) -> dict[str, Any]:
    from crewai_var1_entregable import run_crewai_var1

    out = run_crewai_var1(sample["text"], sample["neighbors"])
    return {
        "mode": "smoke",
        "ticket_hash": sample["text_hash"],
        "true_label": sample["true_label"],
        "parsed_label": out["label"],
        "confidence": out["confidence"],
        "analyst_label": out.get("analyst_label"),
        "reviewer_label": out.get("reviewer_label"),
        "latency_ms": out.get("latency_ms"),
        "tokens": out.get("tokens"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="CrewAI smoke test Var1")
    parser.add_argument("--dry-run", action="store_true", help="Sin API (default si no --smoke)")
    parser.add_argument("--smoke", action="store_true", help="1 llamada CrewAI real")
    parser.add_argument("--query-idx", type=int, default=0, help="Índice ticket en eval CSV")
    parser.add_argument("--eval-csv", type=Path, default=DEFAULT_EVAL)
    parser.add_argument("--neighbors-csv", type=Path, default=DEFAULT_NEIGHBORS)
    args = parser.parse_args()

    load_dotenv()
    load_dotenv(PASO1.parents[2] / ".env")

    if not args.eval_csv.exists():
        sys.exit(f"Falta eval CSV: {args.eval_csv}")

    sample = load_sample_ticket(args.eval_csv, args.neighbors_csv, args.query_idx)
    if args.smoke:
        out = run_smoke(sample)
    else:
        out = run_dry_run(sample)

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
