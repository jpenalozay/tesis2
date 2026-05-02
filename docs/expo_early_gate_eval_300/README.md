# Resultado fijado — evaluación EarlyGate (300 casos)

Archivos congelados de la corrida del **2026-05-02** frente a `data/criticidad_cases/casos_gold_criticidad_v2.jsonl`.

- `predictions.csv` — predicción por requisito
- `summary.json` — métricas y matriz de confusión
- `confusion_matrix.png`, `f1_per_class.png` — figuras de la misma corrida
- `informe.md`, `classification_report.txt` — texto

El notebook `notebooks/eval_early_gate_vs_gold.ipynb` **carga solo estos archivos** (no vuelve a llamar a la API). Para una evaluación nueva, usar `scripts/eval_early_gate_corpus.py` con `DEEPSEEK_API_KEY`.
