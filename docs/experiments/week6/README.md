# Semana 6 — Experimentos A/B (módulo criticidad)

Entrega sprint: comparación **baseline TF-IDF** vs **Var1/Var2** (+ referencia **EarlyGate léxico**, sin LLM).

## Artefactos

| Archivo | Descripción |
|---------|-------------|
| `results.csv` | Tabla comparable (holdout + GroupKFold) |
| `summary.json` | Decisión de variante + F1 por clase |
| `f1_por_clase_baseline_vs_mejor.png` | Gráfico representativo |

## Reproducibilidad

Desde `tesis2/` con venv activo (`scikit-learn`, `pandas`, `matplotlib`):

```bash
python scripts/run_week6_experiments.py
python scripts/run_week6_experiments.py --copy-to-reports
```

Notebook de entrega (misma lógica + narrativa para slide):

```bash
jupyter notebook notebooks/semana6_entrega_criticidad_ab.ipynb
```

Baseline histórico (repo padre, semana 5):

```bash
cd .. && python scripts/run_week5_experiments.py
```

## Validación

- **Holdout:** `StratifiedShuffleSplit`, `test_size=0.2`, `random_state=42`
- **CV:** `GroupKFold(n_splits=5)` por `template_index` (anti-leakage de plantilla)
- **Features:** solo `requirement` (sin `tags`, `id`, etc.)
- **Métricas:** F1-macro + Cohen κ

## EarlyGate LLM

No se ejecuta por defecto (coste). Ver celda opcional `RUN_EARLY_LLM = False` en el notebook y `eval_early_gate_vs_gold.ipynb`.
