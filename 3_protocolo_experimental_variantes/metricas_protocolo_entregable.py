"""
Métricas protocolo experimental — PASO 3 entregable.

Set mínimo 6: F1-macro, F1-stop, ECE, EC (ex-CEPA), FNR-stop, matriz 3×3.
Extendido: MCC macro, balanced accuracy, END (índice auxiliar).
"""

from __future__ import annotations

import json
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold

CLASSES = ("play", "pausa", "stop")


def expected_cost(
    y_true: list[str],
    y_pred: list[str],
    *,
    pause: float = 0.08,
    stop: float = 0.18,
    fn_stop: float = 1.0,
) -> float:
    """Costo esperado de misclasificación (Elkan 2001 / ex-CEPA)."""
    total = 0.0
    for yt, yp in zip(y_true, y_pred):
        if yp == "pausa":
            total += pause
        if yp == "stop":
            total += stop
        if yt == "stop" and yp != "stop":
            total += fn_stop
    return total / max(len(y_true), 1)


def fnr_stop_rate(y_true: list[str], y_pred: list[str]) -> float:
    """Tasa de falsos negativos stop (ex-TFC)."""
    stops = [i for i, yt in enumerate(y_true) if yt == "stop"]
    if not stops:
        return 0.0
    fn = sum(1 for i in stops if y_pred[i] != "stop")
    return fn / len(stops)


