# Análisis PASO 5 — Pasada 2 (auditoría + veredicto final)

**Fecha:** 12 junio 2026 · **Ejecución:** `run_cierre_examen.py` + `run_auditoria_paso5.py`

---

## 1. Resultados ejecución

| Artefacto | Estado |
|-----------|--------|
| Tablero 13 filas | ✅ |
| Checklist 27/27 CUMPLIDO | ✅ 100% |
| Gap/overfitting JSON | ✅ |
| Guía demo 10 min | ✅ |
| Auditoría global 0→4 | ✅ OK (0 gaps) |
| Auditoría PASO 5 pasada 2 | ✅ |

---

## 2. Gap eval vs holdout (F1-stop)

| Variante | n=400 | holdout 120 | Δ | Interpretación |
|----------|-------|-------------|---|----------------|
| Baseline | 0,301 | 0,326 | +0,025 | Acotado |
| Var1 | 0,057 | 0,000 | −0,057 | Abstención D5, no overfitting |
| Var2 | 0,391 | **0,500** | **+0,109** | Generalización favorable |

**Conclusión:** No hay evidencia de overfitting clásico en Var2; holdout supera eval.

---

## 3. Gap calibración (ECE isotónica)

| Variante | n=400 | holdout 120 | Δ |
|----------|-------|-------------|---|
| Baseline | 0,003 | 0,011 | +0,007 |
| Var1 | 0,035 | 0,117 | +0,082 |
| Var2 | 0,026 | 0,087 | +0,061 |

Calibrador fit train 280 puede sobreajustar — validar en holdout antes de producción.

---

## 4. Alineación documental

Cruce automático Var2 F1-stop / override vs README, informe, presentación: **✅**

Salvedad D5/Chow presente en 3/3 documentos clave: **✅**

---

## 5. Gaps restantes (honestidad — no bloquean veredicto)

| Gap | Tipo |
|-----|------|
| Piloto CrewAI 10% | Alcance D5 |
| HITL USD supuesto | Documental |
| n_stop=30 | Estadístico |
| ECE holdout > n400 post-isotónica | Calibración |

---

## 6. Veredicto pasada 2

### **Veredicto PASO 5: ✅ APROBADO**

Detalle: `6_veredicto_final_entregable.md`, `9_informe_auditoria_pasada2_resultado_final.json`
