# Entregable — Examen Parcial 3

Pipeline numerado del proyecto. Cada carpeta `N_*` corresponde a una etapa del flujo;
dentro de ella, notebooks y artefactos llevan prefijo numérico según **orden de ejecución y de salida**.

## Documentación de diseño y síntesis

| Documento | Contenido |
|-----------|-----------|
| `ANALISIS_VARIABLES_METRICAS.md` | Métricas por capa (criticidad vs framework); set mínimo 6 |
| `ANALISIS_CRITICIDAD_PASADA1_ARQUITECTURA.md` | Arquitectura Criticality Engine, dual gate, plugins |
| `ANALISIS_CRITICIDAD_PASADA2_PLUGIN_RAG_MEDICION.md` | RagPlugin, Var1/Var2, métricas C-01..C-10 |
| `ANALISIS_ENTREGABLE_SINTESIS_PASADA1.md` | Síntesis auditoría pasada 1 (pipeline 0→3) |
| `ANALISIS_ENTREGABLE_SINTESIS_PASADA2.md` | Síntesis auditoría pasada 2 + veredicto final |
| `INVESTIGACION_CREWAI_API_REAL_PASADA1.md` | Investigación CrewAI Var1 (diseño) |
| `INVESTIGACION_CREWAI_API_REAL_PASADA2.md` | Crítica CrewAI Var1 (riesgos) |
| `ANALISIS_CREWAI_PASADA1.md` | Implementación CrewAI piloto n=40 + arquitectura |
| `ANALISIS_CREWAI_PASADA2.md` | Auditoría CrewAI + veredicto final |
| `ANALISIS_PROTOCOLO_PASADA1.md` | Diseño PASO 3 protocolo (implementado) |
| `ANALISIS_PROTOCOLO_PASADA2.md` | Crítica PASO 3 + métricas finales |
| `ANALISIS_PASO4_PASADA1.md` | Diseño PASO 4 calibración/ablación/explicabilidad (IA06) |
| `ANALISIS_PASO4_PASADA2.md` | Auditoría PASO 4 + veredicto final |
| `ANALISIS_ARQUITECTURA_V2_PASADA1.md` | Diseño arquitectura v2 + catálogo métricas estándar |
| `ANALISIS_ARQUITECTURA_V2_PASADA2.md` | Auditoría arquitectura v2 + veredicto final |
| `VERIFICACION_ENTREGABLE_PASADA1.md` | Inventario + integridad pasada 1 |
| `VERIFICACION_ENTREGABLE_PASADA2.md` | Alineación documental + veredicto final |
| `VERIFICACION_ENTREGABLE_PASADA3.md` | Cierre IA08 + auditoría global 0→5 |
| `ANALISIS_ENTREGABLE_SINTESIS_FINAL.md` | Síntesis pipeline completo 0→5 + veredicto examen |
| `ANALISIS_PASO2_PASADA1_DISENO.md` | Diseño histórico protocolo experimental |
| `ANALISIS_PASO2_PASADA2_CRITICA.md` | Crítica histórica protocolo |
| `ESTUDIO_SOTA_COMPONENTE_CRITICIDAD.md` | SOTA 2024–2026; DAA/HITL; LangGraph |

## Estructura actual

