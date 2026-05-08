# Entregables Semana 5 — Experimentos A/B (baseline ML)

Este directorio contiene los artefactos **comparables** solicitados para la semana 5: **baseline + 2 variantes** (un cambio por vez), **validación (holdout + CV)**, **tabla** y **gráfico clave**, más **logs** reproducibles.

## Qué se ejecutó (A/B)

Script: [`scripts/run_week5_experiments.py`](../../../scripts/run_week5_experiments.py)

- **Baseline**: TF‑IDF *word unigrams* + LogisticRegression.
- **Var1**: **cambio único** → TF‑IDF *word (1,2)* (bigrams habilitados).
- **Var2**: **cambio único** → TF‑IDF *char (3,5)* (n‑gramas de caracteres).

> Nota: estos experimentos **no llaman a LLM** (costo 0). La evaluación de EarlyGate (LLM+léxico) se conserva aparte para la exposición en `docs/expo_early_gate_eval_300/`.

## Resultados comparables (tabla + 1 gráfico)

- **Tabla estándar**: [`results.csv`](results.csv)  
- **Resumen en Markdown**: [`week5_report.md`](week5_report.md)  
- **Gráfico clave** (F1‑macro baseline vs variantes): [`comparison_f1_macro.png`](comparison_f1_macro.png)

La métrica principal reportada es **F1‑macro** (multiclase). Secundarias: **accuracy** y tiempo.

## Validación / Split correcto (leakage)

Se reportan dos formas:

1. **Holdout estratificado** por `gold_mode` (reproducible por `seed`).
2. **GroupKFold** por `template_index` (**por grupo**) para reducir leakage por plantilla: ninguna plantilla aparece a la vez en train y test en un fold.

Esto cumple el requisito de “split correcto (estratificado / por grupo)” de la rúbrica.

## Feature set y pipeline (breve)

- **Feature set**: texto `requirement`.
- **Transformación**: TF‑IDF (según variante: word n‑grams o char n‑grams).
- **No leakage por fit**: el vectorizador se **ajusta solo en train** porque está encapsulado en un `Pipeline` de sklearn.

## Logs

Los logs se escriben como JSONL en `logs/week5/` (una línea por experimento con parámetros + métricas + tiempo). En `week5_report.md` se indica el log “oficial” de la corrida.

## Cómo correr (reproducible)

Desde la raíz del repo:

```bash
pip install -r requirements.txt
python scripts/run_week5_experiments.py
```

