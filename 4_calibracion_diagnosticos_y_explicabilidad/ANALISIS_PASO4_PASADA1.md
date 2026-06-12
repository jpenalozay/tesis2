# PASO 4 — Calibración, diagnósticos y explicabilidad (IA06) — PASADA 1 (diseño)

**Proyecto:** Framework multi-agente con middleware play/pausa/stop  
**Autor:** José Luis Peñaloza Yaurivilca — Maestría IA UNI  
**Fecha:** 12 junio 2026  
**Alcance:** diseño PASO 4 sobre predicciones cacheadas PASO 3 (sin re-API).

---

## 1. Objetivo IA06

Completar el ciclo experimental del parcial con:

1. **Calibración post-hoc** (Platt / isotónica) — ECE y Brier antes/después por variante.
2. **Ablación por componente middleware** — apagar Gate B, fuzzy, señal RAG o un eje 4D.
3. **Explicabilidad** — permutation importance sobre señales que disparan overrides Gate B.
4. **Sub-análisis piloto n=40** — métricas Var1 solo en tickets CrewAI reales.

---

## 2. Salvedad metodológica (documentada en PASO 3 y PASO 4)

| Punto | Justificación |
|-------|---------------|
| Var1 = 10 % CrewAI + 90 % abstención pausa | Diseño **D5** intencional; abstención alineada con Chow (1970) |
| No CrewAI n=400 | Costo API + agente permisivo desfavorable en piloto |
| Var2 contribución principal | Gate B demuestra ΔF1-stop +0,334 vs sin middleware |
| Sub-análisis n=40 | Documenta agente sin invalidar protocolo n=400 |

---

## 3. Diseño técnico

| Componente | Entrada | Salida |
|------------|---------|--------|
| Calibración | `3_`–`5_tabla_predicciones_*` | `1_tabla_calibracion_ece_brier_antes_despues.csv`, fig. 2 |
| Ablación | Var1 + PolicyEngine + RAG | `3_tabla_ablacion_componentes_middleware.csv`, fig. 4 |
| Explicabilidad | `5_tabla_predicciones_var2` + `2_tabla_senales` | `5_tabla_importancia_senales_overrides.csv`, fig. 6 |
| Piloto | Var1 filtro `crewai_cache` | `7_tabla_metricas_piloto_crewai_n40.csv` |

**Fit calibración:** split train 280 (`5_conjunto_entrenamiento_holdout_70.csv`); evalúa n=400 y holdout 120.

**Ablaciones planificadas:** `sin_gate_b`, `sin_fuzzy`, `sin_senal_rag`, `sin_eje_I_sec`, `sin_eje_I_db`.

---

## 4. Dependencias upstream

```
PASO 0 (eval n=400, train 280)
  → PASO 3 (predicciones cacheadas)
    → PASO 4 (calibración/ablación/explicabilidad)
```

---

## 5. Criterios de aceptación

- [x] ECE/Brier antes/después para Baseline, Var1, Var2
- [x] Tabla ΔF1-stop, ΔEC, Δoverride por componente
- [x] Importancia señales overrides Gate B
- [x] Métricas piloto n=40 con nota metodológica
- [x] Auditoría doble pasada
- [x] `honesty_notes` en JSON configuración y resumen

---

*Fin PASADA 1 — diseño PASO 4 IA06.*
