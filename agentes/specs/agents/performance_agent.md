# ⚡ PERFORMANCE & STABILITY AGENT - Especificación Completa

**ID**: `performance`  
**Versión**: 1.0  
**Prioridad**: Alta  
**Estado**: Habilitado  

---

## 📋 DESCRIPCIÓN GENERAL

El **Performance & Stability Agent** es un agente especializado en optimización de performance, detección de cuellos de botella, validación de manejo de errores y logging. Su responsabilidad principal es asegurar que la aplicación sea rápida, estable y confiable.

---

## 🎯 RESPONSABILIDADES PRINCIPALES

1. **Análisis de Performance**: Queries SQL, async/await, caching, connection pooling
2. **Detección de Cuellos de Botella**: Queries lentas, operaciones bloqueantes, memory leaks
3. **Validación de Manejo de Errores**: Try/except, retry logic, circuit breakers, recovery
4. **Validación de Logging**: Niveles, formato, contexto, seguridad
5. **Validación de Operaciones Async**: Uso correcto de async/await, evitar bloqueos
6. **Validación de Caching**: Estrategias de cache, TTL, invalidación
7. **Validación de Timeouts**: Timeouts para operaciones externas
8. **Validación de Limpieza de Recursos**: Context managers, cleanup apropiado
9. **Sugerencias de Optimización**: Mejoras basadas en análisis del código

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos

```json
{
  "patterns": [
    "app/**/*.py",
    "app/backend/**/*.py",
    "app/main.py"
  ]
}
```

### Archivos Específicos

- `app/main.py` - Aplicación principal FastAPI
- `app/backend/core/logging.py` - Sistema de logging
- `app/backend/database/connection.py` - Conexión a BD
- `app/backend/database/core_connection.py` - Connection pooling avanzado
- `app/backend/services/**/*.py` - Todos los servicios
- `app/backend/core/config.py` - Configuración

### Directorios Monitoreados

- `app/backend/` - Todo el código backend
- `app/backend/services/` - Servicios de negocio
- `app/backend/core/` - Core y configuración
- `app/backend/database/` - Base de datos
- `logs/` - Archivos de logs

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `analyze_performance()`

**Descripción**: Analiza performance del código

**Reglas de Validación**:
- ✅ Queries deben evitar N+1 problems
- ✅ Operaciones I/O deben ser async
- ✅ Debe usar cache cuando sea apropiado
- ✅ No debe bloquear el event loop
- ✅ Debe usar connection pooling
- ✅ Queries SQL deben estar optimizadas
- ✅ Debe evitar queries innecesarias
- ✅ Debe usar índices apropiados
- ✅ Debe evitar `select *` cuando sea posible
- ✅ Debe usar paginación para grandes datasets

**Output**:
```json
{
  "status": "good|needs_optimization",
  "performance_issues": [
    {
      "type": "n_plus_one",
      "file": "app/main.py",
      "line": 165,
      "description": "Query in loop detected",
      "recommendation": "Use eager loading"
    }
  ],
  "query_analysis": {
    "slow_queries": [],
    "n_plus_one_queries": [],
    "optimization_suggestions": []
  }
}
```

---

### 2. `check_error_handling()`

**Descripción**: Verifica manejo de errores y recovery mechanisms

**Reglas de Validación**:
- ✅ Errores deben loguearse con contexto
- ✅ Debe tener retry logic para operaciones críticas
- ✅ Debe tener circuit breakers para servicios externos
- ✅ Errores no deben causar crashes
- ✅ Debe tener manejo de timeouts
- ✅ Debe manejar errores de conexión apropiadamente
- ✅ Debe tener fallbacks para servicios externos
- ✅ Errores deben tener mensajes descriptivos
- ✅ Debe evitar exponer stack traces a usuarios

**Output**:
```json
{
  "status": "good|needs_improvement",
  "missing_error_handling": [
    {
      "file": "app/main.py",
      "function": "api_chat",
      "line": 450,
      "recommendation": "Add try/except for OpenAI API call"
    }
  ],
  "logging_issues": [],
  "retry_logic": {
    "present": true,
    "missing": []
  }
}
```

