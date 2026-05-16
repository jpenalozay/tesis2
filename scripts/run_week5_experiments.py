#!/usr/bin/env python3
"""
Semana 5 — Experimentos A/B vs baseline (clasificación textual).

Este script implementa:
- Baseline + Var1 + Var2 (un cambio por variante).
- Validación: holdout estratificado y GroupKFold por template_index.
- Tabla comparable y 1 gráfico clave.
- Logs reproducibles (parámetros + métricas + tiempo).

NO usa LLM (costo 0). Trabaja sobre el corpus gold:
  data/criticidad_cases/casos_gold_criticidad_v2.jsonl
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold, StratifiedShuffleSplit
from sklearn.pipeline import Pipeline


REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = REPO_ROOT / "data" / "criticidad_cases" / "casos_gold_criticidad_v2.jsonl"
OUT_DIR = REPO_ROOT / "docs" / "experiments" / "week5"
LOGS_DIR = REPO_ROOT / "logs" / "week5"

LABELS = ["play", "pausa", "stop"]


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    description: str
    vectorizer: dict[str, Any]
    classifier: dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    if "template_index" not in df.columns:
        df["template_index"] = -1
    return df


def make_pipeline(cfg: ExperimentConfig) -> Pipeline:
    vec = TfidfVectorizer(**cfg.vectorizer)
    clf = LogisticRegression(**cfg.classifier)
    # Nota: memory=None explícito para evitar warning de algunos linters.
    return Pipeline([("tfidf", vec), ("clf", clf)], memory=None)


def eval_holdout(
    pipe: Pipeline,
    X: np.ndarray,
    y: np.ndarray,
    *,
    test_size: float,
    seed: int,
) -> dict[str, float]:
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    (train_idx, test_idx) = next(sss.split(X, y))
    t0 = time.perf_counter()
    pipe.fit(X[train_idx], y[train_idx])
    yhat = pipe.predict(X[test_idx])
    elapsed = time.perf_counter() - t0
    return {
        "accuracy": float(accuracy_score(y[test_idx], yhat)),
        "f1_macro": float(f1_score(y[test_idx], yhat, labels=LABELS, average="macro")),
        "elapsed_sec": float(elapsed),
    }


def eval_groupkfold(
    pipe_factory,
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    *,
    n_splits: int,
) -> dict[str, float]:
    gkf = GroupKFold(n_splits=n_splits)
    accs: list[float] = []
    f1s: list[float] = []
    t0 = time.perf_counter()
    for train_idx, test_idx in gkf.split(X, y, groups=groups):
        pipe = pipe_factory()
        pipe.fit(X[train_idx], y[train_idx])
        yhat = pipe.predict(X[test_idx])
        accs.append(float(accuracy_score(y[test_idx], yhat)))
        f1s.append(float(f1_score(y[test_idx], yhat, labels=LABELS, average="macro")))
    elapsed = time.perf_counter() - t0
    return {
        "accuracy_mean": float(np.mean(accs)),
        "accuracy_std": float(np.std(accs)),
        "f1_macro_mean": float(np.mean(f1s)),
        "f1_macro_std": float(np.std(f1s)),
        "elapsed_sec": float(elapsed),
    }


def log_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--group-k", type=int, default=5)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_jsonl(CASES_FILE)
    # Feature set (explícito para la entrega): texto del requirement.
    X = df["requirement"].astype(str).to_numpy()
    y = df["gold_mode"].astype(str).to_numpy()
    groups = df["template_index"].fillna(-1).astype(int).to_numpy()

    # Baseline + 2 variantes (un cambio por vez)
    # Config estable:
    # - lbfgs soporta multiclase de forma nativa.
    # - no fijamos `multi_class` para evitar warnings deprecados (sklearn >=1.5).
    base_clf = {
        "solver": "lbfgs",
        "max_iter": 2000,
        "random_state": args.seed,
    }

    experiments: list[ExperimentConfig] = [
        ExperimentConfig(
            name="baseline",
            description="TF-IDF word unigrams + LogisticRegression (ovr).",
            vectorizer={"analyzer": "word", "ngram_range": (1, 1), "min_df": 1},
            classifier=base_clf,
        ),
        ExperimentConfig(
            name="var1",
            description="Cambio único: TF-IDF word (1,2) bigrams habilitados.",
            vectorizer={"analyzer": "word", "ngram_range": (1, 2), "min_df": 1},
            classifier=base_clf,
        ),
        ExperimentConfig(
            name="var2",
            description="Cambio único: TF-IDF char (3,5) n-gramas de caracteres.",
            vectorizer={"analyzer": "char", "ngram_range": (3, 5), "min_df": 1},
            classifier=base_clf,
        ),
    ]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"week5_experiments_{run_id}.jsonl"

    rows: list[dict[str, Any]] = []
    for cfg in experiments:
        pipe = make_pipeline(cfg)
        hold = eval_holdout(pipe, X, y, test_size=args.test_size, seed=args.seed)
        # Evitar captura tardía de `cfg` en lambdas (linters / claridad)
        gcv = eval_groupkfold(
            lambda cfg_=cfg: make_pipeline(cfg_),
            X,
            y,
            groups,
            n_splits=args.group_k,
        )

        row = {
            "run_id": run_id,
            "timestamp_utc": _utc_now(),
            "dataset": str(CASES_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
            "n_samples": int(len(df)),
            "split": {
                "holdout": {"test_size": args.test_size, "seed": args.seed},
                "group_kfold": {"k": args.group_k, "group": "template_index"},
            },
            "experiment": asdict(cfg),
            "metrics": {"holdout": hold, "group_kfold": gcv},
        }
        rows.append(row)
        log_event(log_path, row)

    # Tabla comparable (Baseline/Var1/Var2)
    table = []
    for r in rows:
        table.append(
            {
                "exp": r["experiment"]["name"],
                "holdout_f1_macro": r["metrics"]["holdout"]["f1_macro"],
                "holdout_accuracy": r["metrics"]["holdout"]["accuracy"],
                "holdout_time_sec": r["metrics"]["holdout"]["elapsed_sec"],
                "gkf_f1_macro_mean": r["metrics"]["group_kfold"]["f1_macro_mean"],
                "gkf_f1_macro_std": r["metrics"]["group_kfold"]["f1_macro_std"],
                "gkf_accuracy_mean": r["metrics"]["group_kfold"]["accuracy_mean"],
                "gkf_time_sec": r["metrics"]["group_kfold"]["elapsed_sec"],
            }
        )
    df_table = pd.DataFrame(table).sort_values("exp")
    df_table.to_csv(OUT_DIR / "results.csv", index=False)

    # Gráfico clave: F1-macro (holdout y group-kfold)
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    x = np.arange(len(df_table))
    ax.bar(x - 0.18, df_table["holdout_f1_macro"], width=0.36, label="Holdout F1-macro")
    ax.bar(x + 0.18, df_table["gkf_f1_macro_mean"], width=0.36, label="GroupKFold F1-macro (mean)")
    ax.set_xticks(x)
    ax.set_xticklabels(df_table["exp"].tolist())
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1-macro")
    ax.set_title("Semana 5 — Baseline vs Var1/Var2 (criticidad)")
    ax.legend()
    plt.tight_layout()
    fig_path = OUT_DIR / "comparison_f1_macro.png"
    plt.savefig(fig_path, dpi=150)
    plt.close(fig)

    # Resumen en Markdown
    md = []
    md.append("# Semana 5 — Experimentos A/B vs baseline\n")
    md.append(f"- **Run id:** `{run_id}`\n")
    md.append(f"- **Dataset:** `{CASES_FILE.relative_to(REPO_ROOT).as_posix()}`\n")
    md.append(f"- **Holdout:** test_size={args.test_size}, seed={args.seed}\n")
    md.append(f"- **Cross-validation:** GroupKFold(k={args.group_k}) por `template_index` (reduce leakage por plantilla)\n")
    md.append("\n## Tabla comparable\n")
    md.append(df_table.to_markdown(index=False))
    md.append("\n\n## Gráfico clave\n")
    md.append(f"- `{fig_path.relative_to(REPO_ROOT).as_posix()}`\n")
    md.append("\n## Feature set y split (auditoría)\n")
    md.append("- **Features usadas:** `requirement` (texto). TF-IDF según variante.\n")
    md.append("- **Transformaciones:** tokenización TF-IDF (word o char n-grams). `fit` solo en train por construcción del pipeline.\n")
    md.append("- **Split/leakage:** además de holdout estratificado, se reporta GroupKFold por `template_index` para evitar que la misma plantilla aparezca en train y test.\n")
    md.append("\n## Logs\n")
    md.append(f"- `{log_path.relative_to(REPO_ROOT).as_posix()}` (una línea JSON por experimento)\n")
    (OUT_DIR / "week5_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("OK — semana 5 artefactos generados:")
    print(" -", (OUT_DIR / "results.csv").relative_to(REPO_ROOT))
    print(" -", (OUT_DIR / "week5_report.md").relative_to(REPO_ROOT))
    print(" -", fig_path.relative_to(REPO_ROOT))
    print(" -", log_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

