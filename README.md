# Framework multi-agente con gestión dinámica de criticidad y HITL adaptativo

## Título y descripción breve

- **Proyecto:** framework multi-agente con gestión dinámica de criticidad y supervisión humana adaptativa (HITL), orientado a desarrollo de software asistido por modelos de lenguaje, con orquestación, evaluación de riesgo y trazabilidad.

## Autor

- **José Luis Peñaloza Yaurivilca** — [GitHub: jpenalozay](https://github.com/jpenalozay)

- **Repositorio:** [https://github.com/jpenalozay/tesis2](https://github.com/jpenalozay/tesis2)

## Dataset

| Aspecto | Detalle |
|--------|---------|
| **Fuente** | [HumanEval](https://huggingface.co/datasets/openai_humaneval) y [MBPP](https://huggingface.co/datasets/mbpp) en Hugging Face. |
| **Descripción** | HumanEval: 164 tareas de programación en Python (prompt, solución de referencia, tests, `entry_point`). MBPP: split de evaluación con problemas de Python en lenguaje natural, código de referencia y listas de tests (p. ej. `task_id`, `text`, `code`, `test_list`). Conteos y rutas concretas tras la ingesta: ver `data/raw/README.md`. |
| **Versión / integridad** | Tras cada ingesta se genera `data/raw/manifest_v0.json` con fecha y hora de ejecución (UTC), tamaño en bytes y hash **SHA-256** de cada artefacto JSONL. |

## Requisitos

```bash
pip install -r requirements.txt
```

Dependencias adicionales del código del framework (Redis, gRPC, etc.): `agentes/requirements.txt`.

## Estructura del repositorio

| Ruta | Rol |
|------|-----|
| `agentes/` | Framework multi-agente: coordinador, agentes especializados, gRPC, configuración, tests, Docker. |
| `data/raw/` | Datos de benchmarks (generados por ingesta) y manifiesto de integridad. |
| `docs/` | Documentación complementaria (p. ej. planificación de iteraciones). |
| `notebooks/` | Análisis exploratorio y experimentos. |
| `src/` | Scripts reutilizables; ingesta y preparación de datos. |

## Cómo correr el pipeline (datos)

1. Instalar dependencias (sección [Requisitos](#requisitos)).
2. Descargar y materializar los conjuntos en formato usable (JSONL) y actualizar el manifiesto:

```bash
python src/ingest_datasets_v0.py
```

3. Revisar salida en consola (logs con instante de ejecución) y archivos bajo `data/raw/` según `data/raw/README.md`.

## Resultados esperados (mínimos)

- Archivos JSONL bajo `data/raw/humaneval/` y `data/raw/mbpp/` (nombres descritos en `data/raw/README.md`).
- `data/raw/manifest_v0.json` con conteos de filas, huellas SHA-256 y marcas de tiempo.
- Tras un clone limpio, el mismo flujo vuelve a generar salidas verificables contra el manifiesto.

## Desarrollo del framework

```bash
cd agentes
```

Instrucciones detalladas de arranque, configuración y pruebas: `agentes/README.md` y `agentes/README_FINAL.md`.

---

*Proyecto de investigación (maestría en inteligencia artificial).*
