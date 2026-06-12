# CrewAI — Var1 (solo CrewAI + RAG)

CrewAI es el **único** framework multi-agente activo en Var1 del protocolo PASO 3. MetaGPT queda reservado para un experimento futuro separado.

## Var1 en el pipeline

| Paso | Carpeta | CrewAI |
|------|---------|--------|
| **0** | `0_etl_ingesta_preprocesamiento/` | No |
| **1** | `1_ingenieria_atributos_y_recuperacion_rag/` | Módulo `crewai_var1_entregable.py` |
| **3** | `3_protocolo_experimental_variantes/` | **Var1** — Analyst + Reviewer + DeepSeek + RAG |

**Var1** = CrewAI multi-agente + DeepSeek + contexto RAG (vecinos de `7_tabla_recuperacion_hibrida_rrf_top5.csv`).

**Prioridad de fuentes Var1 (arquitectura v2):**

1. `crewai_cache` — piloto D5 (seed=42, n=40 estratificado)
2. `crewai_api` — incremental si falta cache en piloto
3. `abstencion_fuera_piloto_d5` — **360/400** tickets fuera del piloto (pausa, Chow 1970)

Sin `pgvector_majority_fallback` en v2.

**Var2** = Var1 + middleware Gate B (determinista, sin API adicional).

## Roles Var1

1. **BugTriageAnalyst** — propone play/pausa/stop con contexto del ticket + vecinos
2. **BugCriticalityReviewer** — revisa y confirma o corrige la propuesta

Modelo: `deepseek-chat` vía `crewai.LLM` + API compatible OpenAI.

## Smoke test

```bash
cd tesis2/parcial3/entregable/1_ingenieria_atributos_y_recuperacion_rag
../../../.venv/bin/python crewai_configuracion_basica.py --dry-run
../../../.venv/bin/python crewai_configuracion_basica.py --smoke
```

## Entradas PASO 3

- `7_tabla_recuperacion_hibrida_rrf_top5.csv` — vecinos RAG
- `8_conjunto_evaluacion_experimento_n400.csv` — tickets eval
- `2_cache_predicciones_var1_crewai_rag.jsonl` — cache local CrewAI

## Nota metodológica

Var1 **no** es "CrewAI puro n=400": solo **10 %** (40 tickets) usa CrewAI; el **90 %** usa abstención pausa (`abstencion_fuera_piloto_d5`). Documentar siempre en informes y presentación.