---

### 3. `validate_logging()`

**Descripción**: Valida sistema de logging

**Reglas de Validación**:
- ✅ Debe usar niveles apropiados (DEBUG, INFO, WARNING, ERROR)
- ✅ Logs deben tener contexto suficiente
- ✅ No debe loguear información sensible
- ✅ Debe tener formato estructurado
- ✅ Debe usar loggers apropiados por módulo
- ✅ Debe tener rotación de logs configurada
- ✅ Debe evitar logs excesivos en producción
- ✅ Logs deben ser útiles para debugging

**Output**:
```json
{
  "status": "good|needs_improvement",
  "logging_issues": [
    {
      "file": "app/main.py",
      "line": 125,
      "type": "sensitive_data",
      "recommendation": "Remove sensitive data from log"
    }
  ],
  "logger_configuration": {
    "appropriate": true,
    "issues": []
  }
}
```

---

### 4. `detect_bottlenecks()`

**Descripción**: Detecta cuellos de botella en el código

**Reglas de Validación**:
- ✅ Detectar queries lentas
- ✅ Detectar operaciones bloqueantes
- ✅ Detectar uso excesivo de memoria
- ✅ Detectar código que puede ser optimizado
- ✅ Detectar patrones anti-performance

**Output**:
```json
{
  "bottlenecks": [
    {
      "type": "slow_query",
      "file": "app/main.py",
      "line": 165,
      "query_time_ms": 2500,
      "recommendation": "Add index or optimize query"
    }
  ],
  "suggestions": []
}
```

---

### 5. `check_async_operations()`

**Descripción**: Verifica uso correcto de async/await

**Reglas de Validación**:
- ✅ Operaciones I/O deben ser async
- ✅ Debe usar await apropiadamente
- ✅ No debe bloquear el event loop
- ✅ Debe usar `asyncio.gather` para operaciones paralelas
- ✅ Debe manejar excepciones async apropiadamente

---

### 6. `validate_caching()`

**Descripción**: Valida uso de cache y estrategias de caching

**Reglas de Validación**:
- ✅ Debe usar cache para datos frecuentemente accedidos
- ✅ Cache debe tener TTL apropiado
- ✅ Cache debe ser invalidado cuando sea necesario
- ✅ Debe usar Redis cuando sea apropiado
- ✅ Cache debe ser eficiente

---

### 7. `check_memory_usage()`

**Descripción**: Verifica uso de memoria y posibles memory leaks

**Reglas de Validación**:
- ✅ Debe evitar memory leaks
- ✅ Debe liberar recursos apropiadamente
- ✅ Debe usar context managers cuando sea apropiado
- ✅ Debe evitar almacenar datos grandes en memoria
- ✅ Debe usar generators para grandes datasets

---

### 8. `validate_timeouts()`

**Descripción**: Valida configuración de timeouts

**Reglas de Validación**:
- ✅ Operaciones externas deben tener timeouts
- ✅ Timeouts deben ser apropiados
- ✅ Debe manejar timeouts apropiadamente
- ✅ Debe tener timeouts para HTTP requests
- ✅ Debe tener timeouts para DB queries

---

### 9. `check_resource_cleanup()`

**Descripción**: Verifica limpieza apropiada de recursos

**Reglas de Validación**:
- ✅ Conexiones deben cerrarse apropiadamente
- ✅ Archivos deben cerrarse apropiadamente
- ✅ Debe usar context managers
- ✅ Debe usar try/finally para cleanup
- ✅ Debe liberar recursos en excepciones

---

### 10. `suggest_optimizations()`

**Descripción**: Sugiere optimizaciones basadas en análisis del código

**Output**:
```json
{
  "suggestions": [
    {
      "type": "performance",
      "priority": "high",
      "file": "app/main.py",
      "line": 165,
      "recommendation": "Use eager loading to avoid N+1 queries",
      "impact": "high",
      "effort": "medium"
    }
  ]
}
```

---

## ⚙️ CONFIGURACIÓN

### Parámetros de Configuración