```
entregable/
├── README.md
├── 0_etl_ingesta_preprocesamiento/     ← PASO 0 · IA02 ETL
│   ├── 0_etl_datos_limpieza_y_muestreo.ipynb
│   ├── 0_datos_crudos_bugzilla_eclipse.csv
│   ├── 1_embudo_limpieza_por_fases.csv
│   ├── 2_corpus_limpio_bugsrepo.csv
│   ├── 3_informe_muestreo_y_distribucion.json
│   ├── 4_muestra_laboratorio_n400.csv
│   ├── 5_conjunto_entrenamiento_holdout_70.csv
│   ├── 6_conjunto_prueba_holdout_30.csv
│   ├── 7_informe_division_train_test.json
│   └── 8_conjunto_evaluacion_experimento_n400.csv
└── 1_ingenieria_atributos_y_recuperacion_rag/  ← PASO 1 · IA04/IA08 + RAG pgvector
    ├── 1_ingenieria_atributos_y_rag.ipynb
    ├── build_notebook_paso1.py
    ├── rag_pgvector_entregable.py         ← módulo pgvector Docker (esquema entregable_rag)
    ├── 0_instrucciones_crewai.md          ← preparación Var1 (PASO 2)
    ├── crewai_configuracion_basica.py     ← smoke test 1 ticket / dry-run
    ├── crewai_var1_entregable.py          ← módulo CrewAI Var1 (Analyst+Reviewer)
    ├── 0_informe_configuracion_ingenieria.json
    ├── 1_matriz_embeddings_historial_rag.npz
    ├── 2_matriz_embeddings_conjunto_evaluacion.npy
    ├── 3_tabla_vecinos_recuperados_top5.csv
    ├── 4_informe_auditoria_anti_fuga.json
    ├── 5_tabla_features_middleware_preview.csv
    ├── 6_informe_conexion_pgvector_docker.json
    ├── 7_tabla_recuperacion_hibrida_rrf_top5.csv
    └── 8_comparacion_sklearn_vs_pgvector_muestra.csv
└── 2_modulo_criticidad_gobernanza_adaptativa/  ← PASO 2 · criticidad play/pausa/stop
    ├── 2_modulo_criticidad_gobernanza_adaptativa.ipynb
    ├── build_notebook_paso2.py
    ├── run_auditoria_pipeline.py
    ├── 0_configuracion_modulo_criticidad.yaml
    ├── plugins/                              ← contratos reutilizables
    │   ├── 0_interfaz_proveedor_senales.py
    │   ├── 1_plugin_rag_recuperacion.py
    │   ├── 2_plugin_costo_tokens_bucles.py
    │   ├── 3_motor_politica_play_pausa_stop.py
    │   └── 4_puerta_hitl_sincrono_asincrono.py
    ├── 0_informe_arquitectura_modulo_criticidad.json
    ├── 1_tabla_mapeo_ejes_evaluacion_criticidad.csv
    ├── 2_tabla_senales_por_ticket_n400.csv
    ├── 3_tabla_decisiones_politica_play_pausa_stop_n400.csv   ← Gate A
    ├── 4_tabla_decisiones_gate_b_post_agente_simulado_n400.csv ← Gate B
    ├── 5_tabla_modos_hitl_asignados_por_clase.csv
    ├── 6_tabla_metricas_modulo_criticidad_capa_a.csv
    ├── 7_informe_auditoria_pasada1_modulo_criticidad.json
    ├── 8_informe_auditoria_pasada1_pipeline_completo.json
    ├── 9_informe_auditoria_pasada2_resultado_final.json
    ├── AUDITORIA_PASADA1_GAPS.md
    └── AUDITORIA_PASADA2_RESULTADO.md
└── 3_protocolo_experimental_variantes/  ← PASO 3 · Baseline / Var1 / Var2
    ├── 3_protocolo_experimental_baseline_var1_var2.ipynb
    ├── build_notebook_paso3.py
    ├── run_auditoria_protocolo.py
    ├── run_protocolo_experiment.py          ← corrida API real + artefactos 0–16
    ├── 0_configuracion_protocolo_experimental.yaml
    ├── metricas_protocolo_entregable.py
    ├── protocolo_variantes_entregable.py
    ├── 0_informe_configuracion_protocolo_experimental.json
    ├── 1_cache_predicciones_deepseek_baseline.jsonl
    ├── 2_cache_predicciones_var1_crewai_rag.jsonl
    ├── 3_tabla_predicciones_baseline_amnesico_n400.csv
    ├── 4_tabla_predicciones_var1_crewai_rag_n400.csv
    ├── 5_tabla_predicciones_var2_middleware_intercepta_n400.csv
    ├── 6_tabla_predicciones_consolidada_tres_variantes_n400.csv
    ├── 7_tabla_metricas_set_minimo_seis_por_variante.csv
    ├── 8_tabla_metricas_extendidas_framework_por_variante.csv
    ├── 9_tabla_validacion_holdout_30_por_variante.csv
    ├── 10_tabla_validacion_cruzada_5fold_estratificada_n400.csv
    ├── 11_tabla_comparacion_pareada_mcnemar.csv
    ├── 12_informe_ejecucion_fuentes_cache_api.json
    ├── 13_figura_ablacion_f1_macro_ec_fnr_stop.png
    ├── 14_figura_matrices_confusion_tres_variantes.png
    ├── 15_figura_curva_calibracion_ece_var2.png
    ├── 16_informe_resumen_protocolo_experimental.json
    ├── 7_informe_auditoria_pasada1_protocolo.json
    ├── 8_informe_auditoria_pasada1_pipeline_0_3.json
    ├── 9_informe_auditoria_pasada2_resultado_final.json
    ├── AUDITORIA_PASADA1_GAPS.md
    └── AUDITORIA_PASADA2_RESULTADO.md
└── 4_calibracion_diagnosticos_y_explicabilidad/  ← PASO 4 · IA06 calibración/diagnósticos
    ├── 4_calibracion_diagnosticos_y_explicabilidad.ipynb
    ├── build_notebook_paso4.py
    ├── run_calibracion_diagnosticos.py
    ├── run_auditoria_paso4.py
    ├── calibracion_diagnosticos_entregable.py
    ├── 0_configuracion_calibracion_diagnosticos.yaml
    ├── 0_informe_configuracion_paso4.json
    ├── 1_tabla_calibracion_ece_brier_antes_despues.csv
    ├── 2_figura_curvas_calibracion_tres_variantes.png
    ├── 3_tabla_ablacion_componentes_middleware.csv
    ├── 4_figura_ablacion_delta_f1_stop_ec.png
    ├── 5_tabla_importancia_senales_overrides.csv
    ├── 6_figura_importancia_senales_gate_b.png
    ├── 7_tabla_metricas_piloto_crewai_n40.csv
    ├── 8_informe_resumen_paso4.json
    ├── 9_informe_auditoria_pasada1_paso4.json
    ├── 10_informe_auditoria_pasada2_resultado_final.json
    ├── ANALISIS_PASO4_PASADA1.md
    ├── ANALISIS_PASO4_PASADA2.md
    ├── AUDITORIA_PASADA1_GAPS.md
    └── AUDITORIA_PASADA2_RESULTADO.md
└── 5_cierre_examen_parcial_mlops/  ← PASO 5 · IA08 MLOps ligero + cierre examen
    ├── 5_cierre_examen_parcial_mlops.ipynb
    ├── build_notebook_paso5.py
    ├── run_cierre_examen.py
    ├── run_auditoria_paso5.py
    ├── cierre_examen_entregable.py
    ├── 0_configuracion_cierre_examen.yaml
    ├── 0_informe_configuracion_paso5.json
    ├── 1_tablero_experimentos_consolidado.csv
    ├── 2_checklist_examen_final_ia08.csv
    ├── 3_informe_gap_overfitting_calibracion.json
    ├── 4_guia_demo_presentacion_10min.md
    ├── presentacion_examen_parcial.md          ← slides Marp demo IA08
    ├── Presentacion_Examen_Parcial.pdf
    ├── build_presentacion_examen.py
    ├── speech_presentacion_examen_parcial.md   ← guion oral 10–12 min
    ├── presentacion_modulo_criticidad.md       ← slides PASO 2 criticidad
    ├── Presentacion_Modulo_Criticidad.pdf
    ├── build_presentacion_criticidad.py
    ├── parcial_informe.md
    ├── Parcial_Informe.pdf
    ├── build_parcial_informe_pdf.py
    ├── 5_informe_auditoria_global_entregable_0_4.json
    ├── 6_veredicto_final_entregable.md
    ├── ANALISIS_PASO5_PASADA1.md
    ├── ANALISIS_PASO5_PASADA2.md
    └── AUDITORIA_PASADA1_GAPS.md / AUDITORIA_PASADA2_RESULTADO.md
../run_auditoria_entregable_completo.py   ← auditoría global desde raíz entregable
```

