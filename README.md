# Tesis: Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo

**Repositorio académico** del proyecto de maestría. El **código ejecutable del framework** (orquestación, agentes, API, Docker) vive en la carpeta [`agentes/`](agentes/); aquí se organizan datos, notebooks y scripts de ingesta alineados al entregable **Track B** (estructura base, dataset, ingesta v0, plan de recuperación).

- **Repositorio remoto:** [https://github.com/jpenalozay/tesis2](https://github.com/jpenalozay/tesis2)

## Integrantes

- **José Luis Peñaloza Yaurivilca** — investigador / autor principal del framework y de la tesis.

*(Añade aquí a otros integrantes oficiales del curso, si aplica.)*

## Último entregable de tesis consolidado

El compendio LaTeX más reciente bajo el árbol `tesis/todo/` es:

- [`tesis/todo/TESIS_TODO_EN_UNO.tex`](tesis/todo/TESIS_TODO_EN_UNO.tex) — tesis en un solo archivo fuente (compilar con LaTeX según tu flujo; ver también `TESIS_COMPLETA.tex` en el mismo directorio si usas otra variante).

Capítulos y borradores adicionales están en `tesis/capitulo1/`, `tesis/capitulo2/`, `tesis/capitulo3y4/`, etc.

## Dataset confirmado (evaluación)

- **HumanEval** y **MBPP** (Hugging Face), descritos y versionados vía manifiesto en `data/raw/`.
- Documentación de variables, fuentes y tamaños: [`data/raw/README.md`](data/raw/README.md).
- Ingesta reproducible: `python src/ingest_datasets_v0.py` (tras `pip install -r requirements.txt`).

## Estructura del repositorio

| Ruta | Contenido |
|------|------------|
| `agentes/` | Framework multi-agente v3, Docker, gRPC, tests. |
| `data/raw/` | JSONL de benchmarks y `manifest_v0.json` (regenerable). |
| `notebooks/` | EDA y experimentos. |
| `src/` | Scripts de ingesta y utilidades; p. ej. `ingest_datasets_v0.py`. |
| `tesis/` | Fuentes LaTeX/Markdown de la tesis. |
| `docs/PLAN_EJECUCION_RECUPERACION.md` | Correcciones y cronograma breve (Track B). |

## Inicio rápido (datos)

```bash
pip install -r requirements.txt
python src/ingest_datasets_v0.py
```

El script registra la **fecha/hora (UTC)**, el **tamaño** de cada archivo y el **hash SHA-256** en `data/raw/manifest_v0.json`.

## Framework (desarrollo)

```bash
cd agentes
# Ver agentes/README.md o README_FINAL.md para dependencias y arranque.
```

---

*Proyecto: Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo. Universidad (maestría).*