```json
{
  "agent": "performance",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "max_query_time": 1000,
    "require_async_io": true,
    "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR"]
  }
}
```

---

## 📤 FORMATO DE FEEDBACK

```json
{
  "agent": "performance",
  "trigger_id": "performance-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/main.py",
  "results": {
    "performance_score": 85,
    "stability_score": 90,
    "logging_score": 88,
    "error_handling_score": 92,
    "bottlenecks_detected": 2,
    "optimizations_suggested": 5
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 🧪 TESTING Y PERFORMANCE

### Análisis Automatizado

- **Análisis de Performance**: Diario a las 03:00 AM
- **Detección de Cuellos de Botella**: Diario a las 04:00 AM
- **Análisis de Logging**: Diario a las 05:00 AM

### Métricas Monitoreadas

- **Tiempo de Queries**: Máximo 1000ms, Warning 500ms
- **Uso de Memoria**: Máximo 512MB, Warning 256MB
- **Tasa de Errores**: Máximo 5%, Warning 2%
- **Logs por Minuto**: Máximo 1000, Warning 500

### Reportes

Los reportes se generan en formato JSON y se almacenan en:
- `agentes/reports/performance_agent_reports/`

---

## 📝 REGLAS ESPECÍFICAS

### Performance

**Prioridad**: Alta

**Requerido**:
- Operaciones I/O async
- Connection pooling
- Queries optimizadas
- Timeouts configurados

**Recomendado**:
- Caching apropiado
- Paginación para grandes datasets
- Lazy loading cuando sea apropiado
- Compresión de respuestas

**Prohibido**:
- N+1 queries
- Operaciones bloqueantes en async
- Queries sin límites
- `select *` innecesarios

### Error Handling

**Prioridad**: Alta

**Requerido**:
- Try/except apropiados
- Logging de errores
- Manejo de excepciones
- Timeouts para operaciones externas

**Recomendado**:
- Retry logic
- Circuit breakers
- Fallbacks
- Error recovery

**Prohibido**:
- Bare except
- Exponer stack traces
- Ignorar errores silenciosamente
- Crashes sin manejo

### Logging

**Prioridad**: Alta

**Requerido**:
- Niveles apropiados
- Contexto suficiente
- Formato estructurado
- No loguear información sensible

**Recomendado**:
- Rotación de logs
- Logs estructurados (JSON)
- Loggers por módulo
- Métricas de performance

**Prohibido**:
- Logs excesivos
- Información sensible en logs
- Logs sin contexto
- Niveles incorrectos

---

## 🔄 COMUNICACIÓN CON OTROS AGENTES

### Canales Redis

**Escucha**:
- `agent:performance:trigger`
- `agent:performance:analyze`
- `agent:performance:optimize`

**Publica**:
- `agent:performance:results`
- `agent:performance:bottlenecks`
- `agent:performance:optimizations`
- `agent:performance:warnings`

### Comunicación Basada en Archivos

- **Input**: `agentes/communication/performance_agent_input.json`
- **Output**: `agentes/communication/performance_agent_output.json`
- **Errors**: `agentes/communication/performance_agent_errors.json`

---

## ✅ RESUMEN DE CARACTERÍSTICAS DEL AGENTE PERFORMANCE

### Funcionalidades Principales
- ✅ Análisis completo de performance
- ✅ Detección de cuellos de botella
- ✅ Validación de manejo de errores
- ✅ Validación de logging
- ✅ Validación de operaciones async
- ✅ Validación de caching
- ✅ Validación de timeouts
- ✅ Sugerencias de optimización

### Monitoreo
- ✅ Monitoreo automático de cambios en código
- ✅ Activación automática al modificar archivos
- ✅ Análisis continuo de performance

### Testing y Performance
- ✅ Análisis automatizado diario
- ✅ Detección de cuellos de botella
- ✅ Análisis de logging
- ✅ Reportes detallados en formato JSON
- ✅ Métricas de performance monitoreadas

### Integración
- ✅ Comunicación con otros agentes vía Redis
- ✅ Comunicación basada en archivos JSON
- ✅ Integración con sistema de agentes maestro

---

**Última actualización**: 2025-01-XX