## Conteos verificados (PASO 0)

| Métrica | Valor |
|---------|-------|
| Registros crudos (`n_raw`) | 88 682 |
| Corpus limpio (`n_clean`) | 88 008 |
| Muestra lab (n=400, ≈ Cochran 384) | 400 |
| Train hold-out 70 % | 280 |
| Test hold-out 30 % | 120 |
| Evaluación experimento LLM | 400 (muestra lab completa) |

Distribución muestra lab: pausa 346 · play 24 · stop 30.

**Nota metodológica:** n=400 se adopta como entero redondo cercano a Cochran (n₀≈384, Z=1.96, p=0.5, E=0.05).

**Justificación del mapeo Bugzilla → play/pausa/stop:** documentada en el notebook PASO 0 (sección *Justificación metodológica del mapeo severidad → criticidad*, FASE 4); declara el uso de *severity* como proxy label y sus limitaciones frente a la criticidad operacional FMEA.

## Orden del pipeline

| Paso | Carpeta / notebook | Produce |
|------|-------------------|---------|
| **0** | `0_etl_ingesta_preprocesamiento/0_etl_datos_limpieza_y_muestreo.ipynb` | Extract → Transform → Load (corpus, muestra lab n=400, splits 70/30, evaluación n=400) |
| **1** | `1_ingenieria_atributos_y_recuperacion_rag/1_ingenieria_atributos_y_rag.ipynb` | TF-IDF+SVD train-only, pgvector Docker (hybrid RRF), vecinos top-5, preview middleware |
| **2** | `2_modulo_criticidad_gobernanza_adaptativa/2_modulo_criticidad_gobernanza_adaptativa.ipynb` | Señales 4D, RagPlugin, PolicyEngine dual gate, HITL, métricas C-01..C-06 |
| **3** | `3_protocolo_experimental_variantes/3_protocolo_experimental_baseline_var1_var2.ipynb` | Baseline + Var1 CrewAI + Var2 Gate B; métricas framework Capa B |
| **4** | `4_calibracion_diagnosticos_y_explicabilidad/4_calibracion_diagnosticos_y_explicabilidad.ipynb` | Calibración post-hoc, ablación middleware, explicabilidad, piloto n=40 |
| **5** | `5_cierre_examen_parcial_mlops/5_cierre_examen_parcial_mlops.ipynb` | Tablero experimentos, checklist IA08, gap/overfitting, guía demo, auditoría global |

