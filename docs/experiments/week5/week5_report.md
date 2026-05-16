# Semana 5 — Experimentos A/B vs baseline

## Objetivo y diseño

Clasificar el modo de criticidad (`gold_mode`: play / pausa / stop) a partir del texto del campo `requirement`, con un **baseline ML** (sin LLM) y **dos variantes** que cambian **solo** la representación TF-IDF frente al baseline, para comparación controlada.

- **Baseline:** TF-IDF *word* unigramas + `LogisticRegression`.
- **Var1:** único cambio → TF-IDF *word* n-gramas (1, 2).
- **Var2:** único cambio → TF-IDF *char* n-gramas (3, 5).

- **Clasificador (igual en los tres):** `solver=lbfgs`, `max_iter=2000`, `random_state=42`.


## Metadatos de la corrida

- **Run id:** `20260516_004409`

- **Dataset:** `data/criticidad_cases/casos_gold_criticidad_v2.jsonl` (`n=300`)


## Validación

- **Holdout:** `StratifiedShuffleSplit` (un split), `test_size=0.2`, `random_state=42` (estratificado por `gold_mode`).

- **CV por grupos:** `GroupKFold(n_splits=5)` con `groups=template_index` (ningún fold mezcla la misma plantilla entre train y test).

- **Métrica principal:** F1-macro (multiclase). **Secundarias:** accuracy y tiempo de ajuste+predicción en holdout / tiempo total en los k folds para GKF.


## Tabla comparable

| exp      |   holdout_f1_macro |   holdout_accuracy |   holdout_time_sec |   gkf_f1_macro_mean |   gkf_f1_macro_std |   gkf_accuracy_mean |   gkf_time_sec |
|:---------|-------------------:|-------------------:|-------------------:|--------------------:|-------------------:|--------------------:|---------------:|
| baseline |                  1 |                  1 |             0.0403 |              0.9866 |             0.0165 |              0.9867 |         0.1756 |
| var1     |                  1 |                  1 |             0.0624 |              0.9899 |             0.0201 |              0.99   |         0.2466 |
| var2     |                  1 |                  1 |             0.5848 |              1      |             0      |              1      |         3.5976 |


## Lectura de resultados

- El **holdout** puede mostrar **F1-macro = 1.0** con un test pequeño y un problema relativamente separable; no implica ausencia de error en generalización.

- La evaluación **GroupKFold por plantilla** es la referencia más conservadora frente a **fuga por plantilla** (misma estructura de caso en train y test). Ahí se observa variación entre folds (barras de error en el gráfico).

- **Coste/tiempo:** Var2 (char n-grams) aumenta claramente el tiempo frente a Var1 y baseline; el trade-off conveniencia vs. ganancia marginal en F1 depende del despliegue.


## Gráfico clave

- Archivo: `docs/experiments/week5/comparison_f1_macro.png` (F1-macro holdout vs media GKF con σ).


## Feature set y pipeline (auditoría de leakage)

- **Features:** solo texto `requirement`.

- **Transformación:** `TfidfVectorizer` (word o char; rango de n-gramas según experimento). `min_df=1`.

- **Sin leakage por ajuste del vectorizador:** el vectorizador vive dentro de un `Pipeline` de sklearn; en cada split se llama a `fit` solo con filas de entrenamiento.

- **Etiqueta y agrupación:** `y = gold_mode`; grupos para GKF = `template_index` (relleno -1 si falta).


## Logs reproducibles

- `logs/week5/week5_experiments_20260516_004409.jsonl` — una línea JSON por experimento (config + métricas).

