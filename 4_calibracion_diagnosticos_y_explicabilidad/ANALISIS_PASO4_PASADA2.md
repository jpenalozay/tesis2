# PASO 4 — Calibración, diagnósticos y explicabilidad — PASADA 2 (auditoría)

**Fecha ejecución:** 12 junio 2026  
**Modo:** cache PASO 3 — sin re-API  
**Veredicto auditoría:** pasada1=OK · pasada2=✅

---

## 1. Calibración post-hoc (isotónica, fit train 280)

| Variante | ECE antes | ECE después | Brier antes | Brier después | ΔECE |
|----------|-----------|-------------|-------------|---------------|------|
| Baseline | 0,448 | **0,003** | 0,405 | 0,250 | −0,445 |
| Var1 | 0,440 | **0,035** | 0,313 | 0,170 | −0,405 |
| Var2 | 0,419 | **0,026** | 0,300 | 0,176 | −0,393 |

**Lectura:** confianzas crudas sobre-estiman accuracy (ECE ~0,42–0,45). Isotónica corrige sin alterar predicciones de clase. Platt disponible en CSV para comparación.

**Limitación:** calibración mejora métricas de confianza, no F1-stop ni EC (labels fijos).

---

## 2. Ablación middleware

| Componente ablado | F1-stop | EC | Override | ΔF1-stop | ΔEC |
|-------------------|---------|-----|----------|----------|-----|
| Var2 completo | 0,391 | 0,123 | 16,5 % | 0 | 0 |
| **sin_gate_b** | **0,057** | 0,147 | 0 % | **−0,334** | +0,024 |
| sin_senal_rag | 0,391 | 0,120 | 13,0 % | 0 | −0,003 |
| sin_fuzzy | 0,391 | 0,123 | 16,5 % | 0 | 0 |
| sin_eje_I_sec | 0,391 | 0,123 | 16,5 % | 0 | 0 |
| sin_eje_I_db | 0,391 | 0,123 | 16,5 % | 0 | 0 |

**Hallazgo crítico:** apagar Gate B reproduce el colapso Var1 (F1-stop 0,057). Fuzzy y ejes 4D individuales no cambian overrides en este corpus — la señal RAG modera overrides (−3,5 pp).

---

## 3. Explicabilidad overrides Gate B

| Señal | Importancia perm. | Interpretación |
|-------|-------------------|----------------|
| rag_uncertainty | **0,028** | Mayor incertidumbre RAG → más overrides conservadores |
| class_consensus | 0,003 | Consenso vecinos modula interceptación |
| I_mem | 0,001 | Eje memoria contribuye marginalmente |

Peso HPO mayor en `risk` (0,231) y `fuzzy_stop` (0,185); overrides empíricos dominados por incertidumbre RAG.

---

## 4. Sub-análisis piloto CrewAI n=40

| Métrica | Valor |
|---------|-------|
| n | 40 (crewai_cache) |
| F1-macro | 0,119 |
| F1-stop | 0,250 |
| FNR-stop | 0,667 |
| EC | 0,073 |

**No extrapolar a n=400:** fuera piloto 360 tickets usan abstención pausa (Chow 1970). Confirma decisión de no escalar CrewAI antes de PASO 4.

---

## 5. Veredicto final

**✅ OK** — PASO 4 IA06 completado; salvedad D5 documentada; Var2 validado por ablación `sin_gate_b`; calibración ECE mejorada en las tres variantes.

Artefactos clave: `8_informe_resumen_paso4.json`, figuras `2_`, `4_`, `6_`.

---

*Fin PASADA 2 — PASO 4 auditado.*