**División de roles:** train 280 + test 120 = muestra lab 400 (≈ Cochran). El experimento LLM evalúa sobre los **400** registros (`8_conjunto_evaluacion_experimento_n400.csv`); train se reserva para fit TF-IDF/SVD (280 filas).

## Cadena de dependencias (PASO 0 → PASO 1)

Rutas relativas desde `1_ingenieria_atributos_y_recuperacion_rag/`: `../0_etl_ingesta_preprocesamiento/<archivo>`.

| Artefacto PASO 0 | Consumido en PASO 1 por | Uso |
|------------------|-------------------------|-----|
| `2_corpus_limpio_bugsrepo.csv` | Notebook celda carga; `rag_pgvector_entregable.py` (indirecto) | Pool historial RAG = corpus − hashes eval |
| `5_conjunto_entrenamiento_holdout_70.csv` | Notebook fit TF-IDF/SVD | **Único** conjunto de ajuste (280 filas, `seed=42`) |
| `6_conjunto_prueba_holdout_30.csv` | Notebook (referencia opcional) | Hold-out 30 %; no entra al fit ni al historial |
| `8_conjunto_evaluacion_experimento_n400.csv` | Notebook transform + recuperación; `crewai_configuracion_basica.py` | Queries evaluación (400); exclusión anti-fuga del pool |
| `4_muestra_laboratorio_n400.csv` | — (derivación documentada) | Fuente de `5_`, `6_` y `8_`; PASO 1 lee `8_` directamente |
| `3_informe_muestreo_y_distribucion.json` | — (trazabilidad) | Conteos y `severity_map` de referencia |
| `7_informe_division_train_test.json` | — (trazabilidad) | Ratios 70/30 y distribución por clase |

**Columnas compartidas:** `text`, `text_hash` (SHA-256 texto normalizado), `thesis_class`, `severity` (donde aplique). El `text_hash` es la clave anti-fuga entre pasos.

## Tabla de alineación PASO 0 ↔ PASO 1

| Ítem | PASO 0 | PASO 1 | Estado |
|------|--------|--------|--------|
| Semilla | `seed=42` en JSON y notebook | `SEED=42` en notebook y JSON | Alineado |
| Muestra lab | `n_lab=400` (`4_muestra_…n400.csv`) | `n_eval=400` en auditoría | Alineado |
| Train / test | 280 / 120 (`5_` / `6_`) | `vectorizer_fit_rows=280` | Alineado |
| Corpus limpio | `n_clean=88008` | `n_corpus=88008` en auditoría | Alineado |
| Eval experimento | `8_conjunto_evaluacion_experimento_n400.csv` | `PATH_EVAL` → mismo archivo | Alineado |
| Anti-fuga RAG | `text_hash` en todos los CSV | `history_eval_hash_overlap=0` | Alineado |
| Fit train-only | Hold-out documentado | `eval_rows_in_fit=0`, `history_rows_in_fit=0` | Alineado |
| pgvector | — | Esquema `entregable_rag` (`chunks`, `run_meta`) | Alineado |
| Artefactos numerados | `0_`…`8_` en español | `0_`…`8_` en español | Alineado |
| nombres activos | Sin `n40`/`n384` en filenames | Sin `n40`/`n384` en filenames | Alineado |

**Nota anti-fuga:** `train ⊂ eval` (280 hashes compartidos) es **intencional** — eval = muestra lab completa. La barrera de fuga aplica al **historial RAG** (`corpus − eval_hashes`), verificado con `history_eval_hash_overlap = 0`.

## Conteos verificados (PASO 1)

| Métrica | Valor |
|---------|-------|
| Embeddings historial RAG | 6 000 × 64 (`1_matriz_embeddings_historial_rag.npz`) |
| Embeddings evaluación | 400 × 64 (`2_matriz_embeddings_conjunto_evaluacion.npy`) |
| Filas recuperación top-5 | 2 000 (400 queries × k=5) en `3_` y `7_` |
| Preview middleware | 400 filas (`5_tabla_features_middleware_preview.csv`) |
| Benchmark sklearn vs pgvector | 20 filas (`8_comparacion_…`) |
| Chunks pgvector insertados | 6 000 en `entregable_rag.chunks` |

## Tabla de artefactos (PASO 0)