def compute_ece(
    y_true: list[str],
    confidences: list[float],
    y_pred: list[str],
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error (Guo et al. 2017)."""
    if not confidences:
        return float("nan")
    correct = [1.0 if yt == yp else 0.0 for yt, yp in zip(y_true, y_pred)]
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = [(lo <= c < hi) if i < n_bins - 1 else (lo <= c <= hi) for c in confidences]
        idx = [j for j, m in enumerate(mask) if m]
        if not idx:
            continue
        acc = float(np.mean([correct[j] for j in idx]))
        conf = float(np.mean([confidences[j] for j in idx]))
        ece += (len(idx) / n) * abs(acc - conf)
    return float(ece)


def mcc_macro(y_true: list[str], y_pred: list[str]) -> float:
    """MCC macro (promedio OvR)."""
    scores = []
    for cls in CLASSES:
        yt_bin = [1 if y == cls else 0 for y in y_true]
        yp_bin = [1 if y == cls else 0 for y in y_pred]
        if len(set(yt_bin)) < 2 or len(set(yp_bin)) < 2:
            continue
        scores.append(matthews_corrcoef(yt_bin, yp_bin))
    return float(np.mean(scores)) if scores else 0.0


def end_indice_auxiliar(f1_macro: float, ec: float, tokens: int) -> float:
    """Índice compuesto interno — NO métrica principal de exposición."""
    return f1_macro / (1.0 + ec + tokens / 10000.0)


# Costo HITL documentado (supuesto operativo — informe UNI / EU AI Act Art. 14)
HITL_MINUTES_PAUSE = 5.0   # checkpoint HOTL (Chow 1970 abstención)
HITL_MINUTES_STOP = 20.0   # validación HITL obligatoria
HITL_MINUTES_OVERRIDE = 3.0  # revisión extra por interceptación middleware
DEV_USD_PER_HOUR = 45.0    # tarifa referencia desarrollador (supuesto)


def hitl_operational_burden(
    y_pred: list[str],
    override_count: int = 0,
) -> dict[str, float]:
    """Carga operativa HITL: tiempo programador + coste USD estimado."""
    n_pause = sum(1 for p in y_pred if p == "pausa")
    n_stop = sum(1 for p in y_pred if p == "stop")
    minutes = n_pause * HITL_MINUTES_PAUSE + n_stop * HITL_MINUTES_STOP
    minutes += override_count * HITL_MINUTES_OVERRIDE
    usd = minutes / 60.0 * DEV_USD_PER_HOUR
    return {
        "hitl_intervenciones_pausa": float(n_pause),
        "hitl_intervenciones_stop": float(n_stop),
        "hitl_overrides_extra": float(override_count),
        "hitl_tiempo_total_min": round(minutes, 2),
        "hitl_costo_programador_usd": round(usd, 4),
    }


def per_class_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, float]:
    """F1, precision, recall por clase (sklearn estándar — papers triage SE)."""
    labels = list(CLASSES)
    f1s = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    precs = precision_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    recs = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    out: dict[str, float] = {}
    for i, cls in enumerate(labels):
        out[f"F1-{cls}"] = round(float(f1s[i]), 6)
        out[f"Precision-{cls}"] = round(float(precs[i]), 6)
        out[f"Recall-{cls}"] = round(float(recs[i]), 6)
    return out


def confusion_dict(y_true: list[str], y_pred: list[str]) -> dict[str, int]:
    cm = confusion_matrix(y_true, y_pred, labels=list(CLASSES))
    out: dict[str, int] = {}
    for i, real in enumerate(CLASSES):
        for j, pred in enumerate(CLASSES):
            out[f"{real}_to_{pred}"] = int(cm[i, j])
    return out


def compute_metrics_bundle(
    y_true: list[str],
    y_pred: list[str],
    variant: str,
    confidences: list[float] | None = None,
    latencies: list[float] | None = None,
    tokens: int = 0,
    *,
    pause_cost: float = 0.08,
    stop_cost: float = 0.18,
    fn_stop_cost: float = 1.0,
    ece_bins: int = 10,
    alcance_n: int | None = None,
    override_count: int = 0,
) -> dict[str, Any]:
    """Calcula set mínimo + extendido + per-class + HITL para una variante."""
    confidences = confidences or [0.5] * len(y_true)
    latencies = latencies or [0.0] * len(y_true)
    f1_macro = float(f1_score(y_true, y_pred, labels=list(CLASSES), average="macro", zero_division=0))
    f1_per = f1_score(y_true, y_pred, labels=list(CLASSES), average=None, zero_division=0)
    f1_play = float(f1_per[0])
    f1_pausa = float(f1_per[1])
    f1_stop = float(f1_per[2])
    ec = expected_cost(y_true, y_pred, pause=pause_cost, stop=stop_cost, fn_stop=fn_stop_cost)
    ece = compute_ece(y_true, confidences, y_pred, n_bins=ece_bins)
    fnr = fnr_stop_rate(y_true, y_pred)
    cm = confusion_dict(y_true, y_pred)
    lat_mean = float(np.mean(latencies)) if latencies else 0.0
    hitl = hitl_operational_burden(y_pred, override_count=override_count)
    per_cls = per_class_metrics(y_true, y_pred)
    return {
        "variante": variant,
        "alcance_n": alcance_n or len(y_true),
        "F1-macro (Macro-averaged F1)": round(f1_macro, 6),
        "F1-play": round(f1_play, 6),
        "F1-pausa": round(f1_pausa, 6),
        "F1-stop (F1-critical)": round(f1_stop, 6),
        "ECE (Expected Calibration Error)": round(ece, 6),
        "EC (Expected Cost / ex-CEPA)": round(ec, 6),
        "FNR-stop (False Negative Rate stop)": round(fnr, 6),
        "MCC-macro (Matthews Correlation)": round(mcc_macro(y_true, y_pred), 6),
        "Balanced accuracy": round(float(balanced_accuracy_score(y_true, y_pred)), 6),
        "tokens_total": int(tokens),
        "latencia_media_ms": round(lat_mean, 2),
        "latencia_p95_ms": round(float(np.percentile(latencies, 95)) if latencies else 0.0, 2),
        "end_indice_auxiliar": round(end_indice_auxiliar(f1_macro, ec, tokens), 6),
        "confusion_matrix_json": json.dumps(cm, ensure_ascii=False),
        **per_cls,
        **hitl,
        **{f"cm_{k}": v for k, v in cm.items()},
    }


def mcnemar_test(
    y_true: list[str],
    y_pred_a: list[str],
    y_pred_b: list[str],
    pair_name: str,
) -> dict[str, Any]:
    """McNemar sobre discordancias (sin scipy: chi-cuadrado con corrección)."""
    b_cnt = sum(1 for yt, a, b in zip(y_true, y_pred_a, y_pred_b) if a == yt and b != yt)
    c_cnt = sum(1 for yt, a, b in zip(y_true, y_pred_a, y_pred_b) if a != yt and b == yt)
    n_disc = b_cnt + c_cnt
    if n_disc == 0:
        stat, pval = 0.0, 1.0
    else:
        stat = (abs(b_cnt - c_cnt) - 1) ** 2 / (b_cnt + c_cnt) if (b_cnt + c_cnt) > 0 else 0.0
        # aproximación p-value chi2(1)
        pval = float(np.exp(-stat / 2.0))
    agree = sum(1 for a, b in zip(y_pred_a, y_pred_b) if a == b) / max(len(y_pred_a), 1)
    return {
        "par": pair_name,
        "discordancias_b": b_cnt,
        "discordancias_c": c_cnt,
        "mcnemar_stat": round(stat, 4),
        "p_value_nominal": round(pval, 6),
        "agreement_rate": round(agree, 6),
        "nota": "p-value nominal; clases raras (stop n=30) limitan poder estadístico",
    }


def stratified_cv_metrics(
    y_true: list[str],
    y_pred: list[str],
    confidences: list[float],
    variant: str,
    seed: int = 42,
    n_splits: int = 5,
    **cost_kw: Any,
) -> pd.DataFrame:
    """CV 5-fold sobre predicciones cacheadas (no re-API)."""
    y = np.array(y_true)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    rows = []
    for fold, (_, val_idx) in enumerate(skf.split(np.zeros(len(y)), y)):
        idx = val_idx.tolist()
        yt = [y_true[i] for i in idx]
        yp = [y_pred[i] for i in idx]
        conf = [confidences[i] for i in idx]
        m = compute_metrics_bundle(yt, yp, variant, conf, alcance_n=len(idx), **cost_kw)
        m["fold"] = fold + 1
        rows.append(m)
    df = pd.DataFrame(rows)
    summary = {"variante": variant, "fold": "mean"}
    for col in ["F1-macro (Macro-averaged F1)", "F1-stop (F1-critical)", "ECE (Expected Calibration Error)",
                "EC (Expected Cost / ex-CEPA)", "FNR-stop (False Negative Rate stop)"]:
        summary[col] = round(df[col].mean(), 6)
        summary[f"{col}_std"] = round(df[col].std(), 6)
    return pd.concat([df, pd.DataFrame([summary])], ignore_index=True)


def _safe_tight_layout(fig) -> None:
    try:
        fig.tight_layout()
    except TypeError:
        fig.subplots_adjust(hspace=0.35, wspace=0.3)


def plot_ablation_f1_ec_fnr(metrics_df: pd.DataFrame, out_path: str) -> None:
    """Figura ablación — F1-macro, EC, FNR-stop (sin END principal)."""
    variants = metrics_df["variante"].tolist()
    x = np.arange(len(variants))
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    metrics = [
        ("F1-macro (Macro-averaged F1)", "F1-macro", "#2ecc71", "↑ mejor"),
        ("EC (Expected Cost / ex-CEPA)", "EC", "#e74c3c", "↓ mejor"),
        ("FNR-stop (False Negative Rate stop)", "FNR-stop", "#3498db", "↓ mejor"),
    ]
    colors = ["#7f8c8d", "#2ecc71", "#e74c3c"]
    for ax, (col, short, color, note) in zip(axes, metrics):
        vals = metrics_df[col].astype(float).tolist()
        ax.bar(x, vals, color=colors)
        ax.set_xticks(x)
        ax.set_xticklabels(variants, rotation=15)
        ax.set_title(f"{short} ({note})")
    fig.suptitle("Ablación simétrica — Baseline → Var1 → Var2 (n=400)")
    _safe_tight_layout(fig)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_confusion_matrices(
    y_true: list[str],
    preds: dict[str, list[str]],
    out_path: str,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    im = None
    for ax, (name, y_pred) in zip(axes, preds.items()):
        cm = confusion_matrix(y_true, y_pred, labels=list(CLASSES))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.set_xticklabels(CLASSES)
        ax.set_yticklabels(CLASSES)
        ax.set_xlabel("Predicho")
        ax.set_ylabel("Real")
        ax.set_title(name)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="black" if cm[i, j] < max(cm.max() / 2, 1) else "white")
    if im is not None:
        fig.colorbar(im, ax=axes, fraction=0.02)
    _safe_tight_layout(fig)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_calibration_curve(
    y_true: list[str],
    confidences: list[float],
    y_pred: list[str],
    out_path: str,
    n_bins: int = 10,
) -> float:
    correct = [1.0 if yt == yp else 0.0 for yt, yp in zip(y_true, y_pred)]
    bins = np.linspace(0, 1, n_bins + 1)
    bin_conf, bin_acc = [], []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = [(lo <= c < hi) if i < n_bins - 1 else (lo <= c <= hi) for c in confidences]
        idx = [j for j, m in enumerate(mask) if m]
        if idx:
            bin_conf.append(float(np.mean([confidences[j] for j in idx])))
            bin_acc.append(float(np.mean([correct[j] for j in idx])))
    ece = compute_ece(y_true, confidences, y_pred, n_bins)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.plot([0, 1], [0, 1], "k--", label="Calibración perfecta")
    if bin_conf:
        ax.plot(bin_conf, bin_acc, "o-", color="#e74c3c", label=f"Var2 (ECE={ece:.3f})")
    ax.set_xlabel("Confianza reportada")
    ax.set_ylabel("Accuracy empírica")
    ax.set_title("Curva de calibración — Var2 middleware")
    ax.legend()
    _safe_tight_layout(fig)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ece
