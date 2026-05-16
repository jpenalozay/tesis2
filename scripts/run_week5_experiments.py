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
            description="TF-IDF word unigrams + LogisticRegression (multiclase, solver=lbfgs).",
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

    # Gráfico clave: F1-macro (holdout y media GKF ± desv. estándar entre folds)
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(df_table))
    w = 0.36
    ax.bar(
        x - 0.18,
        df_table["holdout_f1_macro"],
        width=w,
        label="Holdout F1-macro",
        color="#4C72B0",
    )
    ax.bar(
        x + 0.18,
        df_table["gkf_f1_macro_mean"],
        width=w,
        yerr=df_table["gkf_f1_macro_std"],
        capsize=4,
        label="GroupKFold F1-macro (media ± σ)",
        color="#55A868",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(df_table["exp"].tolist())
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("F1-macro")
    ax.set_title("Semana 5 — Baseline vs Var1/Var2 (criticidad)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    fig_path = OUT_DIR / "comparison_f1_macro.png"
    plt.savefig(fig_path, dpi=150)
    plt.close(fig)

    # Resumen en Markdown (legible para entrega; métricas redondeadas en tabla)
    n_samples = int(len(df))
    md_table = df_table.copy()
    num_cols = [c for c in md_table.columns if c != "exp"]
    md_table[num_cols] = md_table[num_cols].round(4)

    md: list[str] = []
    md.append("# Semana 5 — Experimentos A/B vs baseline\n")
    md.append("## Objetivo y diseño\n")
    md.append(
        "Clasificar el modo de criticidad (`gold_mode`: play / pausa / stop) a partir del texto "
        "del campo `requirement`, con un **baseline ML** (sin LLM) y **dos variantes** que cambian "
        "**solo** la representación TF-IDF frente al baseline, para comparación controlada.\n"
    )
    md.append(
        "- **Baseline:** TF-IDF *word* unigramas + `LogisticRegression`.\n"
        "- **Var1:** único cambio → TF-IDF *word* n-gramas (1, 2).\n"
        "- **Var2:** único cambio → TF-IDF *char* n-gramas (3, 5).\n"
    )
    md.append(
        f"- **Clasificador (igual en los tres):** `solver=lbfgs`, `max_iter=2000`, `random_state={args.seed}`.\n"
    )
    md.append("\n## Metadatos de la corrida\n")
    md.append(f"- **Run id:** `{run_id}`\n")
    md.append(f"- **Dataset:** `{CASES_FILE.relative_to(REPO_ROOT).as_posix()}` (`n={n_samples}`)\n")
    md.append("\n## Validación\n")
    md.append(
        f"- **Holdout:** `StratifiedShuffleSplit` (un split), `test_size={args.test_size}`, `random_state={args.seed}` "
        "(estratificado por `gold_mode`).\n"
    )
    md.append(
        f"- **CV por grupos:** `GroupKFold(n_splits={args.group_k})` con `groups=template_index` "
        "(ningún fold mezcla la misma plantilla entre train y test).\n"
    )
    md.append(
        "- **Métrica principal:** F1-macro (multiclase). **Secundarias:** accuracy y tiempo de ajuste+predicción "
        "en holdout / tiempo total en los k folds para GKF.\n"
    )
    md.append("\n## Tabla comparable\n")
    md.append(md_table.to_markdown(index=False))
    md.append("\n\n## Lectura de resultados\n")
    md.append(
        "- El **holdout** puede mostrar **F1-macro = 1.0** con un test pequeño y un problema relativamente "
        "separable; no implica ausencia de error en generalización.\n"
    )
    md.append(
        "- La evaluación **GroupKFold por plantilla** es la referencia más conservadora frente a **fuga por "
        "plantilla** (misma estructura de caso en train y test). Ahí se observa variación entre folds "
        "(barras de error en el gráfico).\n"
    )
    md.append(
        "- **Coste/tiempo:** Var2 (char n-grams) aumenta claramente el tiempo frente a Var1 y baseline; "
        "el trade-off conveniencia vs. ganancia marginal en F1 depende del despliegue.\n"
    )
    md.append("\n## Gráfico clave\n")
    md.append(
        f"- Archivo: `{fig_path.relative_to(REPO_ROOT).as_posix()}` (F1-macro holdout vs media GKF con σ).\n"
    )
    md.append("\n## Feature set y pipeline (auditoría de leakage)\n")
    md.append("- **Features:** solo texto `requirement`.\n")
    md.append("- **Transformación:** `TfidfVectorizer` (word o char; rango de n-gramas según experimento). `min_df=1`.\n")
    md.append(
        "- **Sin leakage por ajuste del vectorizador:** el vectorizador vive dentro de un `Pipeline` de sklearn; "
        "en cada split se llama a `fit` solo con filas de entrenamiento.\n"
    )
    md.append(
        "- **Etiqueta y agrupación:** `y = gold_mode`; grupos para GKF = `template_index` (relleno -1 si falta).\n"
    )
    md.append("\n## Logs reproducibles\n")
    md.append(
        f"- `{log_path.relative_to(REPO_ROOT).as_posix()}` — una línea JSON por experimento (config + métricas).\n"
    )
    (OUT_DIR / "week5_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("OK — semana 5 artefactos generados:")
    print(" -", (OUT_DIR / "results.csv").relative_to(REPO_ROOT))
    print(" -", (OUT_DIR / "week5_report.md").relative_to(REPO_ROOT))
    print(" -", fig_path.relative_to(REPO_ROOT))
    print(" -", log_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

