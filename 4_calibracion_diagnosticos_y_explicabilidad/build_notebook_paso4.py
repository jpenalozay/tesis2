"""Genera 4_calibracion_diagnosticos_y_explicabilidad.ipynb — PASO 4 entregable."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NB = ROOT / "4_calibracion_diagnosticos_y_explicabilidad.ipynb"


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
        """# PASO 4 — Calibración, diagnósticos y explicabilidad (IA06)

**Examen Parcial 3 · UNI**

1. Calibración post-hoc (Platt / isotónica) — ECE y Brier antes/después
2. Ablación por componente middleware (Gate B, fuzzy, RAG, ejes 4D)
3. Explicabilidad — permutation importance sobre overrides
4. Sub-análisis piloto n=40 CrewAI (sin reclamar n=400)

**Salvedad metodológica:** Var1 = 10 % CrewAI real (D5) + 90 % abstención pausa (Chow 1970). Var2 es la contribución principal. No se escala CrewAI a n=400 por costo/evidencia; sub-análisis n=40 documenta capacidad del agente.

Ejecutar primero: `run_calibracion_diagnosticos.py` (lee cache PASO 3, sin re-API).
"""
    ),
    code(
        """from pathlib import Path
import subprocess
import sys

ROOT = Path(".").resolve()
script = ROOT / "run_calibracion_diagnosticos.py"
result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit(result.returncode)
"""
    ),
    code(
        """import json
from pathlib import Path

import pandas as pd

ROOT = Path(".").resolve()
cal = pd.read_csv(ROOT / "1_tabla_calibracion_ece_brier_antes_despues.csv")
abl = pd.read_csv(ROOT / "3_tabla_ablacion_componentes_middleware.csv")
imp = pd.read_csv(ROOT / "5_tabla_importancia_senales_overrides.csv")
pilot = pd.read_csv(ROOT / "7_tabla_metricas_piloto_crewai_n40.csv")
resumen = json.loads((ROOT / "8_informe_resumen_paso4.json").read_text(encoding="utf-8"))

display(cal.groupby(["variante", "fase", "metodo_calibracion"])[["ECE", "Brier"]].first())
display(abl[["componente_ablado", "F1-stop", "EC", "override_rate", "delta_F1-stop", "delta_EC"]])
display(imp.head(8))
display(pilot[["n_piloto", "F1-macro (Macro-averaged F1)", "F1-stop (F1-critical)", "FNR-stop (False Negative Rate stop)"]])
print(json.dumps(resumen["calibracion_resumen"], indent=2))
"""
    ),
    md("## Figuras\n\nVer `2_figura_curvas_calibracion_tres_variantes.png`, `4_figura_ablacion_delta_f1_stop_ec.png`, `6_figura_importancia_senales_gate_b.png`."),
    code(
        """from IPython.display import Image, display
from pathlib import Path

ROOT = Path(".").resolve()
for fig in [
    "2_figura_curvas_calibracion_tres_variantes.png",
    "4_figura_ablacion_delta_f1_stop_ec.png",
    "6_figura_importancia_senales_gate_b.png",
]:
    p = ROOT / fig
    if p.exists():
        display(Image(filename=str(p)))
"""
    ),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook escrito: {NB}")
