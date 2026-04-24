# Datos en bruto (`data/raw`)

## Fuente y propósito

Los benchmarks se alinean con el marco de evaluación descrito en la tesis (Pass@1, comparación con literatura) y con `agentes/docs/PAPER_FRAMEWORK_COMPLETO.md`.

| Conjunto | Origen (Hugging Face) | Uso en el proyecto |
|----------|------------------------|--------------------|
| **HumanEval** | [openai_humaneval](https://huggingface.co/datasets/openai_humaneval) | 164 tareas de programación en Python; benchmark estándar de referencia. |
| **MBPP** | [mbpp](https://huggingface.co/datasets/mbpp) | Problemas básicos en Python; en la versión actual del dataset, el split `test` contiene 500 filas. |

**Enlaces controlados:** no es necesario subir el JSONL a Git si se regenera con el script; basta con ejecutar `python src/ingest_datasets_v0.py` tras `pip install -r requirements.txt`.

## Variables (campos principales)

### HumanEval (por fila, JSONL)

- `task_id`, `prompt`, `canonical_solution`, `test`, `entry_point`  
- El campo `test` contiene el código de tests como texto.

### MBPP (por fila, JSONL)

- `task_id`, `text` (enunciado), `code` (referencia), `test_list` (aserciones), `test_setup_code`, `challenge_test_list` (tareas extra si existen).

## Tamaño de archivos e integridad

Tras la ingesta, los tamaños y el hash **SHA-256** de cada artefacto quedan registrados en `manifest_v0.json` (generado en esta misma carpeta). Vuelve a comparar con ese manifiesto si sospechas corrupción o versiones mezcladas.

## Regenerar datos

```bash
pip install -r requirements.txt
python src/ingest_datasets_v0.py
```

Revisa la consola: incluye la fecha/hora (UTC) de ejecución y el manifiesto.
