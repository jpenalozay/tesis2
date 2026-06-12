"""
HitlGateway — asignación HITL síncrono (stop) vs asíncrono (pausa).

En batch simula cola en CSV (D4); en runtime PASO 3 integraría LangGraph interrupt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HitlAssignment:
    decision: str
    modo_hitl: str  # auto | sync | async
    bloqueo_pre_accion: bool
    cola_revisión: bool
    nota: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "modo_hitl": self.modo_hitl,
            "bloqueo_pre_accion": self.bloqueo_pre_accion,
            "cola_revision": self.cola_revisión,
            "nota": self.nota,
        }


class HitlGateway:
    """Puerta HITL según decisión criticidad."""

    def __init__(self, play_mode: str = "auto", pausa_mode: str = "async", stop_mode: str = "sync"):
        self.modes = {"play": play_mode, "pausa": pausa_mode, "stop": stop_mode}

    def assign(self, decision: str) -> HitlAssignment:
        mode = self.modes.get(decision, "auto")
        if decision == "stop":
            return HitlAssignment(
                decision=decision,
                modo_hitl=mode,
                bloqueo_pre_accion=True,
                cola_revisión=False,
                nota="HITL síncrono: bloqueo pre-LLM/tools (EU AI Act Art. 14)",
            )
        if decision == "pausa":
            return HitlAssignment(
                decision=decision,
                modo_hitl=mode,
                bloqueo_pre_accion=False,
                cola_revisión=True,
                nota="HITL asíncrono simulado: ticket en cola CSV para operador",
            )
        return HitlAssignment(
            decision=decision,
            modo_hitl=mode,
            bloqueo_pre_accion=False,
            cola_revisión=False,
            nota="Autonomía plena: sin bloqueo HITL",
        )

    def summary_by_class(self, decisions: list[str], true_labels: list[str]) -> list[dict[str, Any]]:
        """Agrega modos HITL por clase real (thesis_class)."""
        from collections import defaultdict

        buckets: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for dec, yt in zip(decisions, true_labels):
            h = self.assign(dec)
            buckets[yt][h.modo_hitl] += 1
            buckets[yt]["total"] += 1
        rows = []
        for cls, counts in sorted(buckets.items()):
            rows.append({
                "thesis_class": cls,
                "n_total": counts["total"],
                "n_auto": counts.get("auto", 0),
                "n_async": counts.get("async", 0),
                "n_sync": counts.get("sync", 0),
            })
        return rows
