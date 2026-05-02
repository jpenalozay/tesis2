# Corpus `criticidad_cases` — casos gold para política de criticidad

Conjunto formal para evaluar la **clasificación de criticidad** (modos `play` / `pausa` / `stop`) frente a etiquetas humanas de referencia.

## Contenido

| Archivo | Descripción |
|---------|-------------|
| `casos_gold_criticidad_v1.jsonl` | Piloto **n=36** (12 por clase); IDs prefijo `CRT-`. |
| `casos_gold_criticidad_v2.jsonl` | **n=300** (**100 por clase**); versión extendida del conjunto de trabajo; IDs prefijo `CRT-`. La procedencia operativa de los textos no se detalla en este repositorio. |
| `PROTOCOLO_ETIQUETADO.md` | Criterios de etiquetado y referencias metodológicas. |
| `EDA_criticidad_casos.ipynb` | EDA: **estadísticas descriptivas**, **distribuciones** (gold, longitudes, plantillas, densidad léxica), **riesgos** (desbalance con χ² de referencia, leakage léxico por keywords, drift en corpus estático). Cada figura incluye título y texto interpretativo. |

## Tamaño muestral (literatura)

- **v2:** **n=300** equilibrado; adecuado para concordancia.
- **v1:** n=36 para análisis exploratorios o comparación de versiones.

## Uso previsto

1. **EDA** sobre el JSONL en este directorio.  
2. **Experimentos:** por cada requerimiento, ejecutar el pipeline (p. ej. arquitecto → Sentinel) y comparar la decisión con `gold_mode` (vía `agentes/` o script dedicado).

## Ubicación

`Tesis/tesis2/data/criticidad_cases/`
