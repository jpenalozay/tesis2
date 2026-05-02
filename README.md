# Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo

**Este `README.md` en la raíz es la guía principal del repositorio** ([versión en GitHub](https://github.com/jpenalozay/tesis2)).

## Autor

- **José Luis Peñaloza Yaurivilca** — [GitHub: jpenalozay](https://github.com/jpenalozay)
- **Repositorio:** [github.com/jpenalozay/tesis2](https://github.com/jpenalozay/tesis2)

## Qué contiene el repo (visión rápida)

| Bloque | Contenido |
|--------|-----------|
| **`data/criticidad_cases/`** | Corpus gold `play` / `pausa` / `stop` + EDA. |
| **`agentes/`** | Código del framework; gate temprano en `agentes/core/early_gate.py`. El árbol de `agentes/` está alineado con el bloque de trabajo local de la tesis (sin carpetas paralelas obligatorias en el remoto). |
| **`docs/`** | Incluye [`PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md`](docs/PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md) y **`docs/expo_early_gate_eval_300/`** — resultado fijado de la evaluación (300 casos). |
| **`scripts/`** | [`eval_early_gate_corpus.py`](scripts/eval_early_gate_corpus.py) — métricas vs gold (requiere API para corrida nueva). |
| **`notebooks/`** | [`eval_early_gate_vs_gold.ipynb`](notebooks/eval_early_gate_vs_gold.ipynb) — tablas y figuras embebidas leyendo `docs/expo_early_gate_eval_300/` (**sin API**). |

## Dataset (HF + corpus propio)

| Aspecto | Detalle |
|--------|---------|
| **Fuente HF** | [HumanEval](https://huggingface.co/datasets/openai_humaneval), [MBPP](https://huggingface.co/datasets/mbpp). Detalle: [`data/raw/README.md`](data/raw/README.md). |
| **Integridad** | `data/raw/manifest_v0.json` tras `python src/ingest_datasets_v0.py`. |
| **Corpus criticidad** | [`data/criticidad_cases/README.md`](data/criticidad_cases/README.md) — utilidades en `src/generate_criticidad_cases.py`, `src/verify_criticidad_cases.py`. |

### EDA corpus criticidad

Notebook [`data/criticidad_cases/EDA_criticidad_casos.ipynb`](data/criticidad_cases/EDA_criticidad_casos.ipynb): estadísticas, distribuciones, riesgos (desbalance, leakage léxico). Ejecutar desde la raíz:

```bash
cd data/criticidad_cases && python -m jupyter nbconvert --to notebook --execute EDA_criticidad_casos.ipynb --inplace
```

## Gate temprano y evaluación baseline

| Artefacto | Descripción |
|-----------|-------------|
| [`agentes/core/early_gate.py`](agentes/core/early_gate.py) | Clasificación LLM + fallback léxico. |
| [`agentes/core/coordinator_v3_gated.py`](agentes/core/coordinator_v3_gated.py) | Coordinador con resultado del gate. |
| [`docs/PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md`](docs/PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md) | Diseño del pipeline. |
| [`scripts/eval_early_gate_corpus.py`](scripts/eval_early_gate_corpus.py) | Evaluación contra gold (salidas en `reports/`, ignoradas por git). |
| [`notebooks/eval_early_gate_vs_gold.ipynb`](notebooks/eval_early_gate_vs_gold.ipynb) | Vista para exposición (usa artefactos en [`docs/expo_early_gate_eval_300/`](docs/expo_early_gate_eval_300/README.md)). |

Configuración LLM: copiar [`.env.example`](.env.example) → `.env` con `DEEPSEEK_API_KEY` (no versionar `.env`).

```bash
pip install -r requirements.txt
python scripts/eval_early_gate_corpus.py --limit 10   # prueba
python scripts/eval_early_gate_corpus.py             # 300 casos (API)
```

## Requisitos

```bash
pip install -r requirements.txt
```

También: [`agentes/requirements.txt`](agentes/requirements.txt) para el paquete `agentes/`.

## Estructura del repositorio

```
.
├── agentes/           # Framework (EarlyGate, coordinadores, agentes)
├── data/
│   ├── criticidad_cases/
│   ├── raw/ interim/ processed/
├── docs/
│   └── expo_early_gate_eval_300/   # corrida 300 casos versionada (expo)
├── notebooks/
├── scripts/
├── src/
├── logs/ slides/
├── README.md          # ← este archivo (fuente principal)
├── requirements.txt
└── pyproject.toml
```

## Pipeline datos (ingesta / EDA HF)

1. `python src/ingest_datasets_v0.py`
2. `python src/preprocesamiento.py` (cuando aplique)
3. Exploración: `notebooks/EDA_basico.ipynb` (requiere datos paso 1)
4. EDA criticidad: comando arriba para `EDA_criticidad_casos.ipynb`
5. Trazas: `logs/ingesta.log` si aplica

## Roadmap

- Baselines adicionales (p. ej. TF-IDF + regresión logística vs EarlyGate).
- Calibración de umbrales del gate para la clase `pausa`.

## Licencia

Uso académico — tesis de maestría (marco del programa).
