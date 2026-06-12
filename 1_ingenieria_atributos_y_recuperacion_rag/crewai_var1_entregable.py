"""
CrewAI Var1 — módulo compartido (smoke test PASO 1 + protocolo PASO 3).

Analyst + Reviewer secuenciales, DeepSeek vía crewai.LLM, RAG pre-inyectado.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("crewai_var1")

CLASSES = ("play", "pausa", "stop")
PROMPT_VERSION = "v2_permissive_agent"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com/v1"


class BugTriageOutput(BaseModel):
    label: str = Field(description="Etiqueta final: play, pausa o stop")
    confidence: float = Field(ge=0.0, le=1.0, description="Confianza 0-1")
    reason: str = Field(default="", description="Justificación breve")

    @field_validator("label")
    @classmethod
    def normalize_label(cls, v: str) -> str:
        lv = str(v).strip().lower()
        if lv in CLASSES:
            return lv
        for c in CLASSES:
            if c in lv:
                return c
        return "pausa"


def format_neighbors_context(neighbors: list[dict[str, Any]]) -> str:
    if not neighbors:
        return "Sin vecinos RAG (ejecutar PASO 1 primero)."
    lines = []
    for n in neighbors[:5]:
        label = n.get("label", n.get("neighbor_label", "pausa"))
        lines.append(
            f"  rank={n.get('rank')}: label={label} dist={n.get('distance', n.get('score', 'n/a'))}"
        )
    return "\n".join(lines)


def build_cache_key(text_hash: str, model: str | None = None) -> str:
    m = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
    raw = f"{text_hash}|var1_crewai_rag|{PROMPT_VERSION}|{m}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _parse_label_regex(raw: str) -> tuple[str, float]:
    text = raw.strip().lower()
    for c in CLASSES:
        if re.search(rf"\b{c}\b", text):
            return c, 0.75
    return "pausa", 0.55


def _parse_label_from_raw(raw: str) -> tuple[str, float]:
    """Intenta JSON embebido; fallback regex."""
    text = raw.strip()
    try:
        if "{" in text and "}" in text:
            blob = text[text.find("{") : text.rfind("}") + 1]
            parsed = json.loads(blob)
            label = str(parsed.get("label", "pausa")).lower()
            if label in CLASSES:
                return label, float(parsed.get("confidence") or 0.75)
    except Exception:
        pass
    return _parse_label_regex(text)


def _extract_pydantic_from_result(result: Any) -> BugTriageOutput | None:
    try:
        if hasattr(result, "pydantic") and result.pydantic is not None:
            if isinstance(result.pydantic, BugTriageOutput):
                return result.pydantic
            return BugTriageOutput.model_validate(result.pydantic)
    except Exception:
        pass
    try:
        tasks_out = getattr(result, "tasks_output", None) or []
        for task_out in reversed(tasks_out):
            pyd = getattr(task_out, "pydantic", None)
            if pyd is not None:
                if isinstance(pyd, BugTriageOutput):
                    return pyd
                return BugTriageOutput.model_validate(pyd)
    except Exception:
        pass
    return None


def _extract_tokens(result: Any) -> tuple[int, dict[str, Any]]:
    usage: dict[str, Any] = {}
    tokens = 0
    try:
        tu = getattr(result, "token_usage", None)
        if tu is not None:
            if hasattr(tu, "model_dump"):
                usage = tu.model_dump()
            elif isinstance(tu, dict):
                usage = dict(tu)
            else:
                usage = {
                    "prompt_tokens": getattr(tu, "prompt_tokens", 0),
                    "completion_tokens": getattr(tu, "completion_tokens", 0),
                    "total_tokens": getattr(tu, "total_tokens", 0),
                }
            tokens = int(usage.get("total_tokens") or 0)
    except Exception:
        pass
    if tokens <= 0:
        tokens = 400
    return tokens, usage


def run_crewai_var1(text: str, neighbors: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Ejecuta CrewAI Analyst→Reviewer para un ticket.

    Returns dict con label, confidence, tokens, latency_ms, analyst_label, reviewer_label, usage, model.
    """
    from crewai import Agent, Crew, LLM, Process, Task

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY no configurada")

    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)

    llm = LLM(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0,
        max_tokens=256,
    )

    neighbor_ctx = format_neighbors_context(neighbors)
    ticket_text = text[:800]

    analyst = Agent(
        role="BugTriageAnalyst",
        goal="Proponer play/pausa/stop priorizando autonomía del equipo en bugs normal/minor (ablación Var1).",
        backstory="Analista productivo que favorece play en incidencias rutinarias; deja pausa/stop a revisión.",
        llm=llm,
        verbose=False,
        memory=False,
        max_iter=1,
        max_retry_limit=2,
    )
    reviewer = Agent(
        role="BugCriticalityReviewer",
        goal="Revisar la propuesta del analista y devolver la etiqueta final play/pausa/stop.",
        backstory="Revisor senior de criticidad operacional.",
        llm=llm,
        verbose=False,
        memory=False,
        max_iter=1,
        max_retry_limit=2,
    )

    analyze_task = Task(
        description=(
            f"Ticket Bugzilla:\n{ticket_text}\n\n"
            f"Vecinos RAG (train-only, top-5):\n{neighbor_ctx}\n\n"
            "Reglas Var1 (agente permisivo — middleware Var2 escala después):\n"
            "- play: normal, minor, cosmetic, typo, docs, enhancement de bajo riesgo\n"
            "- pausa: major sin crash, incertidumbre, impacto medio\n"
            "- stop: SOLO blocker, critical, crash, security, data loss, assertion fatal\n\n"
            "Responde SOLO con una palabra: play, pausa o stop."
        ),
        expected_output="Una etiqueta: play, pausa o stop.",
        agent=analyst,
    )
    review_task = Task(
        description=(
            "Revisa la propuesta del analista. Puedes corregir al alza hacia stop si hay señales críticas.\n"
            "Responde SOLO con play, pausa o stop."
        ),
        expected_output="Etiqueta final: play, pausa o stop.",
        agent=reviewer,
        context=[analyze_task],
    )

    crew = Crew(
        agents=[analyst, reviewer],
        tasks=[analyze_task, review_task],
        process=Process.sequential,
        verbose=False,
        max_rpm=30,
    )

    t0 = time.perf_counter()
    result = crew.kickoff()
    latency_ms = (time.perf_counter() - t0) * 1000

    analyst_label = "pausa"
    reviewer_label = "pausa"
    confidence = 0.75

    try:
        if analyze_task.output:
            raw_a = str(getattr(analyze_task.output, "raw", analyze_task.output)).strip().lower()
            analyst_label, _ = _parse_label_regex(raw_a)
    except Exception:
        pass

    pyd_out = _extract_pydantic_from_result(result)
    if pyd_out is not None:
        reviewer_label = pyd_out.label
        confidence = float(pyd_out.confidence)
    else:
        raw = str(result).strip()
        reviewer_label, confidence = _parse_label_from_raw(raw)
        if reviewer_label == "pausa" and confidence == 0.55:
            logger.warning("CrewAI parse fallback regex (raw=%s)", raw[:120])

    tokens, usage = _extract_tokens(result)

    return {
        "label": reviewer_label,
        "confidence": confidence,
        "analyst_label": analyst_label,
        "reviewer_label": reviewer_label,
        "tokens": tokens,
        "latency_ms": round(latency_ms, 2),
        "usage": usage,
        "model": model,
        "prompt_version": PROMPT_VERSION,
    }
