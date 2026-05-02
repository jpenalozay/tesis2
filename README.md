# Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo

## Título y descripción breve

- **Proyecto:** framework multi-agente con gestión dinámica de criticidad y supervisión humana adaptativa (HITL), orientado a desarrollo de software.
## Autor

- **José Luis Peñaloza Yaurivilca** — [GitHub: jpenalozay](https://github.com/jpenalozay)

- **Repositorio:** [https://github.com/jpenalozay/tesis2](https://github.com/jpenalozay/tesis2)

## Dataset

| Aspecto | Detalle |
|--------|---------|
| **Fuente** | [HumanEval](https://huggingface.co/datasets/openai_humaneval) y [MBPP](https://huggingface.co/datasets/mbpp) (Hugging Face). |
| **Descripción** | Registros, variables y convención de archivos: [`data/raw/README.md`](data/raw/README.md). |
| **Versión / integridad** | `data/raw/manifest_v0.json` (fecha UTC, tamaños, SHA-256) tras `python src/ingest_datasets_v0.py`. |

**Corpus de criticidad (tesis):** requerimientos etiquetados `play` / `pausa` / `stop` en [`data/criticidad_cases/`](data/criticidad_cases/README.md). Utilidades: [`src/generate_criticidad_cases.py`](src/generate_criticidad_cases.py), [`src/verify_criticidad_cases.py`](src/verify_criticidad_cases.py). La procedencia de los textos no se documenta aquí.

### EDA del corpus de criticidad (`EDA_criticidad_casos.ipynb`)

Notebook listo para presentación/defensa, con **comentarios por figura** y secciones alineadas al análisis exploratorio estándar:

| Contenido | Descripción |
|-----------|-------------|
| **Estadísticas descriptivas** | Tipos, valores nulos, `describe()` sobre longitudes (`n_chars`, `n_words`), índice `chars_por_palabra`, tabla cruzada `gold_mode` × `difficulty_hint` cuando existe. |
| **Distribuciones** | Frecuencia de etiquetas gold (Fig. 1), histogramas y boxplots de longitud (Fig. 2–3), violín de palabras (Fig. 4), heatmap `gold_mode` × `template_index` (Fig. 5), densidad léxica (Fig. 6). |
| **Riesgos** | **Desbalance:** χ² de referencia vs reparto equiprobable 33/33/33; **leakage léxico:** heatmap de keywords por clase (Fig. 7); **drift:** alcances en corpus estático vs monitorización en producción. |
| **Síntesis** | Tabla resumen para tesis y siguiente paso experimental (Sentinel vs `gold_mode`). |

Ejecutar desde la raíz del repo (requiere `jupyter`):

```bash
cd data/criticidad_cases && python -m jupyter nbconvert --to notebook --execute EDA_criticidad_casos.ipynb --inplace
```

## Gate temprano (criticidad) y evaluación

| Artefacto | Descripción |
|-----------|-------------|
| [`agentes/core/early_gate.py`](agentes/core/early_gate.py) | Clasificación `play` / `pausa` / `stop` (LLM + fallback léxico). |
| [`agentes/core/coordinator_v3_gated.py`](agentes/core/coordinator_v3_gated.py) | Orquestador que adjunta el resultado de EarlyGate. |
| [`docs/PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md`](docs/PIPELINE_CRITICIDAD_Y_GATE_TEMPRANO.md) | Diseño del pipeline y del gate. |
| [`scripts/eval_early_gate_corpus.py`](scripts/eval_early_gate_corpus.py) | Evalúa `EarlyGate.decide` frente a `gold_mode` en el JSONL (métricas, CSV, figuras en `reports/`, no versionado). |
| [`notebooks/eval_early_gate_vs_gold.ipynb`](notebooks/eval_early_gate_vs_gold.ipynb) | Misma evaluación con salida interactiva. |

Configuración: copiar [`.env.example`](.env.example) a `.env` y definir `DEEPSEEK_API_KEY` (no subir `.env` al repositorio). Entorno Python: `python -m venv .venv` y `pip install -r requirements.txt`.

```bash
python scripts/eval_early_gate_corpus.py --limit 10   # prueba rápida
python scripts/eval_early_gate_corpus.py              # 300 casos (API)
```

## Requisitos

Con `pip` (recomendado para reproducir):

```bash
pip install -r requirements.txt
```

Dependencias del módulo del framework: `agentes/requirements.txt`.

## Estructura del repositorio

Árbol lógico:

```
.
├── data/
│   ├── raw/               # ingesta HF (si aplica)
│   ├── criticidad_cases/  # corpus gold play/pausa/stop + EDA
│   ├── interim/
│   └── processed/
├── scripts/           # evaluación EarlyGate vs gold, etc.
├── logs/              # trazas de pipeline
├── notebooks/         # EDA, evaluación interactiva
├── slides/
├── src/               # ingesta, utilidades corpus criticidad
├── agentes/           # framework (EarlyGate, CoordinatorV3Gated, …)
├── docs/
├── README.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

## Cómo ejecutar el pipeline (datos)

1. **Ingesta** — descarga o materializa el dataset y el manifiesto.

```bash
python src/ingest_datasets_v0.py
```

2. **Preprocesamiento** (cuando esté implementado) — de `data/raw` hacia `data/interim` / `data/processed`.

```bash
python src/preprocesamiento.py
```

3. **Exploración — datasets Hugging Face** — abrir `notebooks/EDA_basico.ipynb` (ver `notebooks/README.md`); requiere `jupyter` y datos generados en el paso 1.

4. **EDA — corpus de criticidad** — con `data/criticidad_cases/casos_gold_criticidad_v2.jsonl`, ejecutar `data/criticidad_cases/EDA_criticidad_casos.ipynb` (comando en la subsección anterior).

5. **Trazas** — revisar consola y, si aplica, `logs/ingesta.log`.

## Resultados esperados (mínimos, etapa actual)

- JSONL bajo `data/raw/…` y `data/raw/manifest_v0.json`.
- Registro de la ingesta en `logs/ingesta.log` (local).
- Corpus `data/criticidad_cases/casos_gold_criticidad_v2.jsonl` y notebook EDA ejecutado (salidas embebidas opcionales).
- Preparación de `data/processed/` cuando el preprocesamiento esté conectado.

## Desarrollo del framework

```bash
cd agentes
```

Detalle: `agentes/README.md`, `agentes/README_FINAL.md`.

## Roadmap

- Avanzar preprocesamiento y líneas base adicionales (p. ej. TF-IDF + regresión logística vs EarlyGate).
- Calibrar umbrales de EarlyGate para mejorar la clase `pausa` frente al gold.
- Sincronizar presentaciones y resultados bajo `slides/` y `logs/`.

## Licencia

Uso académico — tesis de maestría (marco del programa).