| # | Archivo | Rol |
|---|---------|-----|
| 0 | `0_datos_crudos_bugzilla_eclipse.csv` | Extract — ingesta dataset crudo |
| 1 | `1_embudo_limpieza_por_fases.csv` | Transform — embudo limpieza 5 fases |
| 2 | `2_corpus_limpio_bugsrepo.csv` | Load — corpus limpio (~88 008) |
| 3 | `3_informe_muestreo_y_distribucion.json` | Load — estadísticas globales |
| 4 | `4_muestra_laboratorio_n400.csv` | Load — muestra lab n=400 |
| 5 | `5_conjunto_entrenamiento_holdout_70.csv` | Load — 70 % train (RAG/history) |
| 6 | `6_conjunto_prueba_holdout_30.csv` | Load — 30 % test (hold-out referencia) |
| 7 | `7_informe_division_train_test.json` | Load — ratios y conteos split |
| 8 | `8_conjunto_evaluacion_experimento_n400.csv` | Load — evaluación LLM n=400 (baseline/var1/var2) |

## Tabla de artefactos (PASO 1)

| # | Archivo | Rol |
|---|---------|-----|
| 0 | `0_informe_configuracion_ingenieria.json` | Hiperparámetros, backend RAG, refs. reutilización |
| 1 | `1_matriz_embeddings_historial_rag.npz` | Embeddings SVD historial (corpus − eval) |
| 2 | `2_matriz_embeddings_conjunto_evaluacion.npy` | Embeddings SVD evaluación n=400 |
| 3 | `3_tabla_vecinos_recuperados_top5.csv` | Vecinos recuperados k=5 (hybrid RRF principal) |
| 4 | `4_informe_auditoria_anti_fuga.json` | Checks overlap hash, fit train-only |
| 5 | `5_tabla_features_middleware_preview.csv` | Preview señales Var2 (sin middleware) |
| 6 | `6_informe_conexion_pgvector_docker.json` | Diagnóstico conexión Docker pgvector |
| 7 | `7_tabla_recuperacion_hibrida_rrf_top5.csv` | Auditoría detallada hybrid RRF + rerank |
| 8 | `8_comparacion_sklearn_vs_pgvector_muestra.csv` | Benchmark overlap top-5 (muestra n=20) |

**pgvector Docker:** contenedor `irene-postgres` (`pgvector/pgvector:pg15`) en `127.0.0.1:5432`, BD `irene`. Tablas dedicadas en esquema `entregable_rag` (`chunks`, `run_meta`) — no reutiliza tablas sprint6.

Variables de entorno opcionales: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` (defaults: `127.0.0.1`, `5432`, `irene`, `postgres`, `root`).

**CrewAI (Var1):** no se ejecuta en PASO 1 ni PASO 2 (batch). Preparación en `0_instrucciones_crewai.md`. PASO 2 simula `agent_label` desde mayoría RAG; CrewAI real en **PASO 3**.

## Conteos verificados (PASO 2)

| Métrica | Valor |
|---------|-------|
| Señales por ticket | 400 (`2_tabla_senales_por_ticket_n400.csv`) |
| Decisiones Gate A | 400 (`3_tabla_decisiones_politica_...`) |
| Decisiones Gate B | 400 (`4_tabla_decisiones_gate_b_...`) |
| Métricas Capa A | C-01..C-06 en `6_tabla_metricas_...` |
| Anti-fuga (ref PASO 1) | `history_eval_hash_overlap = 0` |
| Gold v2 subconjunto | n=50 proxy 4D (limitación ES/EN documentada) |

Distribución Gate A (última ejecución): play ~166 · pausa ~217 · stop ~17.

## Cadena de dependencias (PASO 0 → PASO 2)

| Artefacto upstream | Consumido en PASO 2 |
|--------------------|---------------------|
| `0_.../8_conjunto_evaluacion_experimento_n400.csv` | Tickets evaluación |
| `1_.../7_tabla_recuperacion_hibrida_rrf_top5.csv` | RagPlugin (obligatorio Var2) |
| `1_.../4_informe_auditoria_anti_fuga.json` | Trazabilidad anti-fuga |
| `docs/.../winning_config.json` | Parámetros PolicyEngine (HPO sprint7) |
| `tesis2/data/.../casos_gold_criticidad_v2.jsonl` | Validación subconjunto D3 |

## Cómo re-ejecutar el PASO 2

```bash
cd tesis2/parcial3/entregable/2_modulo_criticidad_gobernanza_adaptativa
../../../.venv/bin/python build_notebook_paso2.py   # regenerar notebook si cambia builder
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  2_modulo_criticidad_gobernanza_adaptativa.ipynb \
  --output 2_modulo_criticidad_gobernanza_adaptativa.ipynb
../../../.venv/bin/python run_auditoria_pipeline.py   # auditoría 0→2
```

## Cómo re-ejecutar pipeline completo 0 → 1 → 2 → 3

```bash
cd tesis2/parcial3/entregable/0_etl_ingesta_preprocesamiento
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  0_etl_datos_limpieza_y_muestreo.ipynb --output 0_etl_datos_limpieza_y_muestreo.ipynb

