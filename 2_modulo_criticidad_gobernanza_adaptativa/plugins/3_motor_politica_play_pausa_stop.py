"""
PolicyEngine — play / pausa / stop con matriz de costos Elkan.

Lógica mínima adaptada de sprint6_colab (predict_robust) sin depender de tesis2/src.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

CLASSES = ("play", "pausa", "stop")

_STOP_KW_EN = (
    "crash", "deadlock", "hang", "freeze", "unusable", "corrupt", "segfault", "fatal", "data loss",
)
_PLAY_KW_EN = ("typo", "cosmetic", "documentation", "spelling", "ui polish", "test case", "unit test")


def label_value(label: str) -> float:
    return {"play": 0.0, "pausa": 0.5, "stop": 1.0}.get(label, 0.5)


def _clip01(v: float) -> float:
    return min(max(float(v), 0.0), 1.0)


def _entropy01(probs: dict[str, float]) -> float:
    vals = [_clip01(probs.get(c, 0.0)) for c in CLASSES]
    total = sum(vals)
    if total <= 0:
        return 1.0
    norm = [v / total for v in vals]
    ent = -sum(p * math.log(p) for p in norm if p > 0)
    return _clip01(ent / math.log(len(CLASSES)))


def rag_similarity_confidence(neighbors: list[dict[str, Any]] | None) -> float:
    distances = [float(n.get("distance", 1.0)) for n in (neighbors or []) if n.get("distance") is not None]
    if not distances:
        return 0.0
    return _clip01(1.0 - sum(distances) / len(distances))


def majority_label(neighbors: list[dict[str, Any]] | None) -> tuple[str, dict[str, int]]:
    labels = [str(n.get("label", n.get("neighbor_label", "pausa"))) for n in (neighbors or [])]
    counts = Counter(labels)
    if not counts:
        return "pausa", {}
    return str(counts.most_common(1)[0][0]), dict(counts)


def compute_risk_4d_en(text: str) -> tuple[float, dict[str, float]]:
    """Modelo 4D inglés inline (Bugzilla short_desc)."""
    t = text.lower()
    def dim_score(keywords: tuple[tuple[str, float], ...]) -> float:
        raw = sum(w for kw, w in keywords if kw in t)
        return min(max(raw / 2.0, 0.0), 1.0)

    db_kw = (("deadlock", 1.2), ("crash", 1.0), ("hang", 1.0), ("database", 0.8), ("migration", 0.7))
    mem_kw = (("memory leak", 1.2), ("overflow", 1.0), ("heap", 0.7))
    sec_kw = (("injection", 1.1), ("xss", 1.0), ("vulnerability", 1.0), ("authentication", 0.8))
    dat_kw = (("data loss", 1.2), ("corruption", 0.9), ("race condition", 0.9))
    ctx_stop = ("unusable", "blocker", "critical", "production", "fatal", "crash")
    ctx_pause = ("api", "endpoint", "regression", "performance", "timeout")

    prod_boost = 0.2 * sum(1 for kw in ctx_stop if kw in t)
    dims = {
        "I_db": min(dim_score(db_kw) + prod_boost * 0.5, 1.0),
        "I_mem": dim_score(mem_kw),
        "I_sec": min(dim_score(sec_kw) + prod_boost * 0.4, 1.0),
        "I_dat": min(dim_score(dat_kw) + prod_boost * 0.3, 1.0),
        "I_ctx_stop": min(sum(1 for kw in ctx_stop if kw in t) / 3.0, 1.0),
        "I_ctx_pause": min(sum(1 for kw in ctx_pause if kw in t) / 3.0, 1.0),
    }
    raw = (
        0.30 * dims["I_db"] + 0.15 * dims["I_mem"] + 0.30 * dims["I_sec"]
        + 0.25 * dims["I_dat"] + 0.35 * dims["I_ctx_stop"] + 0.18 * dims["I_ctx_pause"]
    )
    play_hits = sum(1 for kw in _PLAY_KW_EN if kw in t)
    mitigation = max(0.0, 1.0 - 0.12 * play_hits)
    risk = min(max(raw * mitigation, 0.0), 1.0)
    return risk, dims


def lexical_stop_flag(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in _STOP_KW_EN)


def build_features(
    text: str,
    base_label: str,
    neighbors: list[dict[str, Any]] | None,
    rag_enrichment: dict[str, float | int] | None = None,
    llm_label: str | None = None,
    llm_confidence: float | None = None,
) -> dict[str, Any]:
    """Construye vector de features para PolicyEngine."""
    risk_4d, dims = compute_risk_4d_en(text)
    base, votes = majority_label(neighbors)
    if base_label not in CLASSES:
        base_label = base
    total = sum(votes.values()) or 1
    probs = {c: votes.get(c, 0) / total for c in CLASSES}
    if llm_label in CLASSES and llm_confidence is not None:
        conf = _clip01(llm_confidence)
        probs = {c: 0.30 * probs.get(c, 0.0) for c in CLASSES}
        probs[str(llm_label)] = probs.get(str(llm_label), 0.0) + 0.70 * conf
        missing = max(1.0 - sum(probs.values()), 0.0)
        for c in CLASSES:
            probs[c] += missing / len(CLASSES)
    rag_sim = rag_similarity_confidence(neighbors)
    ent_u = _entropy01(probs)
    rag = rag_enrichment or {}
    neighbor_ent = float(rag.get("neighbor_entropy", ent_u))
    uncertainty = _clip01(0.40 * (1.0 - max(probs.values())) + 0.30 * neighbor_ent + 0.30 * float(rag.get("rag_uncertainty", 0.0)))
    sec_dat = max(dims.get("I_sec", 0.0), dims.get("I_dat", 0.0))
    fuzzy_stop = max(risk_4d if risk_4d >= 0.68 else 0.0, sec_dat if sec_dat >= 0.78 else 0.0, probs.get("stop", 0.0))
    expected_stop_miss = 1.0 * max(probs.get("stop", 0.0), fuzzy_stop) * (0.55 + 0.45 * uncertainty)
    return {
        "risk_4d": risk_4d,
        "dims_4d": dims,
        "uncertainty": uncertainty,
        "rag_similarity": rag_sim,
        "p_stop": probs.get("stop", 0.0),
        "p_play": probs.get("play", 0.0),
        "p_pausa": probs.get("pausa", 0.0),
        "fuzzy_stop": fuzzy_stop,
        "expected_stop_miss_cost": expected_stop_miss,
        "base_label": base_label,
        "neighbor_entropy": neighbor_ent,
        "class_consensus": float(rag.get("class_consensus", max(probs.values()))),
    }


def combined_score(features: dict[str, Any], weights: dict[str, float]) -> float:
    return float(
        weights["base"] * label_value(str(features["base_label"]))
        + weights["risk"] * features["risk_4d"]
        + weights["p_stop"] * features["p_stop"]
        + weights["uncertainty"] * features["uncertainty"]
        + weights["rag_gap"] * (1.0 - features["rag_similarity"])
        + weights["fuzzy_stop"] * features["fuzzy_stop"]
    )


def predict_robust(features: dict[str, Any], params: dict[str, Any]) -> tuple[str, float, list[str]]:
    """Decisión play/pausa/stop + score + traza."""
    score = combined_score(features, params["weights"])
    trace: list[str] = []
    if (
        features["expected_stop_miss_cost"] >= params["stop_cost_threshold"]
        and (features["risk_4d"] >= params["risk_stop_floor"] or features["p_stop"] >= params["p_stop_floor"])
    ):
        trace.append("STOP: costo esperado FN-stop supera umbral HITL")
        return "stop", score, trace
    if (
        features["base_label"] == "play"
        and features["uncertainty"] >= params["pause_uncertainty"]
        and score >= params["threshold_pausa"]
    ):
        trace.append("PAUSA: play con incertidumbre alta")
        return "pausa", score, trace
    if score >= params["threshold_stop"]:
        trace.append("STOP: score combinado supera umbral stop")
        return "stop", score, trace
    if score >= params["threshold_pausa"]:
        trace.append("PAUSA: score combinado supera umbral pausa")
        return "pausa", score, trace
    trace.append("PLAY: score bajo umbrales")
    return "play", score, trace


class PolicyEngine:
    """Motor de política con RagPlugin obligatorio (Var2 / D2)."""

    def __init__(self, params: dict[str, Any], rag_obligatorio: bool = True):
        self.params = params
        self.rag_obligatorio = rag_obligatorio

    def decide_gate_a(
        self,
        text: str,
        neighbors: list[dict[str, Any]] | None,
        rag_enrichment: dict[str, float | int] | None,
        agent_label: str | None = None,
        agent_confidence: float | None = None,
    ) -> dict[str, Any]:
        base, _ = majority_label(neighbors)
        features = build_features(
            text, base, neighbors, rag_enrichment,
            llm_label=agent_label, llm_confidence=agent_confidence,
        )
        if self.rag_obligatorio and not rag_enrichment:
            features["uncertainty"] = min(1.0, features["uncertainty"] + 0.15)
        label, score, trace = predict_robust(features, self.params)
        return {
            "gate": "A",
            "decision": label,
            "score": score,
            "trace": trace,
            "features": features,
        }

    def decide_gate_b(
        self,
        gate_a_decision: str,
        agent_label: str,
        features: dict[str, Any],
    ) -> dict[str, Any]:
        """Override post-agente si agente contradice señales de riesgo (Var2)."""
        trace: list[str] = []
        severity = {"play": 0, "pausa": 1, "stop": 2}
        final = agent_label if agent_label in CLASSES else gate_a_decision
        override = False
        ga = gate_a_decision if gate_a_decision in CLASSES else "pausa"
        ag = agent_label if agent_label in CLASSES else ga
        risk_high = features["risk_4d"] >= 0.35 or features["p_stop"] >= 0.45
        # Gate B: criticidad más conservadora que agente RAG
        if severity.get(ga, 1) > severity.get(ag, 1) and (risk_high or ga == "stop"):
            final = ga
            override = True
            trace.append("OVERRIDE: Gate A más conservador que agente simulado")
        elif features["expected_stop_miss_cost"] >= 0.42 and ag == "play" and ga != "play":
            final = ga
            override = True
            trace.append("OVERRIDE: FN-stop esperado → decisión Gate A")
        elif ag in ("play", "pausa") and ga == "stop" and (
            features["risk_4d"] >= 0.28 or features["p_stop"] >= 0.40
        ):
            final = "stop"
            override = True
            trace.append("OVERRIDE: riesgo 4D/RAG → escalación stop (Var2)")
        elif ag == "play" and ga == "pausa" and features["uncertainty"] >= 0.38:
            final = "pausa"
            override = True
            trace.append("OVERRIDE: play con incertidumbre RAG → pausa (Var2)")
        if not override:
            trace.append("SIN OVERRIDE: se conserva etiqueta agente simulado")
        return {
            "gate": "B",
            "agent_label": agent_label,
            "decision": final,
            "override": override,
            "trace": trace,
        }


def expected_cost(y_true: list[str], y_pred: list[str], pause_cost: float, stop_cost: float, fn_stop: float) -> float:
    total = 0.0
    for yt, yp in zip(y_true, y_pred):
        if yp == "pausa":
            total += pause_cost
        if yp == "stop":
            total += stop_cost
        if yt == "stop" and yp != "stop":
            total += fn_stop
    return total / max(len(y_true), 1)
