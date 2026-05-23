#!/usr/bin/env python3
"""
Semana 6 — Entrega A/B criticidad (tesis2).

- Baseline + Var1 + Var2 (TF-IDF, un cambio por variante).
- Opcional: EarlyGate léxico (sin LLM).
- Holdout estratificado + GroupKFold por template_index (seed=42).
- Artefactos: docs/experiments/week6/ (+ reports/week6_<ts>/ opcional).

NO ejecuta EarlyGate con LLM por defecto.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    f1_score,
)
from sklearn.model_selection import GroupKFold, StratifiedShuffleSplit
from sklearn.pipeline import Pipeline

TESIS2_ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = TESIS2_ROOT / "data" / "criticidad_cases" / "casos_gold_criticidad_v2.jsonl"
OUT_DIR = TESIS2_ROOT / "docs" / "experiments" / "week6"
REPORTS_DIR = TESIS2_ROOT / "reports"

LABELS = ["play", "pausa", "stop"]


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    description: str
    kind: str  # "sklearn" | "lexical"
    vectorizer: dict[str, Any] | None = None
    classifier: dict[str, Any] | None = None


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
    assert cfg.vectorizer is not None and cfg.classifier is not None
    return Pipeline(
        [("tfidf", TfidfVectorizer(**cfg.vectorizer)), ("clf", LogisticRegression(**cfg.classifier))],
        memory=None,
    )


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0)),
        "kappa": float(cohen_kappa_score(y_true, y_pred, labels=LABELS)),
    }


def eval_holdout_sklearn(
    pipe: Pipeline,
    X: np.ndarray,
    y: np.ndarray,
    *,
    test_size: float,
    seed: int,
) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(X, y))
    t0 = time.perf_counter()
    pipe.fit(X[train_idx], y[train_idx])
    yhat = pipe.predict(X[test_idx])
    elapsed = time.perf_counter() - t0
    m = _metrics(y[test_idx], yhat)
    m["elapsed_sec"] = float(elapsed)
    return m, y[test_idx], yhat


def eval_groupkfold_sklearn(
    pipe_factory: Callable[[], Pipeline],
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    *,
    n_splits: int,
) -> dict[str, float]:
    gkf = GroupKFold(n_splits=n_splits)
    accs: list[float] = []
    f1s: list[float] = []
    kappas: list[float] = []
    t0 = time.perf_counter()
    for train_idx, test_idx in gkf.split(X, y, groups=groups):
        pipe = pipe_factory()
        pipe.fit(X[train_idx], y[train_idx])
        yhat = pipe.predict(X[test_idx])
        accs.append(float(accuracy_score(y[test_idx], yhat)))
        f1s.append(
            float(f1_score(y[test_idx], yhat, labels=LABELS, average="macro", zero_division=0))
        )
        kappas.append(float(cohen_kappa_score(y[test_idx], yhat, labels=LABELS)))
    elapsed = time.perf_counter() - t0
    return {
        "accuracy_mean": float(np.mean(accs)),
        "f1_macro_mean": float(np.mean(f1s)),
        "f1_macro_std": float(np.std(f1s)),
        "kappa_mean": float(np.mean(kappas)),
        "kappa_std": float(np.std(kappas)),
        "elapsed_sec": float(elapsed),
    }


def eval_holdout_lexical(
    X: np.ndarray,
    y: np.ndarray,
    predict_fn: Callable[[str], str],
    *,
    test_size: float,
    seed: int,
) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(X, y))
    del train_idx  # sin entrenamiento
    t0 = time.perf_counter()
    yhat = np.array([predict_fn(str(t)) for t in X[test_idx]])
    elapsed = time.perf_counter() - t0
    m = _metrics(y[test_idx], yhat)
    m["elapsed_sec"] = float(elapsed)
    return m, y[test_idx], yhat


def eval_groupkfold_lexical(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    predict_fn: Callable[[str], str],
    *,
    n_splits: int,
) -> dict[str, float]:
    gkf = GroupKFold(n_splits=n_splits)
    f1s: list[float] = []
    kappas: list[float] = []
    accs: list[float] = []
    t0 = time.perf_counter()
    for _, test_idx in gkf.split(X, y, groups=groups):
        yhat = np.array([predict_fn(str(t)) for t in X[test_idx]])
        accs.append(float(accuracy_score(y[test_idx], yhat)))
        f1s.append(
            float(f1_score(y[test_idx], yhat, labels=LABELS, average="macro", zero_division=0))
        )
        kappas.append(float(cohen_kappa_score(y[test_idx], yhat, labels=LABELS)))
    elapsed = time.perf_counter() - t0
    return {
        "accuracy_mean": float(np.mean(accs)),
        "f1_macro_mean": float(np.mean(f1s)),
        "f1_macro_std": float(np.std(f1s)),
        "kappa_mean": float(np.mean(kappas)),
        "kappa_std": float(np.std(kappas)),
        "elapsed_sec": float(elapsed),
    }


def f1_per_class(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    for lab in LABELS:
        out[lab] = float(
            f1_score(
                y_true == lab,
                y_pred == lab,
                average="binary",
                zero_division=0,
            )
        )
    return out


def cost_label(name: str, elapsed_holdout: float) -> str:
    if name == "early_lexical":
        return f"API 0 · ~{elapsed_holdout:.2f}s holdout (reglas)"
    if name.startswith("early_llm"):
        return "API LLM · alta latencia/coste"
    return f"API 0 · ~{elapsed_holdout:.2f}s holdout (sklearn)"


def plot_f1_per_class(
    f1_baseline: dict[str, float],
    f1_best: dict[str, float],
    best_name: str,
    out_path: Path,
) -> None:
    x = np.arange(len(LABELS))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(
        x - w / 2,
        [f1_baseline[c] for c in LABELS],
        width=w,
        label="baseline",
        color="#4C72B0",
    )
    ax.bar(
        x + w / 2,
        [f1_best[c] for c in LABELS],
        width=w,
        label=best_name,
        color="#55A868",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("F1 (binario por clase)")
    ax.set_title("Semana 6 — F1 por clase (holdout)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def build_experiments(seed: int) -> list[ExperimentConfig]:
    base_clf = {"solver": "lbfgs", "max_iter": 2000, "random_state": seed}
    return [
        ExperimentConfig(
            name="baseline",
            description="TF-IDF word (1,1) + LogisticRegression.",
            kind="sklearn",
            vectorizer={"analyzer": "word", "ngram_range": (1, 1), "min_df": 1},
            classifier=base_clf,
        ),
        ExperimentConfig(
            name="var1",
            description="Cambio único: TF-IDF word (1,2).",
            kind="sklearn",
            vectorizer={"analyzer": "word", "ngram_range": (1, 2), "min_df": 1},
            classifier=base_clf,
        ),
        ExperimentConfig(
            name="var2",
            description="Cambio único: TF-IDF char (3,5).",
            kind="sklearn",
            vectorizer={"analyzer": "char", "ngram_range": (3, 5), "min_df": 1},
            classifier=base_clf,
        ),
        ExperimentConfig(
            name="early_lexical",
            description="EarlyGate.lexical_classify (reglas, sin LLM).",
            kind="lexical",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--group-k", type=int, default=5)
    parser.add_argument("--no-lexical", action="store_true", help="Omitir fila early_lexical")
    parser.add_argument("--copy-to-reports", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_jsonl(CASES_FILE)
    X = df["requirement"].astype(str).to_numpy()
    y = df["gold_mode"].astype(str).to_numpy()
    groups = df["template_index"].fillna(-1).astype(int).to_numpy()

    import importlib.util

    eg_path = TESIS2_ROOT / "agentes" / "core" / "early_gate.py"
    spec = importlib.util.spec_from_file_location("early_gate_standalone", eg_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar {eg_path}")
    eg_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eg_mod)
    gate = eg_mod.EarlyGate()
    lexical_predict = lambda t: gate.lexical_classify(t)[0]

    experiments = build_experiments(args.seed)
    if args.no_lexical:
        experiments = [e for e in experiments if e.name != "early_lexical"]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rows: list[dict[str, Any]] = []
    holdout_preds: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for cfg in experiments:
        if cfg.kind == "sklearn":
            pipe = make_pipeline(cfg)
            hold, y_te, y_pr = eval_holdout_sklearn(
                pipe, X, y, test_size=args.test_size, seed=args.seed
            )
            gcv = eval_groupkfold_sklearn(
                lambda c=cfg: make_pipeline(c), X, y, groups, n_splits=args.group_k
            )
        else:
            hold, y_te, y_pr = eval_holdout_lexical(
                X, y, lexical_predict, test_size=args.test_size, seed=args.seed
            )
            gcv = eval_groupkfold_lexical(
                X, y, groups, lexical_predict, n_splits=args.group_k
            )

        holdout_preds[cfg.name] = (y_te, y_pr)
        rows.append(
            {
                "variante": cfg.name,
                "descripcion": cfg.description,
                "holdout_f1_macro": hold["f1_macro"],
                "holdout_accuracy": hold["accuracy"],
                "holdout_kappa": hold["kappa"],
                "holdout_elapsed_sec": hold["elapsed_sec"],
                "gkf_f1_macro_mean": gcv["f1_macro_mean"],
                "gkf_f1_macro_std": gcv["f1_macro_std"],
                "gkf_kappa_mean": gcv["kappa_mean"],
                "gkf_accuracy_mean": gcv["accuracy_mean"],
                "gkf_elapsed_sec": gcv["elapsed_sec"],
                "coste_latencia": cost_label(cfg.name, hold["elapsed_sec"]),
                "experiment": asdict(cfg),
                "metrics_raw": {"holdout": hold, "group_kfold": gcv},
            }
        )

    df_table = pd.DataFrame(rows).sort_values("variante")
    df_table.to_csv(OUT_DIR / "results.csv", index=False)

    # Ganadora por F1-macro GKF (referencia anti-leakage plantilla)
    ml_rows = df_table[df_table["variante"].isin(["baseline", "var1", "var2"])]
    best_row = ml_rows.loc[ml_rows["gkf_f1_macro_mean"].idxmax()]
    best_name = str(best_row["variante"])

    y_te_b, y_pr_b = holdout_preds["baseline"]
    y_te_w, y_pr_w = holdout_preds[best_name]
    f1_baseline = f1_per_class(y_te_b, y_pr_b)
    f1_best = f1_per_class(y_te_w, y_pr_w)

    fig_path = OUT_DIR / "f1_por_clase_baseline_vs_mejor.png"
    plot_f1_per_class(f1_baseline, f1_best, best_name, fig_path)

    summary = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "dataset": str(CASES_FILE.relative_to(TESIS2_ROOT)),
        "n_samples": int(len(df)),
        "seed": args.seed,
        "test_size": args.test_size,
        "group_kfold": {"k": args.group_k, "group": "template_index"},
        "metricas_centrales": ["f1_macro", "cohen_kappa"],
        "variante_recomendada": best_name,
        "razon": (
            f"Mayor F1-macro en GroupKFold por plantilla ({best_row['gkf_f1_macro_mean']:.4f} "
            f"± {best_row['gkf_f1_macro_std']:.4f}); coste API 0."
        ),
        "f1_por_clase_holdout": {"baseline": f1_baseline, best_name: f1_best},
        "tabla": df_table[
            [
                "variante",
                "holdout_f1_macro",
                "gkf_f1_macro_mean",
                "holdout_accuracy",
                "holdout_kappa",
                "gkf_kappa_mean",
                "coste_latencia",
            ]
        ].to_dict(orient="records"),
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if args.copy_to_reports:
        stamp_dir = REPORTS_DIR / f"week6_{run_id}"
        stamp_dir.mkdir(parents=True, exist_ok=True)
        df_table.to_csv(stamp_dir / "results.csv", index=False)
        (stamp_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        import shutil

        shutil.copy(fig_path, stamp_dir / fig_path.name)

    print("OK — semana 6 (tesis2):")
    print(" -", OUT_DIR / "results.csv")
    print(" -", OUT_DIR / "summary.json")
    print(" -", fig_path)
    print(f"Variante recomendada (GKF): {best_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