cd ../1_ingenieria_atributos_y_recuperacion_rag
../../../.venv/bin/python build_notebook_paso1.py
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  1_ingenieria_atributos_y_rag.ipynb --output 1_ingenieria_atributos_y_rag.ipynb

cd ../2_modulo_criticidad_gobernanza_adaptativa
../../../.venv/bin/python build_notebook_paso2.py
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  2_modulo_criticidad_gobernanza_adaptativa.ipynb \
  --output 2_modulo_criticidad_gobernanza_adaptativa.ipynb
../../../.venv/bin/python run_auditoria_pipeline.py

cd ../3_protocolo_experimental_variantes
../../../.venv/bin/python build_notebook_paso3.py
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  3_protocolo_experimental_baseline_var1_var2.ipynb \
  --output 3_protocolo_experimental_baseline_var1_var2.ipynb
../../../.venv/bin/python run_auditoria_protocolo.py
```

Requisitos PASO 2–3: `pandas`, `numpy`, `scikit-learn`, `pyyaml`, `matplotlib`; PASO 1 requiere Docker pgvector (`irene-postgres`) para backend principal.

## Cómo re-ejecutar el PASO 0

```bash
cd tesis2/parcial3/entregable/0_etl_ingesta_preprocesamiento
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  0_etl_datos_limpieza_y_muestreo.ipynb --output 0_etl_datos_limpieza_y_muestreo.ipynb
```

Requisitos: `pandas`, `numpy`, `scikit-learn`; opcional `datasets` si falta el CSV crudo.

## Cómo re-ejecutar el PASO 1

```bash
cd tesis2/parcial3/entregable/1_ingenieria_atributos_y_recuperacion_rag
../../../.venv/bin/python build_notebook_paso1.py   # regenerar notebook si cambia el builder
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  1_ingenieria_atributos_y_rag.ipynb --output 1_ingenieria_atributos_y_rag.ipynb
```

Smoke test CrewAI (dry-run, sin API):

```bash
../../../.venv/bin/python crewai_configuracion_basica.py --dry-run
```

Requisitos: `pandas`, `numpy`, `scikit-learn`, `scipy`; `psycopg2` + Docker pgvector (`irene-postgres`) para backend principal; fallback sklearn si Docker no está up; `crewai` para `--smoke`.

Test rápido de conexión pgvector:

```bash
cd tesis2/parcial3/entregable/1_ingenieria_atributos_y_recuperacion_rag
../../../.venv/bin/python -c "import rag_pgvector_entregable as r; print(r.check_pgvector_sql())"
```

## Terminología UNI

- **Extract (E):** ingesta desde fuente externa → `0_datos_crudos_…`
- **Transform (T):** preprocesamiento, limpieza (embudo 5 fases), muestreo estratificado y hold-out
- **Load (L):** persistencia en CSV/JSON listos para modelado (`2_…` a `8_…`)

Referencia: `clases/2Curso/Maestria2_IA02.pptx` (Ingesta y Preprocesamiento Reproducibles).

---

## PASO 2 — Módulo criticidad gobernanza adaptativa ✅

**Estado:** implementado y auditado (doble pasada). Decisiones D1–D5 confirmadas.

| Gate | Artefacto | Rol |
|------|-----------|-----|
| **Gate A** | `3_tabla_decisiones_politica_play_pausa_stop_n400.csv` | Pre-LLM: PolicyEngine + RagPlugin |
| **Gate B** | `4_tabla_decisiones_gate_b_post_agente_simulado_n400.csv` | Post-agente: override Var2 |

---

## PASO 3 — Protocolo experimental ✅

**Estado:** implementado y auditado (doble pasada). Modo **`api-incremental`**, `run_api=true`, **`run_crewai=true`** (piloto n=40).

| Documento | Contenido |
|-----------|-----------|
| [`ANALISIS_PROTOCOLO_PASADA1.md`](ANALISIS_PROTOCOLO_PASADA1.md) | Diseño implementado Baseline/Var1/Var2 |
| [`ANALISIS_PROTOCOLO_PASADA2.md`](ANALISIS_PROTOCOLO_PASADA2.md) | Crítica + métricas finales + veredicto |
| [`ANALISIS_VAR1_SOLO_CREWAI_PASADA1.md`](ANALISIS_VAR1_SOLO_CREWAI_PASADA1.md) | Diseño refactor Var1 sin MetaGPT |
| [`ANALISIS_VAR1_SOLO_CREWAI_PASADA2.md`](ANALISIS_VAR1_SOLO_CREWAI_PASADA2.md) | Post-ejecución + auditoría Var1 solo CrewAI |
| [`ANALISIS_VARIABLES_METRICAS.md`](ANALISIS_VARIABLES_METRICAS.md) | Set mínimo 6 + Capa A/B |
| [`ALINEACION_PRESENTACION_PDF_GAPS.md`](ALINEACION_PRESENTACION_PDF_GAPS.md) | Gaps PPT/PDF vs métricas reales n=400 |

### Métricas finales (eval n=400, arquitectura v2 — 2026-06-12)

| Variante | F1-macro | F1-stop | ECE | EC | FNR-stop | Override |
|----------|----------|---------|-----|-----|----------|----------|
| Baseline | 0.362 | 0.301 | 0.448 | 0.111 | 0.333 | — |
| Var1 | 0.335 | 0.057 | 0.440 | 0.147 | 0.967 | 0 % |
| Var2 | **0.435** | **0.391** | 0.419 | 0.123 | **0.433** | **16.5 %** |

**Extendido:** F1-play/pausa, tokens, latencia, HITL USD en `8_tabla_metricas_extendidas_framework_por_variante.csv`.

**Fuentes Baseline:** DeepSeek cache 154 + API 246 = **400/400 LLM real**.

**Fuentes Var1:** **40 CrewAI cache** (piloto D5) + **360 abstención pausa** — sin majority RAG.

**Salvedad metodológica D5:** Var1 = 10 % CrewAI real + 90 % abstención pausa (Chow 1970) — **diseño intencional**, no bug. No escalar CrewAI a n=400 antes de PASO 4: costo API y evidencia desfavorable en piloto; **Var2 es la contribución principal**. Sub-análisis n=40 en PASO 4 documenta capacidad del agente sin invalidar protocolo n=400.

**Var2:** **66 overrides** Gate B (16,5 %) — middleware demostrable.

### Cómo re-ejecutar el PASO 3

```bash
# Requiere tesis2/.env con DEEPSEEK_API_KEY o SYSTEM_LLM_API_KEY (no commitear)
cd tesis2/parcial3/entregable/3_protocolo_experimental_variantes
../../../.venv/bin/python build_notebook_paso3.py
../../../.venv/bin/python run_protocolo_experiment.py   # corrida API + artefactos 0–16
../../../.venv/bin/python run_auditoria_protocolo.py
# Alternativa notebook (usa cache local si ya existe):
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  3_protocolo_experimental_baseline_var1_var2.ipynb \
  --output 3_protocolo_experimental_baseline_var1_var2.ipynb
