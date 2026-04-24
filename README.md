# Tesis: Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo

**Repositorio académico** del proyecto de maestría. El **código ejecutable del framework** (orquestación, agentes, API, Docker) vive en la carpeta [`agentes/`](agentes/); aquí se organizan datos, notebooks y scripts de ingesta alineados al entregable **Track B** (estructura base, dataset, ingesta v0, plan de recuperación).

- **Repositorio remoto:** [https://github.com/jpenalozay/tesis2](https://github.com/jpenalozay/tesis2)

## Integrantes

- **José Luis Peñaloza Yaurivilca** — [GitHub: @jpenalozay](https://github.com/jpenalozay) — investigador / autor principal del framework y de la tesis.

*(Añade correo u otros integrantes oficiales del curso, si aplica.)*

## Dataset confirmado (evaluación)

- **HumanEval** y **MBPP** (Hugging Face), descritos y versionados vía manifiesto en `data/raw/`.
- Documentación de variables, fuentes y tamaños: [`data/raw/README.md`](data/raw/README.md).
- Ingesta reproducible: `python src/ingest_datasets_v0.py` (tras `pip install -r requirements.txt`).

## Estructura del repositorio

| Ruta | Contenido |
|------|------------|
| `agentes/` | Framework multi-agente v3, Docker, gRPC, tests. |
| `data/raw/` | Manifiesto `manifest_v0.json` y documentación; JSONL regenerables con el script de ingesta. |
| `notebooks/` | EDA y experimentos. |
| `src/` | Scripts de ingesta y utilidades; p. ej. `ingest_datasets_v0.py`. |
| `docs/PLAN_EJECUCION_RECUPERACION.md` | Plan de recuperación: correcciones (semana 1) y cronograma (Track B). |

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
