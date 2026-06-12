"""Genera 5_cierre_examen_parcial_mlops.ipynb — PASO 5 entregable."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NB = ROOT / "5_cierre_examen_parcial_mlops.ipynb"


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
        """# PASO 5 — Cierre examen parcial MLOps (IA08)

**Examen Parcial 3 · UNI**

1. Tablero central de experimentos (PASO 0→4 + sprint7 HPO)
2. Checklist examen final IA08 + plantilla informe 9 secciones
3. Análisis gap/overfitting (calibración train 280 vs eval 400 vs holdout 120)
4. Guía demo 10–12 min
5. Auditoría global entregable 0→4

Ejecutar primero: `run_cierre_examen.py` y `run_auditoria_paso5.py`.
"""
    ),
    code(
        """from pathlib import Path
import subprocess
import sys

ROOT = Path(".").resolve()
for script in ("run_cierre_examen.py", "run_auditoria_paso5.py"):
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, capture_output=True, text=True)
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
tab = pd.read_csv(ROOT / "1_tablero_experimentos_consolidado.csv")
chk = pd.read_csv(ROOT / "2_checklist_examen_final_ia08.csv")
gap = json.loads((ROOT / "3_informe_gap_overfitting_calibracion.json").read_text(encoding="utf-8"))
audit = json.loads((ROOT / "5_informe_auditoria_global_entregable_0_4.json").read_text(encoding="utf-8"))
resumen = json.loads((ROOT / "8_informe_resumen_paso5.json").read_text(encoding="utf-8"))

display(tab)
pct = (chk["estado"] == "CUMPLIDO").mean() * 100
print(f"Checklist: {pct:.1f}% cumplido ({(chk['estado']=='CUMPLIDO').sum()}/{len(chk)})")
display(chk[chk["estado"] != "CUMPLIDO"])
print("Gap eval vs holdout:", json.dumps(gap["gap_metricas_eval_vs_holdout"], indent=2))
print("Auditoría global:", audit["veredicto"])
print(json.dumps(resumen, indent=2))
"""
    ),
    md("## Veredicto\n\nVer `6_veredicto_final_entregable.md` y `4_guia_demo_presentacion_10min.md`."),
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
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Notebook: {NB}")