```

---

## PASO 4 — Calibración, diagnósticos y explicabilidad ✅

**Estado:** implementado y auditado (doble pasada). IA06 sobre cache PASO 3 (sin re-API).

**¿De qué se trata?** PASO 4 corresponde a **IA06 — Calibración y diagnóstico de modelos** (PPTs UNI). Tras el protocolo experimental (PASO 3), las predicciones ya están cacheadas; aquí se responde *¿confían bien los scores?*, *¿qué componente del middleware aporta valor?* y *¿por qué el agente overridea?* sin volver a llamar APIs. Cuatro bloques:

1. **Calibración post-hoc** — Platt e isotónica (fit en train 280); ECE y Brier antes/después sobre n=400.
2. **Ablación por componente** — Apagar Gate B, fuzzy, señal RAG o ejes 4D y medir ΔF1-stop, ΔEC, override_rate.
3. **Explicabilidad** — Permutation importance sobre los 66 overrides Gate B de Var2.
4. **Sub-análisis piloto n=40** — Métricas solo en tickets CrewAI reales (D5); no sustituye evaluación n=400 con abstención Chow 1970.

**Notebook:** `4_calibracion_diagnosticos_y_explicabilidad.ipynb` (prefijo `4_` = orden de salida en la carpeta). El pipeline es **script-first**: `run_calibracion_diagnosticos.py` genera CSVs/figuras; `build_notebook_paso4.py` crea un notebook delgado que invoca el script y visualiza resultados. Tras `build_notebook_paso4.py`, ejecutar con nbconvert para outputs embebidos.

| Documento | Contenido |
|-----------|-----------|
| [`ANALISIS_PASO4_PASADA1.md`](4_calibracion_diagnosticos_y_explicabilidad/ANALISIS_PASO4_PASADA1.md) | Diseño calibración/ablación/explicabilidad |
| [`ANALISIS_PASO4_PASADA2.md`](4_calibracion_diagnosticos_y_explicabilidad/ANALISIS_PASO4_PASADA2.md) | Crítica + veredicto final PASO 4 |

### Métricas PASO 4 (2026-06-12, arquitectura v2)

| Análisis | Resultado |
|----------|-----------|
| ECE isotónica (n=400) | Baseline 0,448→0,003 · Var1 0,440→0,035 · Var2 0,419→**0,026** |
| Ablación `sin_gate_b` | ΔF1-stop **−0,334** · override 0 % (reproduce colapso Var1) |
| Ablación `sin_senal_rag` | override 13 % (−3,5 pp) |
| Importancia overrides | `rag_uncertainty` > `class_consensus` > `I_mem` |
| Piloto CrewAI n=40 | F1-stop 0,25 · FNR-stop 0,67 (sub-análisis, no n=400) |

### Cómo re-ejecutar el PASO 4

```bash
cd tesis2/parcial3/entregable/4_calibracion_diagnosticos_y_explicabilidad
../../../.venv/bin/python run_calibracion_diagnosticos.py   # artefactos 0–8 (sin re-API)
../../../.venv/bin/python build_notebook_paso4.py             # regenerar notebook
../../../.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  4_calibracion_diagnosticos_y_explicabilidad.ipynb \
  --output 4_calibracion_diagnosticos_y_explicabilidad.ipynb
