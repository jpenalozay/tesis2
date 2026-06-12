"""
Contrato SignalProvider — señales para el motor de criticidad (PASO 2).

Tres ejes: riesgo operativo, costo/ineficiencia, incertidumbre del plan.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

CLASSES = ("play", "pausa", "stop")


@dataclass
class SenalesTicket:
    """Vector de señales por ticket de evaluación."""

    text_hash: str
    query_idx: int
    # Eje riesgo
    risk_4d: float = 0.0
    lexical_stop: bool = False
    dims_4d: dict[str, float] = field(default_factory=dict)
    # Eje incertidumbre
    plan_entropy: float = 0.0
    agent_disagreement: float = 0.0
    # Eje costo (stub batch)
    token_cost_proxy: float = 0.0
    loop_retry_proxy: int = 0
    # RAG (RagPlugin)
    neighbor_entropy: float = 0.0
    mean_distance: float = 0.0
    class_consensus: float = 0.0
    conformal_set_size: int = 0
    rag_uncertainty: float = 0.0
    # Base agente simulado
    agent_label_sim: str = "pausa"
    agent_confidence_sim: float = 0.5
    true_label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "text_hash": self.text_hash,
            "query_idx": self.query_idx,
            "risk_4d": self.risk_4d,
            "lexical_stop": self.lexical_stop,
            "I_db": self.dims_4d.get("I_db", 0.0),
            "I_mem": self.dims_4d.get("I_mem", 0.0),
            "I_sec": self.dims_4d.get("I_sec", 0.0),
            "I_dat": self.dims_4d.get("I_dat", 0.0),
            "plan_entropy": self.plan_entropy,
            "agent_disagreement": self.agent_disagreement,
            "token_cost_proxy": self.token_cost_proxy,
            "loop_retry_proxy": self.loop_retry_proxy,
            "neighbor_entropy": self.neighbor_entropy,
            "mean_distance": self.mean_distance,
            "class_consensus": self.class_consensus,
            "conformal_set_size": self.conformal_set_size,
            "rag_uncertainty": self.rag_uncertainty,
            "agent_label_sim": self.agent_label_sim,
            "agent_confidence_sim": self.agent_confidence_sim,
            "true_label": self.true_label,
        }


class ProveedorSenales(ABC):
    """Interfaz para proveedores de señales por ticket."""

    @abstractmethod
    def compute(self, text: str, text_hash: str, query_idx: int, true_label: str) -> SenalesTicket:
        """Calcula señales base (4D + léxico) para un ticket."""
