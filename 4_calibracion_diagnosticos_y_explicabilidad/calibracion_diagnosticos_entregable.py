"""
PASO 4 — Calibración post-hoc, ablación middleware, explicabilidad señales.

Lee predicciones cacheadas PASO 3 (sin re-API). IA06 entregable parcial3.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parent
PASO3 = ROOT.parent / "3_protocolo_experimental_variantes"
if str(PASO3) not in sys.path:
    sys.path.insert(0, str(PASO3))

from metricas_protocolo_entregable import compute_ece, compute_metrics_bundle  # noqa: E402


def load_config(path: Path | None = None) -> dict[str, Any]:
    p = path or ROOT / "0_configuracion_calibracion_diagnosticos.yaml"
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(rel: str, base: Path = ROOT) -> Path:
    return (base / rel).resolve()


def compute_brier(y_true: list[str], y_pred: list[str], confidences: list[float]) -> float:
    correct = [1.0 if yt == yp else 0.0 for yt, yp in zip(y_true, y_pred)]
    return float(np.mean([(c - corr) ** 2 for c, corr in zip(confidences, correct)]))


def _recompute_risk_from_dims(dims: dict[str, float]) -> float:
    raw = (
        0.30 * dims.get("I_db", 0.0)
        + 0.15 * dims.get("I_mem", 0.0)
        + 0.30 * dims.get("I_sec", 0.0)
        + 0.25 * dims.get("I_dat", 0.0)
        + 0.35 * dims.get("I_ctx_stop", 0.0)
        + 0.18 * dims.get("I_ctx_pause", 0.0)
    )
    return float(min(max(raw, 0.0), 1.0))


def apply_ablation_to_features(features: dict[str, Any], ablation: str) -> dict[str, Any]:
    f = deepcopy(features)
    if ablation == "sin_fuzzy":
        f["fuzzy_stop"] = 0.0
    elif ablation == "sin_senal_rag":
        f["rag_similarity"] = 1.0
        f["uncertainty"] = max(0.0, float(f.get("uncertainty", 0.0)) * 0.25)
        f["neighbor_entropy"] = 0.0
    elif ablation.startswith("sin_eje_"):
        axis = ablation.replace("sin_eje_", "I_")
        dims = dict(f.get("dims_4d") or {})
        if axis in dims:
            dims[axis] = 0.0
            f["dims_4d"] = dims
            f["risk_4d"] = _recompute_risk_from_dims(dims)
            sec_dat = max(dims.get("I_sec", 0.0), dims.get("I_dat", 0.0))
            f["fuzzy_stop"] = max(
                f["risk_4d"] if f["risk_4d"] >= 0.68 else 0.0,
                sec_dat if sec_dat >= 0.78 else 0.0,
                f.get("p_stop", 0.0),
            )
    return f


def fit_isotonic_calibrator(confidences: np.ndarray, correct: np.ndarray) -> IsotonicRegression:
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(confidences, correct)
    return iso


def fit_platt_calibrator(confidences: np.ndarray, correct: np.ndarray) -> LogisticRegression:
    lr = LogisticRegression(max_iter=1000)
    lr.fit(confidences.reshape(-1, 1), correct)
    return lr


def apply_calibrator(confidences: list[float], calibrator: Any, method: str) -> list[float]:
    arr = np.array(confidences, dtype=float)
    if method == "isotonic":
        out = calibrator.predict(arr)
    else:
        out = calibrator.predict_proba(arr.reshape(-1, 1))[:, 1]
    return [float(min(max(c, 0.0), 1.0)) for c in out]


def calibration_table_row(
    variant: str,
    phase: str,
    method: str,
    y_true: list[str],
    y_pred: list[str],
    confidences: list[float],
    n_bins: int,
    alcance: str,
) -> dict[str, Any]:
    ece = compute_ece(y_true, confidences, y_pred, n_bins=n_bins)
    brier = compute_brier(y_true, y_pred, confidences)
    acc = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / max(len(y_true), 1)
    return {
        "variante": variant,
        "fase": phase,
        "metodo_calibracion": method,
        "alcance": alcance,
        "n": len(y_true),
        "accuracy": round(acc, 6),
        "ECE": round(ece, 6),
        "Brier": round(brier, 6),
        "confianza_media": round(float(np.mean(confidences)), 6),
    }


def run_posthoc_calibration(
    preds: dict[str, pd.DataFrame],
    train_hashes: set[str],
    holdout_hashes: set[str],
    n_bins: int = 10,
) -> tuple[pd.DataFrame, dict[str, dict[str, list[float]]]]:
    rows: list[dict[str, Any]] = []
    calibrated: dict[str, dict[str, list[float]]] = {}

    for variant, df in preds.items():
        y_true = df["true_label"].astype(str).tolist()
        y_pred = df["pred_label"].astype(str).tolist()
        conf = df["confidence"].astype(float).tolist()
        rows.append(calibration_table_row(variant, "antes", "ninguno", y_true, y_pred, conf, n_bins, "n400"))

        train_mask = df["text_hash"].astype(str).isin(train_hashes)
        tr_conf = df.loc[train_mask, "confidence"].astype(float).values
        tr_correct = (
            df.loc[train_mask, "true_label"].astype(str) == df.loc[train_mask, "pred_label"].astype(str)
        ).astype(float).values

        if len(tr_conf) < 10:
            continue

        iso = fit_isotonic_calibrator(tr_conf, tr_correct)
        conf_iso = apply_calibrator(conf, iso, "isotonic")
        calibrated[variant] = {"isotonic": conf_iso}
        rows.append(calibration_table_row(variant, "despues", "isotonic", y_true, y_pred, conf_iso, n_bins, "n400"))

        platt = fit_platt_calibrator(tr_conf, tr_correct)
        conf_platt = apply_calibrator(conf, platt, "platt")
        calibrated[variant]["platt"] = conf_platt
        rows.append(calibration_table_row(variant, "despues", "platt", y_true, y_pred, conf_platt, n_bins, "n400"))

        ho_mask = df["text_hash"].astype(str).isin(holdout_hashes)
        if ho_mask.any():
            ho = df.loc[ho_mask]
            yt_h = ho["true_label"].astype(str).tolist()
            yp_h = ho["pred_label"].astype(str).tolist()
            c0 = ho["confidence"].astype(float).tolist()
            c1 = apply_calibrator(c0, iso, "isotonic")
            rows.append(calibration_table_row(variant, "antes", "ninguno", yt_h, yp_h, c0, n_bins, "holdout120"))
            rows.append(calibration_table_row(variant, "despues", "isotonic", yt_h, yp_h, c1, n_bins, "holdout120"))

    return pd.DataFrame(rows), calibrated


def plot_calibration_curves_three_variants(
    preds: dict[str, pd.DataFrame],
    calibrated: dict[str, dict[str, list[float]]],
    out_path: Path,
    n_bins: int = 10,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    colors = {"Baseline": "#7f8c8d", "Var1": "#3498db", "Var2": "#e74c3c"}

    for ax, (variant, df) in zip(axes, preds.items()):
        y_true = df["true_label"].astype(str).tolist()
        y_pred = df["pred_label"].astype(str).tolist()
        conf_before = df["confidence"].astype(float).tolist()
        conf_after = calibrated.get(variant, {}).get("isotonic", conf_before)

        for conf, style, label_suffix in [
            (conf_before, "-", "antes"),
            (conf_after, "--", "isotónica"),
        ]:
            correct = [1.0 if yt == yp else 0.0 for yt, yp in zip(y_true, y_pred)]
            bins = np.linspace(0, 1, n_bins + 1)
            bin_conf, bin_acc = [], []
            for i in range(n_bins):
                lo, hi = bins[i], bins[i + 1]
                mask = [(lo <= c < hi) if i < n_bins - 1 else (lo <= c <= hi) for c in conf]
                idx = [j for j, m in enumerate(mask) if m]
                if idx:
                    bin_conf.append(float(np.mean([conf[j] for j in idx])))
                    bin_acc.append(float(np.mean([correct[j] for j in idx])))
            ece = compute_ece(y_true, conf, y_pred, n_bins)
            if bin_conf:
                ax.plot(
                    bin_conf, bin_acc, style, color=colors.get(variant, "#333"),
                    label=f"{label_suffix} ECE={ece:.3f}",
                )

        ax.plot([0, 1], [0, 1], "k:", alpha=0.4, linewidth=1)
        ax.set_title(variant)
        ax.set_xlabel("Confianza")
        ax.set_ylabel("Accuracy empírica")
        ax.legend(fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    fig.suptitle("Calibración post-hoc — tres variantes (train-fit isotónica)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_middleware_ablation(
    df_eval: pd.DataFrame,
    df_var1: pd.DataFrame,
    df_var2_ref: pd.DataFrame,
    df_gate_a: pd.DataFrame,
    neighbors_map: dict[str, list],
    rag_plugin: Any,
    policy_engine: Any,
    build_features: Any,
    ablations: list[str],
    cost_kw: dict[str, Any],
) -> pd.DataFrame:
    gate_a = df_gate_a.set_index("text_hash")["decision"].to_dict()
    ref_metrics = compute_metrics_bundle(
        df_var2_ref["true_label"].astype(str).tolist(),
        df_var2_ref["final_label"].astype(str).tolist(),
        "Var2_completo",
        df_var2_ref["confidence"].astype(float).tolist(),
        alcance_n=len(df_var2_ref),
        override_count=int(df_var2_ref["overridden"].sum()),
        **cost_kw,
    )
    ref_f1_stop = ref_metrics["F1-stop (F1-critical)"]
    ref_ec = ref_metrics["EC (Expected Cost / ex-CEPA)"]
    ref_override = float(df_var2_ref["overridden"].mean())

    rows = [{
        "componente_ablado": "ninguno (Var2 completo)",
        "F1-stop": round(ref_f1_stop, 6),
        "EC": round(ref_ec, 6),
        "override_rate": round(ref_override, 6),
        "delta_F1-stop": 0.0,
        "delta_EC": 0.0,
        "delta_override_rate": 0.0,
        "n_overrides": int(df_var2_ref["overridden"].sum()),
    }]

    eval_text = df_eval.set_index("text_hash")["text"].to_dict()

    for ablation in ablations:
        if ablation == "sin_gate_b":
            preds = df_var1["pred_label"].astype(str).tolist()
            overrides = 0
        else:
            preds, overrides = [], 0
            for _, row in df_var1.iterrows():
                th = str(row["text_hash"])
                text = str(eval_text.get(th, ""))
                v1_label = str(row["pred_label"])
                v1_conf = float(row["confidence"])
                ns = neighbors_map.get(th, [])
                rag_enrich = rag_plugin.enrich(th, ns)
                features = build_features(text, v1_label, ns, rag_enrich, llm_label=v1_label, llm_confidence=v1_conf)
                features = apply_ablation_to_features(features, ablation)
                ga = gate_a.get(th, "pausa")
                gb = policy_engine.decide_gate_b(ga, v1_label, features)
                preds.append(gb["decision"])
                if gb["override"]:
                    overrides += 1

        y_true = df_var1["true_label"].astype(str).tolist()
        m = compute_metrics_bundle(
            y_true, preds, f"abl_{ablation}",
            df_var1["confidence"].astype(float).tolist(),
            alcance_n=len(preds),
            override_count=overrides,
            **cost_kw,
        )
        ov_rate = overrides / max(len(preds), 1)
        rows.append({
            "componente_ablado": ablation,
            "F1-stop": round(m["F1-stop (F1-critical)"], 6),
            "EC": round(m["EC (Expected Cost / ex-CEPA)"], 6),
            "override_rate": round(ov_rate, 6),
            "delta_F1-stop": round(m["F1-stop (F1-critical)"] - ref_f1_stop, 6),
            "delta_EC": round(m["EC (Expected Cost / ex-CEPA)"] - ref_ec, 6),
            "delta_override_rate": round(ov_rate - ref_override, 6),
            "n_overrides": overrides,
        })

    return pd.DataFrame(rows)


def plot_ablation_delta(out_df: pd.DataFrame, out_path: Path) -> None:
    df = out_df[out_df["componente_ablado"] != "ninguno (Var2 completo)"].copy()
    if df.empty:
        df = out_df.copy()
    labels = df["componente_ablado"].tolist()
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].barh(x, df["delta_F1-stop"].astype(float), color="#2ecc71")
    axes[0].set_yticks(x)
    axes[0].set_yticklabels(labels, fontsize=8)
    axes[0].axvline(0, color="k", linewidth=0.8)
    axes[0].set_title("Δ F1-stop vs Var2 completo")
    axes[1].barh(x, df["delta_EC"].astype(float), color="#e74c3c")
    axes[1].set_yticks(x)
    axes[1].set_yticklabels(labels, fontsize=8)
    axes[1].axvline(0, color="k", linewidth=0.8)
    axes[1].set_title("Δ EC vs Var2 completo")
    fig.suptitle("Ablación middleware — impacto por componente")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_signal_importance(
    df_var2: pd.DataFrame,
    df_senales: pd.DataFrame,
    winning_config: dict[str, Any],
    n_repeats: int = 15,
) -> pd.DataFrame:
    merged = df_var2.merge(df_senales, on="text_hash", suffixes=("", "_sig"))
    signal_cols = [
        "risk_4d", "I_db", "I_mem", "I_sec", "I_dat",
        "rag_uncertainty", "neighbor_entropy", "class_consensus",
    ]
    for c in signal_cols:
        if c not in merged.columns:
            merged[c] = 0.0

    X = merged[signal_cols].astype(float).fillna(0.0)
    y = merged["overridden"].astype(int)

    clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
    clf.fit(X, y)
    perm = permutation_importance(clf, X, y, n_repeats=n_repeats, random_state=42, scoring="roc_auc")

    imp_rows = []
    params = winning_config.get("params", winning_config)
    weights = params.get("weights", {})
    weight_map = {
        "risk_4d": weights.get("risk", 0),
        "class_consensus": weights.get("p_stop", 0),
        "rag_uncertainty": weights.get("uncertainty", 0),
        "neighbor_entropy": weights.get("uncertainty", 0) * 0.5,
    }

    for i, col in enumerate(signal_cols):
        imp_rows.append({
            "senal": col,
            "importancia_perm_media": round(float(perm.importances_mean[i]), 6),
            "importancia_perm_std": round(float(perm.importances_std[i]), 6),
            "coef_logistic_override": round(float(clf.coef_[0][i]), 6),
            "peso_hpo_referencia": round(float(weight_map.get(col, weights.get("fuzzy_stop", 0) if col == "risk_4d" else 0)), 6),
            "target": "override_gate_b",
        })

    return pd.DataFrame(imp_rows).sort_values("importancia_perm_media", ascending=False)


def plot_signal_importance(imp_df: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(imp_df["senal"], imp_df["importancia_perm_media"], xerr=imp_df["importancia_perm_std"], color="#8e44ad")
    ax.set_xlabel("Permutation importance (AUC override Gate B)")
    ax.set_title("Señales que disparan overrides — Gate B")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_pilot_crewai_subanalysis(df_var1: pd.DataFrame, cost_kw: dict[str, Any]) -> pd.DataFrame:
    crewai_sources = {"crewai_cache", "crewai_api"}
    pilot = df_var1[df_var1["source"].isin(crewai_sources)].copy()
    if len(pilot) == 0:
        return pd.DataFrame([{"nota": "sin tickets CrewAI en cache"}])

    m = compute_metrics_bundle(
        pilot["true_label"].astype(str).tolist(),
        pilot["pred_label"].astype(str).tolist(),
        "Var1_solo_crewai_piloto",
        pilot["confidence"].astype(float).tolist(),
        alcance_n=len(pilot),
        **cost_kw,
    )
    m["n_piloto"] = len(pilot)
    m["fuentes"] = json.dumps(pilot["source"].value_counts().to_dict(), ensure_ascii=False)
    m["nota_metodologica"] = (
        "Sub-análisis n=40; no sustituye evaluación protocolo n=400 con abstención Chow 1970"
    )
    return pd.DataFrame([m])


def load_predictions(cfg: dict[str, Any]) -> dict[str, pd.DataFrame]:
    df_bl = pd.read_csv(resolve_path(cfg["paths"]["pred_baseline"]))
    df_v1 = pd.read_csv(resolve_path(cfg["paths"]["pred_var1"]))
    df_v2 = pd.read_csv(resolve_path(cfg["paths"]["pred_var2"]))
    df_v2 = df_v2.rename(columns={"final_label": "pred_label"})
    return {"Baseline": df_bl, "Var1": df_v1, "Var2": df_v2}


def build_resumen_informe(
    cal_df: pd.DataFrame,
    abl_df: pd.DataFrame,
    imp_df: pd.DataFrame,
    pilot_df: pd.DataFrame,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    resumen_cal = {}
    for var in ("Baseline", "Var1", "Var2"):
        antes = cal_df[(cal_df["variante"] == var) & (cal_df["fase"] == "antes") & (cal_df["alcance"] == "n400")]
        desp = cal_df[(cal_df["variante"] == var) & (cal_df["metodo_calibracion"] == "isotonic") & (cal_df["alcance"] == "n400")]
        if not antes.empty and not desp.empty:
            resumen_cal[var] = {
                "ECE_antes": float(antes.iloc[0]["ECE"]),
                "ECE_despues_isotonic": float(desp.iloc[0]["ECE"]),
                "Brier_antes": float(antes.iloc[0]["Brier"]),
                "Brier_despues_isotonic": float(desp.iloc[0]["Brier"]),
                "delta_ECE": round(float(desp.iloc[0]["ECE"]) - float(antes.iloc[0]["ECE"]), 6),
            }

    top_signals = imp_df.head(3)["senal"].tolist() if not imp_df.empty else []
    worst_ablation = None
    if len(abl_df) > 1:
        sub = abl_df[abl_df["componente_ablado"] != "ninguno (Var2 completo)"]
        if not sub.empty:
            worst_ablation = sub.loc[sub["delta_F1-stop"].idxmin()]["componente_ablado"]

    pilot_n = 0
    if not pilot_df.empty and "n_piloto" in pilot_df.columns:
        pilot_n = int(pilot_df.iloc[0]["n_piloto"])

    return {
        "paso": 4,
        "ia06": True,
        "n_eval_protocolo": cfg["n_eval"],
        "n_piloto_crewai": cfg["n_piloto_crewai"],
        "calibracion_resumen": resumen_cal,
        "ablacion_peor_F1_stop": worst_ablation,
        "senales_top_override": top_signals,
        "piloto_n": pilot_n,
        "honesty_notes": cfg.get("honesty_notes", []),
        "veredicto": "PASO 4 completado sobre cache PASO 3 — sin re-API",
    }