../../../.venv/bin/python run_auditoria_paso4.py
```

Requisito: artefactos PASO 3 (`3_`–`7_tabla_metricas_*`) generados previamente.

---

## PASO 5 — Cierre examen parcial MLOps (IA08) ✅

**Estado:** implementado y auditado (doble pasada). Consolidación pipeline 0→4 + sprint7 HPO.

| Documento | Contenido |
|-----------|-----------|
| [`ANALISIS_PASO5_PASADA1.md`](5_cierre_examen_parcial_mlops/ANALISIS_PASO5_PASADA1.md) | Diseño tablero/checklist/gap/demo |
| [`ANALISIS_PASO5_PASADA2.md`](5_cierre_examen_parcial_mlops/ANALISIS_PASO5_PASADA2.md) | Auditoría + veredicto final PASO 5 |
| [`6_veredicto_final_entregable.md`](5_cierre_examen_parcial_mlops/6_veredicto_final_entregable.md) | Veredicto global examen parcial |
| [`Parcial_Informe.pdf`](5_cierre_examen_parcial_mlops/Parcial_Informe.pdf) | Informe examen parcial IA08 (9 secciones) |
| [`Presentacion_Examen_Parcial.pdf`](5_cierre_examen_parcial_mlops/Presentacion_Examen_Parcial.pdf) | Slides demo 10–12 min (IA08) |
| [`Presentacion_Modulo_Criticidad.pdf`](5_cierre_examen_parcial_mlops/Presentacion_Modulo_Criticidad.pdf) | Slides módulo criticidad PASO 2 |
| [`speech_presentacion_examen_parcial.md`](5_cierre_examen_parcial_mlops/speech_presentacion_examen_parcial.md) | Guion oral + notas extendidas |
| [`parcial_informe.md`](5_cierre_examen_parcial_mlops/parcial_informe.md) | Fuente Markdown del informe |
| [`VERIFICACION_ENTREGABLE_PASADA3.md`](VERIFICACION_ENTREGABLE_PASADA3.md) | Checklist IA08 + auditoría 0→5 |
| [`ANALISIS_ENTREGABLE_SINTESIS_FINAL.md`](ANALISIS_ENTREGABLE_SINTESIS_FINAL.md) | Síntesis pipeline completo |

### Resultados PASO 5 (2026-06-12)

| Ítem | Resultado |
|------|-----------|
| Tablero experimentos | **13** corridas (PASO 0→4 + holdout + sprint7 + calibración) |
| Checklist IA08 + informe 9 secciones | **100%** cumplido (27/27) |
| Auditoría global 0→4 | **OK** (0 gaps críticos) |
| Gap F1-stop Var2 eval vs holdout | +0,109 (generalización favorable) |
| Veredicto global | **✅ APROBADO** |

### Cómo re-ejecutar el PASO 5

```bash
cd tesis2/parcial3/entregable/5_cierre_examen_parcial_mlops
../../../.venv/bin/python build_notebook_paso5.py
../../../.venv/bin/python run_cierre_examen.py
../../../.venv/bin/python run_auditoria_paso5.py
../../../.venv/bin/python build_parcial_informe_pdf.py   # genera Parcial_Informe.pdf
../../../.venv/bin/python build_presentacion_examen.py   # Presentacion_Examen_Parcial.pdf
../../../.venv/bin/python build_presentacion_criticidad.py  # Presentacion_Modulo_Criticidad.pdf
# Auditoría global desde raíz entregable:
cd .. && ../../.venv/bin/python run_auditoria_entregable_completo.py
```

Requisito: artefactos PASO 0→4 generados previamente.

### Generar `Parcial_Informe.pdf` (fuente en `6_otros/`)

```bash
cd tesis2/parcial3/entregable/6_otros
../../../.venv/bin/python build_parcial_informe_pdf.py
```

Ver también [`6_otros/README.md`](6_otros/README.md).
