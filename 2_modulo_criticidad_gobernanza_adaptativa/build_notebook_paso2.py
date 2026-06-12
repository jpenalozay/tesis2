"""Genera 2_modulo_criticidad_gobernanza_adaptativa.ipynb — PASO 2 entregable."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NB = ROOT / "2_modulo_criticidad_gobernanza_adaptativa.ipynb"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md(
        """# PASO 2 — Módulo criticidad y gobernanza adaptativa

**Examen Parcial 3 · Proyecto de Investigación 2 · UNI**

Motor **play / pausa / stop** con dual gate (D1), RagPlugin obligatorio Var2 (D2),
validación gold v2 subconjunto (D3), HITL async simulado en CSV (D4).

| Gate | Rol |
|------|-----|
| **Gate A (pre-LLM)** | PolicyEngine decide antes del agente |
| **Gate B (post-agente)** | Override si agente simulado contradice riesgo |

**Semilla:** `seed = 42` · **n eval:** 400

**Honestidad:** `agent_label` se simula desde mayoría RAG (sin API CrewAI).
"""
    ),
    code(
        """# ── Configuración ───────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import f1_score, confusion_matrix

ROOT = Path(".").resolve()
PLUGINS = ROOT / "plugins"
if str(PLUGINS) not in sys.path:
    sys.path.insert(0, str(PLUGINS))

from importlib import import_module

rag_mod = import_module("1_plugin_rag_recuperacion")
cost_mod = import_module("2_plugin_costo_tokens_bucles")
policy_mod = import_module("3_motor_politica_play_pausa_stop")
hitl_mod = import_module("4_puerta_hitl_sincrono_asincrono")

RagPlugin = rag_mod.RagPlugin
load_neighbors_table = rag_mod.load_neighbors_table
neighbors_by_hash = rag_mod.neighbors_by_hash
CostPlugin = cost_mod.CostPlugin
PolicyEngine = policy_mod.PolicyEngine
predict_robust = policy_mod.predict_robust
build_features = policy_mod.build_features
majority_label = policy_mod.majority_label
compute_risk_4d_en = policy_mod.compute_risk_4d_en
lexical_stop_flag = policy_mod.lexical_stop_flag
expected_cost = policy_mod.expected_cost
HitlGateway = hitl_mod.HitlGateway

