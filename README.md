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
│   ├── raw/           # orígenes y manifiesto (ingesta)
│   ├── interim/      # intermedio (opcional)
│   └── processed/    # listos para modelado / análisis
├── logs/             # trazas de pipeline (p. ej. salida de ingesta)
├── notebooks/        # EDA, baselines, experimentos
├── slides/           # presentaciones
├── src/              # ingesta, preprocesamiento, utilidades
├── agentes/          # framework multi-agente (código principal)
├── docs/             # documentación adicional
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

3. **Exploración** — abrir `notebooks/EDA_basico.ipynb` (ver `notebooks/README.md`); requiere `jupyter` y datos generados en el paso 1.

4. **Trazas** — revisar consola y, si aplica, `logs/ingesta.log`.

## Resultados esperados (mínimos, etapa actual)

- JSONL bajo `data/raw/…` y `data/raw/manifest_v0.json`.
- Registro de la ingesta en `logs/ingesta.log` (local).
- Preparación de `data/processed/` cuando el preprocesamiento esté conectado.

## Desarrollo del framework

```bash
cd agentes
```

Detalle: `agentes/README.md`, `agentes/README_FINAL.md`.

## Roadmap

- Avanzar preprocesamiento y notebooks de EDA / línea base (métricas acordes al tipo de tarea).
- Integrar evaluación con el orquestador en `agentes/`.
- Sincronizar presentaciones y resultados bajo `slides/` y `logs/`.

## Licencia

Uso académico — tesis de maestría (marco del programa).
