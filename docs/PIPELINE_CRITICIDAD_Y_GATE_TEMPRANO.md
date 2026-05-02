# Pipeline de criticidad, baseline y gate temprano

Este documento consolida el diseño (marco multi-agente, política `play` / `pausa` / `stop`) y las extensiones implementadas.

## 1. Baseline mínimo (clasificación de las tres clases)

Objetivo: línea base **simple y reproducible** antes de comparar con el Sentinel u otros LLM.

| Paso | Detalle |
|------|---------|
| Entrada | Texto `requirement`, etiqueta `gold_mode`. |
| Partición | Validación cruzada estratificada o hold-out estratificado. |
| Representación | TF-IDF (n-gramas de palabra 1–2). |
| Modelo | Regresión logística multinomial, SGD log-loss o Naive Bayes multinomial. |
| Métricas | **F1-macro**, **κ** (concordancia), matriz de confusión; ROC-AUC multiclase solo si se define bien (p. ej. OvR macro). |
| Lectura | Si el baseline sube “demasiado” solo por léxico, revisar **leakage** (como en el EDA); si es bajo, el texto solo no basta y refuerza el papel del pipeline profundo. |

---

## 3. Agentes del framework (referencia)

Orden **original** en `CoordinatorV3` (v3):

1. **Arquitecto** → blueprint  
2. **UI/UX Designer** → especificación de interfaz  
3. **Sentinel** → riesgo sobre **blueprint** (no sobre texto crudo)  
4. **Coder** → código  
5. **Test Designer** → tests  
6. **Test Executor** → ejecución  
7. **Linter** → calidad  
8. **Auditor** → trazas  

**Agente de requisito** explícito: no es obligatorio si el coordinador ya recibe un único string; tiene sentido como capa aparte si hay tickets estructurados, adjuntos o normalización desde herramientas externas.

---

## 4. Gate temprano (implementación en `agentes/`)

**Motivo:** el modelo operativo sin contexto de repositorio puede **dudar** al clasificar solo por texto; el Sentinel completo actúa **después** del blueprint y es más costoso.

**Ubicación del código:**

- `agentes/core/early_gate.py` — decisión temprana.
- `agentes/core/coordinator_v3_gated.py` — orquestador que llama al gate **antes** del Arquitecto y adjunta el resultado en `early_gate` / `agents.early_gate`.

**Política del gate:**

1. **LLM** — una llamada que devuelve JSON: `gold_mode`, `confidence`, `doubt`, `reason`.  
   - `doubt=true` cuando falta conocimiento del proyecto o el propio modelo declara incertidumbre.

2. Si **duda** o **confianza baja** → **fallback léxico**: reglas ponderadas en español (palabras asociadas a stop / pausa / play).

3. **Fusión:** si el LLM es claro y confiado, se respeta; si no, se prioriza el léxico cuando tiene peso alto, con reglas conservadoras ante conflicto (más restrictivo entre candidatos).

**Qué no es:** no reemplaza al Sentinel sobre blueprint; es una **señal previa** para trazabilidad, experimentos comparativos y futuros cortocircuitos opcionales (política de producto).

**“Sentinel solo texto” / embeddings livianos:** en esta implementación el segundo escalón es **léxico** (sin dependencia extra). Se puede extender con embeddings sentence-transformers o una segunda llamada LLM más corta si se desea alinear literalmente con ese diseño.

---

## 5. Mejor flujo

**Lectura A (coste):** colocar el gate **antes** del Arquitecto evita asumir que todo el coste LLM posterior está justificado sin una primera señal de criticidad.

**Lectura B (evaluación):** conviene distinguir experimentos: **solo texto** vs **tras blueprint**; son dos preguntas distintas y ambas defendibles si se declaran.

---

## 6. Uso rápido del coordinador con gate

Desde el directorio `agentes/` (con `PYTHONPATH` o instalación editable según tu entorno):

```python
from core.coordinator_v3_gated import CoordinatorV3Gated

coord = CoordinatorV3Gated(enable_early_gate=True)
resultado = coord.process("Tu requerimiento aquí...")
print(resultado.get("early_gate"))
```

Variables opcionales: `EARLY_GATE_CONFIDENCE_OK`, `EARLY_GATE_DOUBT_CONF` (ver `early_gate.py`).

---

## 7. Referencias en este repo

| Ruta | Contenido |
|------|-----------|
| `data/criticidad_cases/` | Corpus gold + EDA + protocolo (redacción neutra). |
| `agentes/core/early_gate.py` | Gate temprano. |
| `agentes/core/coordinator_v3_gated.py` | Orquestador v3 + gate. |
| `src/` | Utilidades de corpus y verificación (uso reproducibilidad interna). |
