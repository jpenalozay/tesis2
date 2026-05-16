# Semana 5 — Experimentos A/B vs baseline

- **Run id:** `20260508_150159`

- **Dataset:** `data/criticidad_cases/casos_gold_criticidad_v2.jsonl`

- **Holdout:** test_size=0.2, seed=42

- **Cross-validation:** GroupKFold(k=5) por `template_index` (reduce leakage por plantilla)


## Tabla comparable

| exp      |   holdout_f1_macro |   holdout_accuracy |   holdout_time_sec |   gkf_f1_macro_mean |   gkf_f1_macro_std |   gkf_accuracy_mean |   gkf_time_sec |
|:---------|-------------------:|-------------------:|-------------------:|--------------------:|-------------------:|--------------------:|---------------:|
| baseline |                  1 |                  1 |          0.0143624 |            0.986556 |          0.0164661 |            0.986667 |      0.0918948 |
| var1     |                  1 |                  1 |          0.0237283 |            0.989943 |          0.0201131 |            0.99     |      0.133865  |
| var2     |                  1 |                  1 |          0.402002  |            1        |          0         |            1        |      1.49063   |


## Gráfico clave

- `docs/experiments/week5/comparison_f1_macro.png`


## Feature set y split (auditoría)

- **Features usadas:** `requirement` (texto). TF-IDF según variante.

- **Transformaciones:** tokenización TF-IDF (word o char n-grams). `fit` solo en train por construcción del pipeline.

- **Split/leakage:** además de holdout estratificado, se reporta GroupKFold por `template_index` para evitar que la misma plantilla aparezca en train y test.


## Logs

- `logs/week5/week5_experiments_20260508_150159.jsonl` (una línea JSON por experimento)

