# Análisis PASO 5 — Pasada 1 (diseño cierre IA08)

**Fecha:** 12 junio 2026 · **Referencia:** PPT `Maestria2_IA08.pptx` + plantilla informe Ex. Parcial UNI

---

## 1. Objetivos IA08 mapeados

| Requisito PPT IA08 | Implementación PASO 5 |
|--------------------|------------------------|
| MLOps ligero: trazabilidad, seed, config | `0_configuracion_cierre_examen.yaml` + tablero CSV |
| Tablero central experimentos | `1_tablero_experimentos_consolidado.csv` (13 filas) |
| Gap train/val/overfitting | `3_informe_gap_overfitting_calibracion.json` |
| Checklist informe 9 secciones | `2_checklist_examen_final_ia08.csv` (27 ítems) |
| Demo 10–12 min | `4_guia_demo_presentacion_10min.md` |
| Top-k corridas + HPO | sprint7 trial 68 en tablero |
| Auditoría global | `run_auditoria_entregable_completo.py` |

---

## 2. Diseño tablero

Filas consolidadas desde:

- PASO 0–2 (metadatos pipeline, sin métricas clasificación)
- PASO 3 Baseline/Var1/Var2 n=400 + holdout 120
- sprint7 HPO (F1-macro 0,701 test n=40 — no confundir con n=400)
- PASO 4 calibración isotónica ECE post-hoc

Columnas: `exp_id`, `paso`, `variante`, métricas clave, `notas_honestidad`.

---

## 3. Diseño gap/overfitting

Tres ejes de comparación:

1. **Eval n=400 vs holdout 120** — F1-stop, FNR-stop por variante
2. **Calibración** — ECE crudo vs isotónica n=400 vs holdout (fit train 280)
3. **Señales documentadas** — Var1 colapso D5; Var2 generalización favorable

---

## 4. Checklist (27 ítems)

- 12 requisitos IA08 (`IA08-01` … `IA08-12`)
- 10 secciones plantilla informe (`INF-01` … `INF-10`)
- 5 auditoría transversal (`AUD-01` … `AUD-05`)

Fuente de verdad métricas: `7_tabla_metricas_set_minimo_seis_por_variante.csv`.

---

## 5. Dependencias upstream

PASO 5 es **solo lectura** — no re-ejecuta API ni notebooks 0→4.

```bash
cd 5_cierre_examen_parcial_mlops
python run_cierre_examen.py
python run_auditoria_paso5.py
```

Ver pasada 2 para veredicto final.
