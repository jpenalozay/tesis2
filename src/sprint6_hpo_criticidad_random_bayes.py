"""
Sprint 7 — HPO Random vs Bayesian (Optuna TPE) para política criticidad Var2.

Optimiza hiperparámetros de la capa criticidad post-RAG sobre split fijo n=40
(seed=42), sin re-llamar LLM. Usa artefactos de sprint6_metagpt_multiagente_uni_n40.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
from optuna.pruners import MedianPruner
from optuna.samplers import RandomSampler, TPESampler
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.model_selection import StratifiedKFold

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.sprint6_colab_metagpt_vector_criticidad import (  # noqa: E402
    CLASSES,
    RunConfig,
    compute_metrics,
    load_bugsrepo_dataframe,
    make_stratified_eval,
    majority_label,
    objective,
    predict_robust,
    robust_features,
    run_cleaning_pipeline,
    sample_history_and_calibration,
)

DEFAULT_SPRINT6_DIR = PROJECT_ROOT / "docs/experiments/sprint6_metagpt_multiagente_uni_n40"
DEFAULT_OUT_DIR = PROJECT_ROOT / "docs/experiments/sprint7_hpo_random_bayes_criticidad_uni_n40"
SEED = 42
N_TRIALS = 80
N_CV_FOLDS = 5
TOP_K = 10

WEIGHT_KEYS = ("base", "risk", "p_stop", "uncertainty", "rag_gap", "fuzzy_stop")


@dataclass
class HPOConfig:
    seed: int = SEED
    n_trials: int = N_TRIALS
    n_cv_folds: int = N_CV_FOLDS
    sprint6_dir: str = str(DEFAULT_SPRINT6_DIR)
    out_dir: str = str(DEFAULT_OUT_DIR)
    top_k: int = TOP_K
    pruner_n_startup_trials: int = 10
    pruner_n_warmup_steps: int = 1
    pruner_interval_steps: int = 1


def setup_logger(out_dir: Path) -> logging.Logger:
    logger = logging.getLogger("sprint7_hpo")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = logging.FileHandler(out_dir / "hpo_run.log", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def build_search_space() -> dict[str, Any]:
    return {
        "description": "Hiperparámetros política criticidad Var2 (post-RAG, sin LLM)",
        "protocol": "Calibración train-only (n=600); eval final test n=40; seed=42",
        "objective": "F1-macro + α·F1-STOP − β·PolicyCost (modo stop_heavy o balanced)",
        "parameters": {
            "mode": {"type": "categorical", "choices": ["stop_heavy", "balanced"]},
            "w_base": {"type": "float", "low": 0.15, "high": 0.45},
            "w_risk": {"type": "float", "low": 0.12, "high": 0.38},
            "w_p_stop": {"type": "float", "low": 0.08, "high": 0.28},
            "w_uncertainty": {"type": "float", "low": 0.05, "high": 0.22},
            "w_rag_gap": {"type": "float", "low": 0.02, "high": 0.14},
            "w_fuzzy_stop": {"type": "float", "low": 0.06, "high": 0.22},
            "threshold_stop": {"type": "float", "low": 0.48, "high": 0.76, "step": 0.02},
            "threshold_pausa": {"type": "float", "low": 0.20, "high": 0.56, "step": 0.02},
            "risk_stop_floor": {"type": "float", "low": 0.16, "high": 0.48, "step": 0.04},
            "p_stop_floor": {"type": "float", "low": 0.36, "high": 0.64, "step": 0.04},
            "stop_cost_threshold": {"type": "float", "low": 0.30, "high": 0.54, "step": 0.02},
            "pause_uncertainty": {"type": "float", "low": 0.36, "high": 0.58, "step": 0.02},
        },
        "constraints": [
            "threshold_pausa < threshold_stop",
            "weights normalizados a suma=1",
        ],
        "baseline_sprint6": {
            "mode": "stop_heavy",
            "threshold_stop": 0.54,
            "threshold_pausa": 0.24,
            "risk_stop_floor": 0.2,
            "p_stop_floor": 0.4,
            "stop_cost_threshold": 0.38,
            "pause_uncertainty": 0.48,
            "weights": {
                "base": 0.34,
                "risk": 0.24,
                "p_stop": 0.14,
                "uncertainty": 0.1,
                "rag_gap": 0.06,
                "fuzzy_stop": 0.12,
            },
        },
    }


def neighbors_from_audit(audit_df: pd.DataFrame, query_hashes: list[str]) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in audit_df.sort_values(["query_hash", "rank"]).itertuples():
        grouped.setdefault(str(row.query_hash), []).append(
            {
                "text_hash": str(row.neighbor_hash),
                "label": str(row.neighbor_label),
                "distance": float(row.distance),
            }
        )
    return [grouped.get(str(h), []) for h in query_hashes]


def normalize_weights(raw: dict[str, float]) -> dict[str, float]:
    total = sum(raw.values())
    if total <= 0:
        return {k: 1.0 / len(WEIGHT_KEYS) for k in WEIGHT_KEYS}
    return {k: float(raw[k] / total) for k in WEIGHT_KEYS}


def suggest_params(trial: optuna.Trial) -> dict[str, Any]:
    mode = trial.suggest_categorical("mode", ["stop_heavy", "balanced"])
    raw = {
        "base": trial.suggest_float("w_base", 0.15, 0.45),
        "risk": trial.suggest_float("w_risk", 0.12, 0.38),
        "p_stop": trial.suggest_float("w_p_stop", 0.08, 0.28),
        "uncertainty": trial.suggest_float("w_uncertainty", 0.05, 0.22),
        "rag_gap": trial.suggest_float("w_rag_gap", 0.02, 0.14),
        "fuzzy_stop": trial.suggest_float("w_fuzzy_stop", 0.06, 0.22),
    }
    threshold_stop = trial.suggest_float("threshold_stop", 0.48, 0.76, step=0.02)
    threshold_pausa_hi = min(threshold_stop - 0.02, 0.56)
    threshold_pausa = trial.suggest_float("threshold_pausa", 0.20, max(0.22, threshold_pausa_hi), step=0.02)
    return {
        "weights": normalize_weights(raw),
        "threshold_stop": float(threshold_stop),
        "threshold_pausa": float(min(threshold_pausa, threshold_stop - 0.02)),
        "risk_stop_floor": float(trial.suggest_float("risk_stop_floor", 0.16, 0.48, step=0.04)),
        "p_stop_floor": float(trial.suggest_float("p_stop_floor", 0.36, 0.64, step=0.04)),
        "stop_cost_threshold": float(trial.suggest_float("stop_cost_threshold", 0.30, 0.54, step=0.02)),
        "pause_uncertainty": float(trial.suggest_float("pause_uncertainty", 0.36, 0.58, step=0.02)),
        "mode": mode,
    }


def predict_batch(features_list: list[dict[str, Any]], params: dict[str, Any]) -> list[str]:
    return [predict_robust(f, params)[0] for f in features_list]


def evaluate_fold(
    features: list[dict[str, Any]],
    y_true: list[str],
    params: dict[str, Any],
) -> dict[str, float]:
    preds = predict_batch(features, params)
    mode = params["mode"]
    return {
        "objective": objective(y_true, preds, mode),
        "f1_macro": float(f1_score(y_true, preds, labels=CLASSES, average="macro", zero_division=0)),
        "f1_stop": float(f1_score(y_true, preds, labels=CLASSES, average=None, zero_division=0)[2]),
        "accuracy": float(accuracy_score(y_true, preds)),
        "kappa": float(cohen_kappa_score(y_true, preds, labels=CLASSES)),
    }


def load_dataset(root: Path, sprint6_dir: Path, logger: logging.Logger) -> dict[str, Any]:
    summary_path = sprint6_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"No existe {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    run_cfg = RunConfig(**summary["config"])

    df_raw, _ = load_bugsrepo_dataframe(root)
    df_clean, _, _ = run_cleaning_pipeline(df_raw)
    df_eval, _ = make_stratified_eval(df_clean, run_cfg.target_n, run_cfg.seed)
    _, calibration, _, _ = sample_history_and_calibration(
        df_clean, df_eval, run_cfg.history_n, run_cfg.calibration_n, run_cfg.seed
    )

    audit_calib = pd.read_csv(sprint6_dir / "retrieval_audit_calibration.csv")
    audit_test = pd.read_csv(sprint6_dir / "retrieval_audit_test.csv")
    predictions = pd.read_csv(sprint6_dir / "predictions.csv")
    metagpt_preds = pd.read_csv(sprint6_dir / "metagpt_team_predictions.csv")

    neighbors_calib = neighbors_from_audit(audit_calib, calibration["text_hash"].astype(str).tolist())
    neighbors_test = neighbors_from_audit(audit_test, df_eval["text_hash"].astype(str).tolist())

    var1_llm = metagpt_preds[metagpt_preds["variant"] == "var1_metagpt_pgvector"].sort_values("idx")
    llm_by_hash = {
        str(r.text_hash): (str(r.label), float(r.confidence) if pd.notna(r.confidence) else None)
        for r in var1_llm.itertuples()
    }

    calib_features: list[dict[str, Any]] = []
    for row, ns in zip(calibration.itertuples(), neighbors_calib):
        base, _, _ = majority_label(ns)
        calib_features.append(robust_features(str(row.text), base, ns))

    test_features: list[dict[str, Any]] = []
    var1_preds = predictions["pred_var1"].astype(str).tolist()
    for pos, row in df_eval.reset_index(drop=True).iterrows():
        th = str(row["text_hash"])
        llm_label, llm_conf = llm_by_hash.get(th, (var1_preds[pos], None))
        test_features.append(
            robust_features(
                str(row["text"]),
                var1_preds[pos],
                neighbors_test[pos],
                llm_label=llm_label if llm_label in CLASSES else None,
                llm_confidence=llm_conf,
            )
        )

    y_calib = calibration["thesis_class"].astype(str).tolist()
    y_test = df_eval["thesis_class"].astype(str).tolist()
    baseline_params = summary["selected_var2_params"]
    baseline_metrics = summary["metric_by_model"][
        "Var2 Var1 + criticidad Camino B-lite (stop_heavy)"
    ]

    logger.info(
        "Dataset cargado: calib=%s test=%s baseline Var2 F1-Macro=%s PolicyCost=%s",
        len(calib_features),
        len(test_features),
        baseline_metrics["F1-Macro"],
        baseline_metrics["PolicyCost"],
    )
    return {
        "run_cfg": run_cfg,
        "summary": summary,
        "calib_features": calib_features,
        "test_features": test_features,
        "y_calib": y_calib,
        "y_test": y_test,
        "baseline_params": baseline_params,
        "baseline_metrics": baseline_metrics,
        "df_eval": df_eval,
    }


def make_objective(
    data: dict[str, Any],
    log_path: Path,
    method: str,
    cv: StratifiedKFold,
) -> Any:
    features = data["calib_features"]
    y_all = data["y_calib"]
    indices = np.arange(len(y_all))

    def _objective(trial: optuna.Trial) -> float:
        params = suggest_params(trial)
        fold_scores: list[float] = []
        for step, (train_idx, val_idx) in enumerate(cv.split(indices, y_all)):
            val_features = [features[i] for i in val_idx]
            val_y = [y_all[i] for i in val_idx]
            metrics = evaluate_fold(val_features, val_y, params)
            fold_scores.append(metrics["objective"])
            trial.report(metrics["objective"], step)
            if trial.should_prune():
                record = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "method": method,
                    "trial_number": trial.number,
                    "step": step,
                    "status": "pruned",
                    "objective": metrics["objective"],
                    "params": params,
                }
                with log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                raise optuna.TrialPruned()
        final_obj = float(np.mean(fold_scores))
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "trial_number": trial.number,
            "status": "complete",
            "objective_cv_mean": final_obj,
            "objective_cv_std": float(np.std(fold_scores)),
            "fold_objectives": fold_scores,
            "params": params,
        }
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return final_obj

    return _objective


def trials_to_dataframe(study: optuna.Study, method: str) -> pd.DataFrame:
    rows = []
    for t in study.trials:
        row: dict[str, Any] = {
            "method": method,
            "trial": t.number,
            "state": str(t.state),
            "objective_cv": t.value,
            "duration_s": (t.duration.total_seconds() if t.duration else None),
            "pruned": t.state == optuna.trial.TrialState.PRUNED,
        }
        for k, v in (t.params or {}).items():
            row[f"param_{k}"] = v
        rows.append(row)
    return pd.DataFrame(rows)


def best_so_far(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["state"] == "TrialState.COMPLETE"].copy()
    if completed.empty:
        return completed
    completed = completed.sort_values("trial")
    completed["best_so_far"] = completed["objective_cv"].cummax()
    return completed


def top_k_from_study(study: optuna.Study, data: dict[str, Any], k: int) -> pd.DataFrame:
    completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE and t.value is not None]
    completed.sort(key=lambda t: t.value, reverse=True)
    rows = []
    for rank, trial in enumerate(completed[:k], start=1):
        params = dict(trial.params)
        params["weights"] = normalize_weights(
            {
                "base": params.pop("w_base"),
                "risk": params.pop("w_risk"),
                "p_stop": params.pop("w_p_stop"),
                "uncertainty": params.pop("w_uncertainty"),
                "rag_gap": params.pop("w_rag_gap"),
                "fuzzy_stop": params.pop("w_fuzzy_stop"),
            }
        )
        full_params = {
            "weights": params["weights"],
            "threshold_stop": params["threshold_stop"],
            "threshold_pausa": params["threshold_pausa"],
            "risk_stop_floor": params["risk_stop_floor"],
            "p_stop_floor": params["p_stop_floor"],
            "stop_cost_threshold": params["stop_cost_threshold"],
            "pause_uncertainty": params["pause_uncertainty"],
            "mode": params["mode"],
        }
        preds = predict_batch(data["test_features"], full_params)
        test_metrics = compute_metrics(data["y_test"], preds, f"top{rank}", None)
        rows.append(
            {
                "rank": rank,
                "trial": trial.number,
                "objective_cv": trial.value,
                "test_f1_macro": test_metrics["F1-Macro"],
                "test_f1_stop": test_metrics["F1-STOP"],
                "test_accuracy": test_metrics["Accuracy"],
                "test_policy_cost": test_metrics["PolicyCost"],
                "params_json": json.dumps(full_params, ensure_ascii=False, sort_keys=True),
            }
        )
    return pd.DataFrame(rows)


def params_from_trial(trial: optuna.trial.FrozenTrial) -> dict[str, Any]:
    p = dict(trial.params)
    weights = normalize_weights(
        {
            "base": p["w_base"],
            "risk": p["w_risk"],
            "p_stop": p["w_p_stop"],
            "uncertainty": p["w_uncertainty"],
            "rag_gap": p["w_rag_gap"],
            "fuzzy_stop": p["w_fuzzy_stop"],
        }
    )
    return {
        "weights": weights,
        "threshold_stop": float(p["threshold_stop"]),
        "threshold_pausa": float(min(p["threshold_pausa"], p["threshold_stop"] - 0.02)),
        "risk_stop_floor": float(p["risk_stop_floor"]),
        "p_stop_floor": float(p["p_stop_floor"]),
        "stop_cost_threshold": float(p["stop_cost_threshold"]),
        "pause_uncertainty": float(p["pause_uncertainty"]),
        "mode": str(p["mode"]),
    }


def plot_evolution(random_df: pd.DataFrame, bayes_df: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, df, title in zip(
        axes,
        [random_df, bayes_df],
        ["Random Search + MedianPruner", "Bayesian TPE + MedianPruner"],
    ):
        comp = best_so_far(df)
        if len(comp):
            ax.plot(comp["trial"], comp["best_so_far"], marker="o", markersize=3, linewidth=1.5)
        pruned_n = int(df["pruned"].sum()) if "pruned" in df.columns else 0
        ax.set_title(f"{title}\n(pruned={pruned_n})")
        ax.set_xlabel("Trial")
        ax.set_ylabel("Best-so-far objective (CV)")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "evolution_best_so_far.png", dpi=140)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(8, 4.5))
    for df, label, color in [
        (random_df, "Random", "#1f77b4"),
        (bayes_df, "Bayes TPE", "#ff7f0e"),
    ]:
        comp = best_so_far(df)
        if len(comp):
            ax2.plot(comp["trial"], comp["best_so_far"], label=label, color=color, linewidth=1.8)
    ax2.set_title("Comparación Random vs Bayes (best-so-far)")
    ax2.set_xlabel("Trial")
    ax2.set_ylabel("Objective CV")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(out_dir / "figures" / "comparison_random_vs_bayes.png", dpi=140)
    plt.close(fig2)


def run_hpo(root: Path, cfg: HPOConfig) -> dict[str, Any]:
    out_dir = root / cfg.out_dir
    logs_dir = out_dir / "logs"
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(out_dir)
    sprint6_dir = root / cfg.sprint6_dir
    data = load_dataset(root, sprint6_dir, logger)

    search_space = build_search_space()
    (out_dir / "search_space.json").write_text(json.dumps(search_space, ensure_ascii=False, indent=2), encoding="utf-8")

    pruner = MedianPruner(
        n_startup_trials=cfg.pruner_n_startup_trials,
        n_warmup_steps=cfg.pruner_n_warmup_steps,
        interval_steps=cfg.pruner_interval_steps,
    )
    cv = StratifiedKFold(n_splits=cfg.n_cv_folds, shuffle=True, random_state=cfg.seed)

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    t0 = time.perf_counter()

    study_random = optuna.create_study(
        direction="maximize",
        sampler=RandomSampler(seed=cfg.seed),
        pruner=pruner,
        study_name="hpo_random_criticidad",
    )
    study_random.optimize(
        make_objective(data, logs_dir / "hpo_random.jsonl", "random", cv),
        n_trials=cfg.n_trials,
        show_progress_bar=False,
    )

    study_bayes = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=cfg.seed, n_startup_trials=cfg.pruner_n_startup_trials),
        pruner=pruner,
        study_name="hpo_bayes_criticidad",
    )
    study_bayes.optimize(
        make_objective(data, logs_dir / "hpo_bayes.jsonl", "bayes", cv),
        n_trials=cfg.n_trials,
        show_progress_bar=False,
    )

    elapsed_s = time.perf_counter() - t0
    random_df = trials_to_dataframe(study_random, "random")
    bayes_df = trials_to_dataframe(study_bayes, "bayes")
    random_df.to_csv(out_dir / "trials_random.csv", index=False)
    bayes_df.to_csv(out_dir / "trials_bayes.csv", index=False)

    top_random = top_k_from_study(study_random, data, cfg.top_k)
    top_bayes = top_k_from_study(study_bayes, data, cfg.top_k)
    top_random.to_csv(out_dir / "top_k_random.csv", index=False)
    top_bayes.to_csv(out_dir / "top_k_bayes.csv", index=False)

    best_random_trial = max(
        [t for t in study_random.trials if t.value is not None],
        key=lambda t: t.value,
    )
    best_bayes_trial = max(
        [t for t in study_bayes.trials if t.value is not None],
        key=lambda t: t.value,
    )
    best_random_test = compute_metrics(
        data["y_test"],
        predict_batch(data["test_features"], params_from_trial(best_random_trial)),
        "best_random_test",
    )
    best_bayes_test = compute_metrics(
        data["y_test"],
        predict_batch(data["test_features"], params_from_trial(best_bayes_trial)),
        "best_bayes_test",
    )

    candidates = [
        ("random", best_random_trial, best_random_test),
        ("bayes", best_bayes_trial, best_bayes_test),
    ]
    winner_name, winner_trial, winner_test = max(candidates, key=lambda x: x[2]["F1-Macro"])
    winning_params = params_from_trial(winner_trial)

    baseline_preds = predict_batch(data["test_features"], data["baseline_params"])
    baseline_test = compute_metrics(data["y_test"], baseline_preds, "sprint6_var2_baseline")

    budget_summary = {
        "n_trials_per_method": cfg.n_trials,
        "total_trials": cfg.n_trials * 2,
        "cv_folds": cfg.n_cv_folds,
        "pruner": "MedianPruner",
        "pruner_config": {
            "n_startup_trials": cfg.pruner_n_startup_trials,
            "n_warmup_steps": cfg.pruner_n_warmup_steps,
            "interval_steps": cfg.pruner_interval_steps,
        },
        "samplers": {"random": "RandomSampler", "bayes": "TPESampler"},
        "seed": cfg.seed,
        "elapsed_seconds": round(elapsed_s, 2),
        "random_completed": int((random_df["state"] == "TrialState.COMPLETE").sum()),
        "random_pruned": int(random_df["pruned"].sum()),
        "bayes_completed": int((bayes_df["state"] == "TrialState.COMPLETE").sum()),
        "bayes_pruned": int(bayes_df["pruned"].sum()),
        "no_llm_calls": True,
        "calibration_scope": "train-only n=600",
        "test_eval_n": len(data["y_test"]),
    }
    (out_dir / "budget_summary.json").write_text(json.dumps(budget_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    winning_config = {
        "selected_method": winner_name,
        "trial_number": winner_trial.number,
        "objective_cv": winner_trial.value,
        "params": winning_params,
        "test_metrics": winner_test,
        "baseline_sprint6_var2": {
            "params": data["baseline_params"],
            "test_metrics": baseline_test,
        },
        "improvement_vs_baseline": {
            "delta_f1_macro": round(winner_test["F1-Macro"] - baseline_test["F1-Macro"], 4),
            "delta_f1_stop": round(winner_test["F1-STOP"] - baseline_test["F1-STOP"], 4),
            "delta_policy_cost": round(winner_test["PolicyCost"] - baseline_test["PolicyCost"], 4),
            "delta_accuracy": round(winner_test["Accuracy"] - baseline_test["Accuracy"], 4),
        },
        "decision_rationale": (
            f"Se elige {winner_name} por mayor F1-Macro en test n=40 "
            f"({winner_test['F1-Macro']} vs baseline sprint6 {baseline_test['F1-Macro']}). "
            "HPO optimiza solo política criticidad post-RAG; no re-calibra MetaGPT/LLM."
        ),
    }
    (out_dir / "winning_config.json").write_text(json.dumps(winning_config, ensure_ascii=False, indent=2), encoding="utf-8")

    plot_evolution(random_df, bayes_df, out_dir)

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": "sprint7_hpo_random_bayes_criticidad_uni_n40",
        "sprint6_source": str(sprint6_dir),
        "out_dir": str(out_dir),
        "budget": budget_summary,
        "winning_config": winning_config,
        "best_random_cv": best_random_trial.value,
        "best_bayes_cv": best_bayes_trial.value,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("HPO completado en %.1fs. Ganador=%s F1-Macro test=%s", elapsed_s, winner_name, winner_test["F1-Macro"])
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sprint 7 HPO Random vs Bayes criticidad Var2")
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--n-trials", type=int, default=N_TRIALS)
    p.add_argument("--sprint6-dir", default=str(DEFAULT_SPRINT6_DIR))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cfg = HPOConfig(seed=args.seed, n_trials=args.n_trials, sprint6_dir=args.sprint6_dir, out_dir=args.out_dir)
    result = run_hpo(PROJECT_ROOT, cfg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