CFG_PATH = ROOT / "0_configuracion_modulo_criticidad.yaml"
with CFG_PATH.open(encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

SEED = int(CFG["seed"])
CLASSES = ["play", "pausa", "stop"]

def resolve(p: str) -> Path:
    return (ROOT / p).resolve()

PATH_EVAL = resolve(CFG["paths"]["eval"])
PATH_RAG = resolve(CFG["paths"]["rag_hibrido"])
PATH_RAG_FB = resolve(CFG["paths"]["rag_fallback"])
PATH_ANTI = resolve(CFG["paths"]["anti_fuga"])
PATH_WIN = resolve(CFG["paths"]["winning_config"])
PATH_GOLD = resolve(CFG["paths"]["gold_v2"])

print(f"ROOT={ROOT}")
print(f"eval exists={PATH_EVAL.exists()}, rag exists={PATH_RAG.exists()}")
"""
    ),
    code(
        """# ── Carga parámetros política (winning_config sprint7) ──────────────────
policy_params = {
    "mode": CFG["policy"]["mode"],
    "weights": dict(CFG["policy"]["weights"]),
    "threshold_stop": CFG["policy"]["threshold_stop"],
    "threshold_pausa": CFG["policy"]["threshold_pausa"],
    "risk_stop_floor": CFG["policy"]["risk_stop_floor"],
    "p_stop_floor": CFG["policy"]["p_stop_floor"],
    "stop_cost_threshold": CFG["policy"]["stop_cost_threshold"],
    "pause_uncertainty": CFG["policy"]["pause_uncertainty"],
}
winning_source = "yaml_fallback"
if PATH_WIN.exists():
    win = json.loads(PATH_WIN.read_text(encoding="utf-8"))
    p = win.get("params", {})
    policy_params = {
        "mode": p.get("mode", policy_params["mode"]),
        "weights": dict(p.get("weights", policy_params["weights"])),
        "threshold_stop": p.get("threshold_stop", policy_params["threshold_stop"]),
        "threshold_pausa": p.get("threshold_pausa", policy_params["threshold_pausa"]),
        "risk_stop_floor": p.get("risk_stop_floor", policy_params["risk_stop_floor"]),
        "p_stop_floor": p.get("p_stop_floor", policy_params["p_stop_floor"]),
        "stop_cost_threshold": p.get("stop_cost_threshold", policy_params["stop_cost_threshold"]),
        "pause_uncertainty": p.get("pause_uncertainty", policy_params["pause_uncertainty"]),
    }
    winning_source = str(PATH_WIN)

cost_pause = float(CFG["cost_matrix"]["pause_hitl"])
cost_stop = float(CFG["cost_matrix"]["stop_hitl"])
cost_fn_stop = float(CFG["cost_matrix"]["false_negative_stop"])

print(f"policy mode={policy_params['mode']} source={winning_source}")
"""
    ),
    code(
        """# ── Carga datos PASO 0/1 ────────────────────────────────────────────────
df_eval = pd.read_csv(PATH_EVAL)
assert len(df_eval) == CFG["n_eval"], f"n_eval={len(df_eval)}"

df_rag = load_neighbors_table(PATH_RAG, PATH_RAG_FB)
neighbors_map = neighbors_by_hash(df_rag)
assert len(df_rag) == CFG["n_eval"] * CFG["top_k"], f"rag rows={len(df_rag)}"

anti_fuga = json.loads(PATH_ANTI.read_text(encoding="utf-8")) if PATH_ANTI.exists() else {}

rag_plugin = RagPlugin(neighbors_map)
cost_plugin = CostPlugin()
policy_engine = PolicyEngine(policy_params, rag_obligatorio=CFG["decisiones"]["D2_rag_plugin_obligatorio_var2"])
hitl_gateway = HitlGateway(
    play_mode=CFG["hitl"]["play"],
    pausa_mode=CFG["hitl"]["pausa"],
    stop_mode=CFG["hitl"]["stop"],
)

print(f"n_eval={len(df_eval)} rag_neighbors={len(df_rag)} unique_queries={len(neighbors_map)}")
"""
    ),
    code(
        """# ── Simulación agent_label (sin API) ─────────────────────────────────────
def simulate_agent_label(text: str, neighbors: list, rag_majority: str, risk: float) -> tuple[str, float]:
    \"\"\"Proxy Var1 sin API: etiqueta = mayoría RAG top-k (puede contradecir Gate A).\"\"\"
    if rag_majority in CLASSES:
        conf = 0.55 + 0.15 * min(len(neighbors), 5) / 5.0
        return rag_majority, min(conf, 0.85)
    return "pausa", 0.50
"""
    ),
    code(
        """# ── Pipeline señales + Gate A + Gate B ───────────────────────────────────
senales_rows: list[dict[str, Any]] = []
gate_a_rows: list[dict[str, Any]] = []
gate_b_rows: list[dict[str, Any]] = []
hitl_rows: list[dict[str, Any]] = []

for pos, row in df_eval.reset_index(drop=True).iterrows():
    text = str(row["text"])
    th = str(row["text_hash"])
    true_label = str(row["thesis_class"])
    ns = neighbors_map.get(th, [])
    rag_maj, _ = majority_label(ns)
    risk, dims = compute_risk_4d_en(text)
    rag_enrich = rag_plugin.enrich(th, ns)
    agent_label, agent_conf = simulate_agent_label(text, ns, rag_maj, risk)

    cost_pre = cost_plugin.estimate()
    senales_rows.append({
        "query_idx": int(pos),
        "text_hash": th,
        "true_label": true_label,
        "risk_4d": round(risk, 6),
        "lexical_stop": lexical_stop_flag(text),
        "I_db": round(dims["I_db"], 6),
        "I_mem": round(dims["I_mem"], 6),
        "I_sec": round(dims["I_sec"], 6),
        "I_dat": round(dims["I_dat"], 6),
        "neighbor_entropy": round(float(rag_enrich["neighbor_entropy"]), 6),
        "mean_distance": round(float(rag_enrich["mean_distance"]), 6),
        "class_consensus": round(float(rag_enrich["class_consensus"]), 6),
        "conformal_set_size": int(rag_enrich["conformal_set_size"]),
        "rag_uncertainty": round(float(rag_enrich["rag_uncertainty"]), 6),
        "agent_label_sim": agent_label,
        "agent_confidence_sim": agent_conf,
        "token_cost_proxy": cost_pre.token_cost_proxy,
        "loop_retry_proxy": cost_pre.loop_retry_proxy,
        "plan_entropy": round(float(rag_enrich["neighbor_entropy"]), 6),
        "agent_disagreement": round(abs({"play":0,"pausa":0.5,"stop":1.0}.get(agent_label,0.5) - {"play":0,"pausa":0.5,"stop":1.0}.get(rag_maj,0.5)), 6),
    })

    ga = policy_engine.decide_gate_a(text, ns, rag_enrich, agent_label, agent_conf)
    gate_a_rows.append({
        "query_idx": int(pos),
        "text_hash": th,
        "true_label": true_label,
        "gate": "A",
        "decision": ga["decision"],
        "score": round(ga["score"], 6),
        "trace": " | ".join(ga["trace"]),
        "risk_4d": round(ga["features"]["risk_4d"], 6),
        "uncertainty": round(ga["features"]["uncertainty"], 6),
        "p_stop": round(ga["features"]["p_stop"], 6),
    })

    gb = policy_engine.decide_gate_b(ga["decision"], agent_label, ga["features"])
    gate_b_rows.append({
        "query_idx": int(pos),
        "text_hash": th,
        "true_label": true_label,
        "gate": "B",
        "agent_label_sim": agent_label,
        "decision_gate_a": ga["decision"],
        "decision_final": gb["decision"],
        "override": gb["override"],
        "trace": " | ".join(gb["trace"]),
    })

    hitl = hitl_gateway.assign(ga["decision"])
    hitl_rows.append({
        "query_idx": int(pos),
        "text_hash": th,
        "true_label": true_label,
        "decision_gate_a": ga["decision"],
        **hitl.to_dict(),
    })

df_senales = pd.DataFrame(senales_rows)
df_gate_a = pd.DataFrame(gate_a_rows)
df_gate_b = pd.DataFrame(gate_b_rows)
df_hitl = pd.DataFrame(hitl_rows)

print(f"senales={len(df_senales)} gate_a={len(df_gate_a)} gate_b={len(df_gate_b)}")
print(df_gate_a["decision"].value_counts().to_dict())
"""
    ),
    code(
        """# ── Métricas Capa A (C-01..C-06) ─────────────────────────────────────────
y_true = df_gate_a["true_label"].astype(str).tolist()
y_gate_a = df_gate_a["decision"].astype(str).tolist()
y_gate_b = df_gate_b["decision_final"].astype(str).tolist()

f1_macro_a = f1_score(y_true, y_gate_a, labels=CLASSES, average="macro", zero_division=0)
f1_per_a = f1_score(y_true, y_gate_a, labels=CLASSES, average=None, zero_division=0)
f1_stop_a = float(f1_per_a[2])

f1_macro_b = f1_score(y_true, y_gate_b, labels=CLASSES, average="macro", zero_division=0)
f1_per_b = f1_score(y_true, y_gate_b, labels=CLASSES, average=None, zero_division=0)
f1_stop_b = float(f1_per_b[2])

# ECE (bins de confianza = score Gate A)
scores = df_gate_a["score"].astype(float).values
correct = (df_gate_a["decision"].astype(str) == df_gate_a["true_label"].astype(str)).astype(int).values
n_bins = 10
bin_edges = np.linspace(0, 1, n_bins + 1)
ece = 0.0
for i in range(n_bins):
    mask = (scores >= bin_edges[i]) & (scores < bin_edges[i + 1] if i < n_bins - 1 else scores <= bin_edges[i + 1])
    if mask.sum() == 0:
        continue
    acc = correct[mask].mean()
    conf = scores[mask].mean()
    ece += abs(conf - acc) * mask.sum() / len(scores)

ec_a = expected_cost(y_true, y_gate_a, cost_pause, cost_stop, cost_fn_stop)
ec_b = expected_cost(y_true, y_gate_b, cost_pause, cost_stop, cost_fn_stop)

cm = confusion_matrix(y_true, y_gate_a, labels=CLASSES)
tp_stop = cm[2, 2]
fn_stop = cm[2, 0] + cm[2, 1]
fnr_stop = fn_stop / max(tp_stop + fn_stop, 1)

override_rate = float(df_gate_b["override"].astype(bool).mean())

metricas = [
    {"metrica_id": "C-01", "nombre": "F1-macro (Gate A)", "valor": round(f1_macro_a, 6), "gate": "A"},
    {"metrica_id": "C-02", "nombre": "F1-stop (Gate A)", "valor": round(f1_stop_a, 6), "gate": "A"},
    {"metrica_id": "C-03", "nombre": "ECE (Gate A)", "valor": round(ece, 6), "gate": "A"},
    {"metrica_id": "C-04", "nombre": "EC ex-CEPA (Gate A)", "valor": round(ec_a, 6), "gate": "A"},
    {"metrica_id": "C-05", "nombre": "FNR-stop (Gate A)", "valor": round(fnr_stop, 6), "gate": "A"},
    {"metrica_id": "C-06", "nombre": "Override rate (Gate B)", "valor": round(override_rate, 6), "gate": "B"},
    {"metrica_id": "C-01", "nombre": "F1-macro (Gate B)", "valor": round(f1_macro_b, 6), "gate": "B"},
    {"metrica_id": "C-02", "nombre": "F1-stop (Gate B)", "valor": round(f1_stop_b, 6), "gate": "B"},
    {"metrica_id": "C-04", "nombre": "EC ex-CEPA (Gate B)", "valor": round(ec_b, 6), "gate": "B"},
]
df_metricas = pd.DataFrame(metricas)
print(df_metricas)
"""
    ),
    code(
        """# ── Gold v2 subconjunto (D3) ─────────────────────────────────────────────
gold_report: dict[str, Any] = {"enabled": CFG["decisiones"]["D3_calibrar_gold_v2"], "path": str(PATH_GOLD)}
if PATH_GOLD.exists() and CFG["decisiones"]["D3_calibrar_gold_v2"]:
    gold_rows = [json.loads(line) for line in PATH_GOLD.read_text(encoding="utf-8").splitlines() if line.strip()]
    gold_subset = gold_rows[:50]
    gold_preds = []
    for g in gold_subset:
        req = str(g.get("requirement", ""))
        risk, _ = compute_risk_4d_en(req)
        # gold ES: usar risk thresholds adaptados
        if risk >= 0.45:
            pred = "stop"
        elif risk >= 0.20:
            pred = "pausa"
        else:
            pred = "play"
        gold_preds.append({
            "id": g.get("id"),
            "gold_mode": g.get("gold_mode"),
            "pred": pred,
            "risk_4d": round(risk, 6),
            "match": pred == g.get("gold_mode"),
        })
    df_gold = pd.DataFrame(gold_preds)
    acc_gold = float(df_gold["match"].mean())
    gold_report.update({
        "n_total_file": len(gold_rows),
        "n_subset": len(gold_subset),
        "accuracy_subset": acc_gold,
        "note": "Validación proxy 4D EN sobre requisitos ES gold v2 (limitación documentada)",
    })
else:
    gold_report["note"] = "gold v2 no disponible o D3 desactivado"

print(json.dumps(gold_report, indent=2, ensure_ascii=False))
"""
    ),
    code(
        """# ── Artefactos de salida 0_–7_ ───────────────────────────────────────────
mapeo_ejes = pd.DataFrame([
    {"eje": "riesgo_operativo", "senal": "risk_4d", "componente": "SignalProvider 4D", "fuente": "texto ticket"},
    {"eje": "riesgo_operativo", "senal": "lexical_stop", "componente": "EarlyGate EN", "fuente": "keywords"},
    {"eje": "incertidumbre_plan", "senal": "neighbor_entropy", "componente": "RagPlugin", "fuente": "7_tabla_recuperacion_hibrida"},
    {"eje": "incertidumbre_plan", "senal": "agent_disagreement", "componente": "SignalProvider", "fuente": "agente sim vs RAG"},
    {"eje": "costo_ineficiencia", "senal": "token_cost_proxy", "componente": "CostPlugin stub", "fuente": "batch constante"},
    {"eje": "costo_ineficiencia", "senal": "loop_retry_proxy", "componente": "CostPlugin stub", "fuente": "batch constante"},
])

arquitectura = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "seed": SEED,
    "n_eval": len(df_eval),
    "decisiones_D1_D5": CFG["decisiones"],
    "dual_gate": CFG["decisiones"]["D1_dual_gate"],
    "rag_plugin_obligatorio": CFG["decisiones"]["D2_rag_plugin_obligatorio_var2"],
    "policy_params_source": winning_source,
    "policy_mode": policy_params["mode"],
    "plugins": [
        "0_interfaz_proveedor_senales.py",
        "1_plugin_rag_recuperacion.py",
        "2_plugin_costo_tokens_bucles.py",
        "3_motor_politica_play_pausa_stop.py",
        "4_puerta_hitl_sincrono_asincrono.py",
    ],
    "anti_fuga_ref": anti_fuga.get("checks", {}).get("history_eval_hash_overlap"),
    "agent_label_note": "Simulado desde mayoría RAG top-k (sin API CrewAI)",
    "gold_v2": gold_report,
}

