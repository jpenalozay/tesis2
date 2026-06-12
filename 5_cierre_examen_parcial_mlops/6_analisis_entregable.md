# Veredicto final entregable — Examen Parcial 

**Fecha:** 2026-06-12 · **PASO 5 IA08**

## Veredicto global

**✅ APROBADO**

- Checklist examen: **100.0%** (27/27)
- Auditoría pipeline 0→4: **OK**
- Experimentos en tablero: **13**

## Métricas clave (fuente CSV)

| Variante | F1-macro | F1-STOP | Override |
|----------|----------|---------|----------|
| Baseline | 0.362 | 0.301 | — |
| Var1 | 0.335 | 0.057 | 0% |
| Var2 | **0.435** | **0.391** | **16.5%** |

## Checklist IA08 — items pendientes

Todos los ítems verificados como CUMPLIDO o PARCIAL documentado.

## Gaps metodológicos (honestidad)

- Piloto CrewAI 10% (D5)
- HITL cost supuesto
- n_stop=30 — bajo poder McNemar
- Proxy Bugzilla severity

## Comandos reproducibilidad

```bash
cd tesis2/parcial3/entregable/5_cierre_examen_parcial_mlops
../../../.venv/bin/python run_cierre_examen.py
../../../.venv/bin/python run_auditoria_paso5.py
cd .. && ../../../.venv/bin/python run_auditoria_entregable_completo.py
```

Detalle: `ANALISIS_ENTREGABLE_SINTESIS_FINAL.md`, `VERIFICACION_ENTREGABLE_PASADA3.md`.
