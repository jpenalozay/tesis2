"""
Predictores Baseline / Var1 / Var2 — PASO 3 entregable.

Cache-first; API DeepSeek incremental cuando run_api=true.
Var1: CrewAI Analyst+Reviewer vía crewai.LLM + DeepSeek (crewai_var1_entregable).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("protocolo_variantes")

_PASO1 = Path(__file__).resolve().parents[1] / "1_ingenieria_atributos_y_recuperacion_rag"
if str(_PASO1) not in sys.path:
    sys.path.insert(0, str(_PASO1))

from crewai_var1_entregable import build_cache_key, run_crewai_var1  # noqa: E402

CLASSES = ("play", "pausa", "stop")

# Importar simulate_baseline desde tesis2 si disponible
_TESIS2 = Path(__file__).resolve().parents[3]  # tesis2/
if str(_TESIS2) not in sys.path:
    sys.path.insert(0, str(_TESIS2))

try:
    from src.math_criticidad import baseline_rules_classify as _baseline_es
except ImportError:
    _baseline_es = None

from metricas_protocolo_entregable import CLASSES as _  # noqa: F401 — reexport


def ensure_deepseek_env() -> bool:
    """Mapea SYSTEM_LLM_* → DEEPSEEK_* si hace falta."""
    key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("SYSTEM_LLM_API_KEY")
    if key:
        os.environ.setdefault("DEEPSEEK_API_KEY", key)
    model = os.getenv("DEEPSEEK_MODEL") or os.getenv("SYSTEM_LLM_MODEL")
    if model:
        os.environ.setdefault("DEEPSEEK_MODEL", model)
    base = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("SYSTEM_LLM_BASE_URL")
    if base:
        os.environ.setdefault("DEEPSEEK_BASE_URL", base)
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def _parse_api_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "401" in msg or "unauthorized" in msg:
        return "auth_401"
    if "402" in msg or "insufficient" in msg or "balance" in msg or "credit" in msg:
        return "credits_exhausted"
    if "429" in msg or "rate" in msg:
        return "rate_limit"
    return "api_error"


def load_jsonl_cache(path: Path) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return cache
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            key = item.get("cache_key") or item.get("text_hash")
            if key:
                cache[str(key)] = item
        except json.JSONDecodeError:
            pass
    return cache


def load_deepseek_cache(paths: list[Path]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for p in paths:
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                h = str(item.get("text_hash", ""))
                if h:
                    merged[h] = item
            except json.JSONDecodeError:
                pass
    return merged


def load_metagpt_var1_cache(path: Path) -> dict[str, dict[str, Any]]:
    """Deprecated — MetaGPT no forma parte del flujo Var1 (experimento futuro separado)."""
    _ = path
    return {}


def select_var1_pilot_hashes_stratified(
    eval_rows: list[dict[str, Any]],
    seed: int = 42,
    n: int = 40,
) -> set[str]:
    """Selección estratificada determinística (seed=42) — alineada D5 10%."""
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.DataFrame(eval_rows)
    if len(df) <= n:
        return set(df["text_hash"].astype(str))
    sample, _ = train_test_split(
        df,
        train_size=n,
        stratify=df["thesis_class"],
        random_state=seed,
    )
    return set(sample["text_hash"].astype(str))


def compute_var1_api_queue(
    eval_rows: list[dict[str, Any]],
    crewai_cache: dict[str, dict[str, Any]],
    pilot_hashes: set[str],
) -> set[str]:
    """Tickets del piloto D5 sin entrada válida en crewai_cache (candidatos a crewai_api)."""
    pending: set[str] = set()
    for th in pilot_hashes:
        ck = build_cache_key(th)
        item = crewai_cache.get(ck)
        if item and item.get("status") == "ok" and item.get("label") in CLASSES:
            continue
        pending.add(th)
    return pending


def simulate_baseline(text: str) -> str:
    """Fallback léxico determinista (EarlyGate / reglas ES)."""
    t = text.lower()
    stop_kw = ("crash", "deadlock", "hang", "freeze", "segfault", "fatal", "data loss", "blocker", "critical")
    play_kw = ("typo", "cosmetic", "documentation", "spelling", "ui polish", "test case")
    if any(k in t for k in stop_kw):
        return "stop"
    if any(k in t for k in play_kw):
        return "play"
    if _baseline_es is not None:
        return _baseline_es(text)
    return "pausa"


def majority_label(neighbors: list[dict[str, Any]]) -> tuple[str, float]:
    from collections import Counter
    import math

    labels = [str(n.get("label", n.get("neighbor_label", "pausa"))) for n in neighbors]
    if not labels:
        return "pausa", 1.0
    counts = Counter(labels)
    maj, cnt = counts.most_common(1)[0]
    ent = -sum((c / len(labels)) * math.log(c / len(labels)) for c in counts.values())
    ent_norm = ent / math.log(len(CLASSES))
    uncertainty = min(max(ent_norm, 0.0), 1.0)
    return str(maj), uncertainty


def predict_baseline(
    text: str,
    text_hash: str,
    deepseek_cache: dict[str, dict[str, Any]],
    local_cache_path: Path | None,
    run_api: bool,
    api_calls: list[int],
    max_api: int,
    api_errors: dict[str, int] | None = None,
) -> tuple[str, float, float, str, int]:
    start = time.perf_counter()
    item = deepseek_cache.get(text_hash)
    if item and item.get("status") == "ok" and item.get("label") in CLASSES:
        usage = item.get("usage") or {}
        tokens = int(usage.get("total_tokens") or 150)
        src = "deepseek_api" if item.get("source") == "deepseek_api" else "deepseek_cache"
        return (
            str(item["label"]),
            float(item.get("confidence") or 0.7),
            (time.perf_counter() - start) * 1000,
            src,
            tokens,
        )

    has_key = ensure_deepseek_env()
    if run_api and api_calls[0] < max_api and has_key:
        try:
            api_calls[0] += 1
            sys.path.insert(0, str(_TESIS2 / "agentes"))
            from core.llm_client_v3 import LLMClient

            client = LLMClient()
            prompt = (
                "Clasifica este bug Bugzilla en exactamente una etiqueta: play, pausa o stop.\n"
                "play=bajo riesgo; pausa=riesgo medio/revisión; stop=critical/blocker/security.\n"
                "Responde SOLO JSON: {\"label\": \"...\", \"confidence\": 0.0-1.0}\n\n"
                f"Ticket:\n{text}"
            )
            raw = client.generate_with_retry(
                prompt,
                system_prompt="Conservative bug criticality classifier. JSON only.",
                temperature=0.0,
                max_tokens=120,
                max_retries=3,
                retry_delay=3,
            )
            parsed = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
            label = str(parsed.get("label", "pausa")).lower()
            if label not in CLASSES:
                label = "pausa"
            conf = float(parsed.get("confidence") or 0.7)
            tokens = 150
            rec = {
                "text_hash": text_hash,
                "status": "ok",
                "label": label,
                "confidence": conf,
                "source": "deepseek_api",
                "usage": {"total_tokens": tokens},
            }
            deepseek_cache[text_hash] = rec
            if local_cache_path:
                with local_cache_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return label, conf, (time.perf_counter() - start) * 1000, "deepseek_api", tokens
        except Exception as exc:
            err_kind = _parse_api_error(exc)
            if api_errors is not None:
                api_errors[err_kind] = api_errors.get(err_kind, 0) + 1
            logger.warning("DeepSeek API falló (%s): %s", err_kind, exc)

    label = simulate_baseline(text)
    return label, 0.55, (time.perf_counter() - start) * 1000, "early_gate_lexical_fallback", 0


def predict_var1(
    text: str,
    text_hash: str,
    neighbors: list[dict[str, Any]],
    crewai_cache: dict[str, dict[str, Any]],
    run_crewai: bool,
    api_calls: list[int],
    max_api: int,
    local_cache_path: Path | None,
    api_errors: dict[str, int] | None = None,
    api_pilot_hashes: set[str] | None = None,
) -> tuple[str, float, float, str, int]:
    """Var1 piloto D5: RAG→CrewAI (cache→API). Fuera piloto: abstención pausa (Chow 1970). Sin majority."""
    start = time.perf_counter()
    in_pilot = api_pilot_hashes is None or text_hash in api_pilot_hashes
    if not in_pilot:
        return "pausa", 0.45, (time.perf_counter() - start) * 1000, "abstencion_fuera_piloto_d5", 0

    ck = build_cache_key(text_hash)
    if ck in crewai_cache and crewai_cache[ck].get("status") == "ok" and crewai_cache[ck].get("label") in CLASSES:
        item = crewai_cache[ck]
        return (
            str(item["label"]),
            float(item.get("confidence") or 0.75),
            float(item.get("latency_ms") or 0),
            "crewai_cache",
            int(item.get("tokens") or 0),
        )

    has_key = ensure_deepseek_env()
    if run_crewai and api_calls[0] < max_api and has_key:
        try:
            api_calls[0] += 1
            out = run_crewai_var1(text, neighbors)
            label = str(out["label"]).lower()
            if label not in CLASSES:
                label = "pausa"
            conf = float(out.get("confidence") or 0.75)
            tok = int(out.get("tokens") or 0)
            rec = {
                "cache_key": ck,
                "text_hash": text_hash,
                "variant": "var1_crewai_rag",
                "status": "ok",
                "label": label,
                "confidence": conf,
                "tokens": tok,
                "latency_ms": out.get("latency_ms"),
                "source": "crewai_api",
                "model": out.get("model"),
                "prompt_version": out.get("prompt_version"),
                "analyst_label": out.get("analyst_label"),
                "reviewer_label": out.get("reviewer_label"),
                "usage": out.get("usage") or {},
            }
            crewai_cache[ck] = rec
            if local_cache_path:
                with local_cache_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return label, conf, float(out.get("latency_ms") or (time.perf_counter() - start) * 1000), "crewai_api", tok
        except Exception as exc:
            err_kind = _parse_api_error(exc)
            if api_errors is not None:
                api_errors[err_kind] = api_errors.get(err_kind, 0) + 1
            logger.warning("CrewAI API falló (%s) hash=%s: %s", err_kind, text_hash[:12], exc)

    return "pausa", 0.40, (time.perf_counter() - start) * 1000, "abstencion_crewai_fallo", 0


def predict_var2(
    var1_label: str,
    var1_conf: float,
    gate_a_decision: str,
    features: dict[str, Any],
    policy_engine: Any,
) -> tuple[str, float, bool, str, list[str]]:
    """Var1 + Gate B (política criticidad PASO 2). Sin API adicional."""
    gb = policy_engine.decide_gate_b(gate_a_decision, var1_label, features)
    final = gb["decision"]
    conf = float(var1_conf)
    if gb["override"]:
        conf = min(conf + 0.1, 0.95)
    trace_str = " | ".join(gb["trace"])
    return final, conf, bool(gb["override"]), trace_str, gb["trace"]


def build_features_from_senales(row: dict[str, Any], agent_label: str, agent_conf: float) -> dict[str, Any]:
    """Reconstruye features mínimas para Gate B desde tabla señales PASO 2."""
    p_stop = float(row.get("class_consensus", 0.0))
    if row.get("agent_label_sim") == "stop":
        p_stop = max(p_stop, 0.5)
    risk = float(row.get("risk_4d", 0.0))
    uncertainty = float(row.get("rag_uncertainty", row.get("neighbor_entropy", 0.5)))
    return {
        "risk_4d": risk,
        "p_stop": p_stop,
        "uncertainty": uncertainty,
        "expected_stop_miss_cost": 1.0 * max(p_stop, 0.0) * (0.55 + 0.45 * uncertainty),
        "rag_similarity": max(0.0, 1.0 - float(row.get("mean_distance", 1.0))),
        "base_label": agent_label,
    }