hitl_by_class = hitl_gateway.summary_by_class(
    df_gate_a["decision"].astype(str).tolist(),
    df_gate_a["true_label"].astype(str).tolist(),
)

auditoria_modulo = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "checks": {
        "n_eval": len(df_eval),
        "n_senales": len(df_senales),
        "n_gate_a": len(df_gate_a),
        "n_gate_b": len(df_gate_b),
        "n_rag_rows_upstream": len(df_rag),
        "history_eval_overlap": anti_fuga.get("checks", {}).get("history_eval_hash_overlap"),
        "f1_macro_gate_a": round(f1_macro_a, 6),
        "override_rate": round(override_rate, 6),
    },
    "distribution_gate_a": df_gate_a["decision"].value_counts().to_dict(),
    "veredicto": "OK" if len(df_eval) == 400 and len(df_senales) == 400 else "REVISAR",
}

(ROOT / "0_informe_arquitectura_modulo_criticidad.json").write_text(
    json.dumps(arquitectura, indent=2, ensure_ascii=False), encoding="utf-8"
)
mapeo_ejes.to_csv(ROOT / "1_tabla_mapeo_ejes_evaluacion_criticidad.csv", index=False)
df_senales.to_csv(ROOT / "2_tabla_senales_por_ticket_n400.csv", index=False)
df_gate_a.to_csv(ROOT / "3_tabla_decisiones_politica_play_pausa_stop_n400.csv", index=False)
df_gate_b.to_csv(ROOT / "4_tabla_decisiones_gate_b_post_agente_simulado_n400.csv", index=False)
pd.DataFrame(hitl_by_class).to_csv(ROOT / "5_tabla_modos_hitl_asignados_por_clase.csv", index=False)
df_metricas.to_csv(ROOT / "6_tabla_metricas_modulo_criticidad_capa_a.csv", index=False)
(ROOT / "7_informe_auditoria_pasada1_modulo_criticidad.json").write_text(
    json.dumps(auditoria_modulo, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("Artefactos 0_–7_ escritos en", ROOT)
"""
    ),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"},
    },
    "cells": cells,
}

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook generado: {NB}")
