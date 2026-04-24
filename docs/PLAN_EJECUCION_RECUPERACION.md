# Plan de ejecución y recuperación (Track B)

Documento de respuesta al requisito: correcciones frente a retroalimentación y cronograma breve.

## 1. Ajustes tras la semana 1 (o retroalimentación docente)

| Área | Qué se corrigió o fortaleció |
|------|------------------------------|
| **Repositorio** | Estructura mínima `data/raw`, `notebooks/`, `src/` y README de proyecto en la raíz, enlazando el código del framework en `agentes/`. |
| **Datos** | Dataset de evaluación acordado: **HumanEval** y **MBPP** desde Hugging Face, con documentación de variables y de tamaño/hash en `data/raw/README.md` y `manifest_v0.json`. |
| **Reproducibilidad** | Script de ingesta v0 con registro de fecha de ejecución, tamaño de archivo y SHA-256. |
| **Claridad académica** | Referencia explícita al entregable de tesis consolidado más reciente en el README (`tesis/todo/TESIS_TODO_EN_UNO.tex`). |

*Si en tu sección aún no hubo comentarios formales, este bloque actúa como registro de decisiones técnicas alineadas a la rúbrica del curso.*

## 2. Cronograma breve (próximas semanas)

| Semana | Meta concreta |
|--------|-----------------|
| **Semana 2 (actual)** | Repo público, datos documentados, ingesta v0; exploración en `notebooks/` (estadísticos básicos de longitud de prompts, conteo de tareas). |
| **Semana 3** | **Preprocesado listo:** normalización de esquemas (si se unifican salidas), particiones fijas y seeds para evaluación; borrador de pipeline que consuma `data/raw` desde el framework en `agentes/`. |
| **Semana 4+** | Integración con un primer experimento (subconjunto) y trazas de orquestación; avance de capítulos de metodología en paralelo. |

Fecha de actualización: 24 de abril de 2026.
