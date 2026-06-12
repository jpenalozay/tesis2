"""
CostPlugin — stub batch para eje costo/ineficiencia.

En runtime PASO 3 medirá tokens y reintentos reales; aquí constantes documentadas.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostSignals:
    token_cost_proxy: float
    loop_retry_proxy: int
    cost_axis_score: float


class CostPlugin:
    """Proxy de costo computacional en modo batch offline."""

    def __init__(self, base_tokens: float = 1200.0, retry_on_pausa: int = 1, retry_on_stop: int = 0):
        self.base_tokens = base_tokens
        self.retry_on_pausa = retry_on_pausa
        self.retry_on_stop = retry_on_stop

    def estimate(self, decision: str | None = None) -> CostSignals:
        """Estima costo según modo criticidad (stub)."""
        retries = 0
        tokens = self.base_tokens
        if decision == "pausa":
            retries = self.retry_on_pausa
            tokens *= 1.15
        elif decision == "stop":
            retries = self.retry_on_stop
            tokens *= 0.5  # bloqueo temprano reduce tokens
        cost_score = min(1.0, tokens / 10000.0 + retries * 0.05)
        return CostSignals(
            token_cost_proxy=round(tokens, 2),
            loop_retry_proxy=retries,
            cost_axis_score=round(cost_score, 6),
        )
