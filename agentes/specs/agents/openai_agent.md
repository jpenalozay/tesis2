# 🤖 OPENAI AGENT - Especificación Completa

**ID**: `openai`  
**Versión**: 1.0  
**Prioridad**: Media  
**Estado**: Habilitado  

---

## 📋 DESCRIPCIÓN GENERAL

El **OpenAI Agent** es un agente especializado en validar integración OpenAI, optimizar prompts, gestionar tokens y costos. Su responsabilidad principal es asegurar que la integración con OpenAI sea eficiente, costeable y confiable.

---

## 🎯 RESPONSABILIDADES PRINCIPALES

1. **Validación de Integración**: API key, Assistant ID, manejo de errores, timeouts
2. **Optimización de Prompts**: Reducción de tokens, claridad, efectividad
3. **Monitoreo de Costos**: Tracking de tokens, cálculo de costos, límites, alertas
4. **Validación de Rate Limits**: Manejo de rate limits, retry logic, backoff exponencial
5. **Validación de Respuestas**: Procesamiento, formato, manejo de errores
6. **Monitoreo de Performance**: Tiempo de respuesta, tasa de éxito, detección de problemas
7. **Sugerencias de Optimización**: Mejoras de prompts, reducción de tokens, mejoras de costo

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos

```json
{
  "patterns": [
    "app/backend/services/external/openai*.py",
    "app/backend/core/config.py"
  ]
}
```

### Archivos Específicos

- `app/backend/services/external/openai_service.py` - Servicio principal OpenAI
- `app/backend/services/external/openai_advanced.py` - Servicio avanzado OpenAI
- `app/backend/core/config.py` - Configuración OpenAI

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `validate_integration()`

**Descripción**: Valida integración con OpenAI API

**Reglas de Validación**:
- ✅ API key debe estar configurada
- ✅ Assistant ID debe estar configurado
- ✅ Debe manejar errores de API apropiadamente
- ✅ Debe tener timeouts configurados
- ✅ Debe tener retry logic para rate limits
- ✅ Debe usar cliente async apropiadamente
- ✅ Debe tener manejo de excepciones específicas de OpenAI

**Output**:
```json
{
  "status": "valid|invalid",
  "integration_issues": [
    {
      "type": "missing_api_key",
      "recommendation": "Configure OPENAI_API_KEY in .env"
    }
  ]
}
```

---

### 2. `optimize_prompts()`

**Descripción**: Optimiza prompts para reducir tokens y mejorar efectividad

**Reglas de Validación**:
- ✅ Prompts deben ser claros y concisos
- ✅ Debe evitar tokens innecesarios
- ✅ Debe usar instrucciones específicas
- ✅ Debe incluir ejemplos cuando sea apropiado
- ✅ Debe evitar repetición de información
- ✅ Debe usar formato apropiado para el modelo

**Output**:
```json
{
  "status": "optimized|needs_optimization",
  "suggestions": [
    {
      "prompt": "Generate a response...",
      "current_tokens": 150,
      "optimized_tokens": 120,
      "savings": "20%",
      "recommendation": "Remove redundant phrases"
    }
  ]
}
```

---

### 3. `monitor_costs()`

**Descripción**: Monitorea costos de OpenAI y tokens usados

**Reglas de Validación**:
- ✅ Debe trackear tokens usados por request
- ✅ Debe calcular costos por request
- ✅ Debe tener límites configurados
- ✅ Debe alertar sobre costos altos
- ✅ Debe trackear costos diarios y mensuales
- ✅ Debe registrar métricas de uso

**Output**:
```json
{
  "status": "tracking|not_tracking",
  "costs": {
    "daily": 0.50,
    "monthly": 15.00,
    "limit": 100.00,
    "percentage_used": 15
  },
  "tokens": {
    "total_today": 50000,
    "total_month": 1500000,
    "avg_per_request": 150
  },
  "alerts": []
}
```

---

### 4. `validate_rate_limits()`

**Descripción**: Valida manejo de rate limits de OpenAI

**Reglas de Validación**:
- ✅ Debe manejar rate limits apropiadamente
- ✅ Debe tener retry logic con backoff exponencial
- ✅ Debe evitar exceder límites de tokens
- ✅ Debe manejar errores de rate limit específicos

---

### 5. `validate_responses()`

**Descripción**: Valida calidad y formato de respuestas de OpenAI

**Reglas de Validación**:
- ✅ Respuestas deben ser procesadas apropiadamente
- ✅ Debe manejar respuestas vacías
- ✅ Debe manejar errores en respuestas
- ✅ Debe validar formato de respuestas
- ✅ Debe extraer contenido correctamente

---

### 6. `monitor_performance()`

**Descripción**: Monitorea performance de llamadas a OpenAI

**Reglas de Validación**:
- ✅ Debe trackear tiempo de respuesta
- ✅ Debe trackear tiempo de espera
- ✅ Debe detectar timeouts
- ✅ Debe monitorear tasa de éxito
- ✅ Debe detectar respuestas lentas

---

### 7. `suggest_optimizations()`

**Descripción**: Sugiere optimizaciones para uso de OpenAI

**Output**:
```json
{
  "suggestions": [
    {
      "type": "prompt_optimization",
      "priority": "high",
      "current_tokens": 200,
      "optimized_tokens": 150,
      "savings_percentage": 25,
      "recommendation": "Remove redundant instructions"
    }
  ]
}
```

---

## ⚙️ CONFIGURACIÓN

### Parámetros de Configuración

```json
{
  "agent": "openai",
  "enabled": true,
  "priority": "medium",
  "config": {
    "validate_on_change": true,
    "max_tokens_per_request": 1500,
    "daily_cost_limit_usd": 10.0,
    "monthly_cost_limit_usd": 300.0,
    "target_response_time_ms": 20000
  }
}
```

---

## 📤 FORMATO DE FEEDBACK

```json
{
  "agent": "openai",
  "trigger_id": "openai-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/backend/services/external/openai_service.py",
  "results": {
    "integration_status": "valid",
    "prompts_optimized": 3,
    "costs_tracked": true,
    "performance_score": 88
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 🧪 TESTING Y PERFORMANCE

### Análisis Automatizado

- **Análisis de Costos**: Diario a las 06:00 AM
- **Análisis de Performance**: Diario a las 07:00 AM

### Métricas Monitoreadas

- **Costos**: Límite diario $10, mensual $300
- **Tokens**: Máximo 1500 por request, warning 1200
- **Performance**: Máximo 30s de respuesta, warning 20s
- **Tasa de Éxito**: Objetivo 95%

---

## ✅ RESUMEN DE CARACTERÍSTICAS DEL AGENTE OPENAI

### Funcionalidades Principales
- ✅ Validación completa de integración OpenAI
- ✅ Optimización de prompts y tokens
- ✅ Monitoreo de costos y límites
- ✅ Validación de rate limits
- ✅ Monitoreo de performance
- ✅ Sugerencias de optimización

### Monitoreo
- ✅ Monitoreo automático de cambios en código OpenAI
- ✅ Activación automática al modificar archivos
- ✅ Análisis continuo de costos y performance

### Testing y Performance
- ✅ Análisis automatizado diario
- ✅ Tracking de costos y tokens
- ✅ Reportes detallados en formato JSON
- ✅ Alertas de costos y límites

---

**Última actualización**: 2025-01-XX

