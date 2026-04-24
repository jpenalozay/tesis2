# 📊 AGENTE DB - PLAN DE PRUEBAS Y PERFORMANCE

**Versión**: 1.0  
**Última actualización**: 2025-01-XX

---

## 🎯 ¿QUÉ ES EL SISTEMA DE PRUEBAS Y PERFORMANCE?

El Agente DB incluye un **sistema completo de pruebas y análisis de performance** que se ejecuta automáticamente según horarios programados. Este sistema:

- ✅ **Ejecuta pruebas** automáticamente según plan
- ✅ **Analiza performance** en tiempo real y por volumen
- ✅ **Detecta cuellos de botella** automáticamente
- ✅ **Investiga por qué** se demoran las operaciones
- ✅ **Sugiere optimizaciones** basadas en los resultados

---

## 📅 PLAN DE PRUEBAS AUTOMATIZADAS

### Pruebas Diarias (02:00 AM)

Se ejecutan **todos los días a las 2:00 AM**:

#### 1. **Test de Conexión a Base de Datos** 🔴 CRITICAL
- **Qué hace**: Verifica que la conexión a la BD funcione
- **Timeout**: 30 segundos
- **Resultado esperado**: Conexión exitosa

#### 2. **Test de Connection Pool** 🟠 HIGH
- **Qué hace**: Verifica que el pool de conexiones esté funcionando
- **Timeout**: 60 segundos
- **Resultado esperado**: Pool con al menos 5 conexiones disponibles

#### 3. **Test de Integridad de Modelos** 🟠 HIGH
- **Qué hace**: Valida que todos los modelos SQLAlchemy estén correctos
- **Timeout**: 120 segundos
- **Resultado esperado**: Todos los modelos válidos

#### 4. **Test de Foreign Keys** 🔴 CRITICAL
- **Qué hace**: Verifica que todas las foreign keys sean válidas
- **Timeout**: 180 segundos
- **Resultado esperado**: Todas las FK válidas

#### 5. **Test de Índices Existentes** 🟡 MEDIUM
- **Qué hace**: Verifica que los índices esperados existan
- **Timeout**: 120 segundos
- **Resultado esperado**: Todos los índices presentes

---

### Pruebas Semanales (Domingo 03:00 AM)

Se ejecutan **cada domingo a las 3:00 AM**:

#### 1. **Test de Migraciones** 🟠 HIGH
- **Qué hace**: Verifica que todas las migraciones estén aplicadas
- **Timeout**: 5 minutos
- **Resultado esperado**: Todas las migraciones aplicadas

#### 2. **Test de Integridad de Datos** 🟠 HIGH
- **Qué hace**: Verifica que no haya registros huérfanos
- **Timeout**: 10 minutos
- **Resultado esperado**: Sin registros huérfanos

#### 3. **Test de Naming Conventions** 🟡 MEDIUM
- **Qué hace**: Verifica que se sigan las convenciones de nombres
- **Timeout**: 3 minutos
- **Resultado esperado**: Convenciones seguidas

---

## ⚡ PLAN DE ANÁLISIS DE PERFORMANCE

### Análisis Horario (Cada Hora)

Se ejecuta **cada hora automáticamente**:

#### 1. **Análisis de Queries Lentas** 🟠 HIGH
- **Qué hace**: Detecta queries que toman más de 1 segundo
- **Métricas**:
  - Cantidad de queries lentas
  - Tiempo promedio de ejecución
  - Tiempo máximo de ejecución
  - Queries más lentas
  - Patrones de queries

#### 2. **Análisis de Connection Pool** 🟠 HIGH
- **Qué hace**: Analiza el uso del pool de conexiones
- **Umbrales**:
  - Utilización del pool > 80%
  - Tiempo de espera > 100ms
  - Overflow > 5 conexiones
- **Métricas**:
  - Tamaño del pool
  - Conexiones activas
  - Conexiones idle
  - Tiempo de espera
  - Cantidad de overflow

#### 3. **Análisis de Tamaños de Tablas** 🟡 MEDIUM
- **Qué hace**: Detecta tablas que crecen rápidamente
- **Umbral**: Tablas con más de 10K registros
- **Métricas**:
  - Filas por tabla
  - Tamaño de tabla en MB
  - Tamaño de índices en MB
  - Tasa de crecimiento por día

---

### Análisis Diario de Performance por Volumen (04:00 AM)

Se ejecuta **todos los días a las 4:00 AM**:

#### 1. **Análisis de Performance por Volumen** 🔴 CRITICAL

**¿Qué hace?**
Analiza qué parte del modelo se demora más con volumen creciente de datos.

**Escenarios de Prueba**:

1. **Volumen Pequeño** (< 1K registros)
   - Baseline para comparación
   - `users`: 100 registros
   - `conversations`: 500 registros
   - `messages`: 2,000 registros

2. **Volumen Medio** (1K - 10K registros)
   - `users`: 1,000 registros
   - `conversations`: 5,000 registros
   - `messages`: 20,000 registros

3. **Volumen Grande** (10K - 100K registros)
   - `users`: 10,000 registros
   - `conversations`: 50,000 registros
   - `messages`: 200,000 registros

4. **Volumen Muy Grande** (> 100K registros)
   - `users`: 100,000 registros
   - `conversations`: 500,000 registros
   - `messages`: 2,000,000 registros

**Queries que se Prueban**:

1. **Obtener Conversaciones de Usuario**
   ```sql
   SELECT * FROM conversations 
   WHERE user_id = ? 
   ORDER BY created_at DESC 
   LIMIT 20
   ```
   - ⏱️ Esperado: 50ms (pequeño) → 2,000ms (muy grande)

2. **Obtener Mensajes de Conversación**
   ```sql
   SELECT * FROM messages 
   WHERE conversation_id = ? 
   ORDER BY created_at ASC
   ```
   - ⏱️ Esperado: 50ms (pequeño) → 5,000ms (muy grande)

3. **Obtener Todos los Mensajes de Usuario**
   ```sql
   SELECT * FROM messages 
   WHERE user_id = ? 
   ORDER BY created_at DESC 
   LIMIT 100
   ```
   - ⏱️ Esperado: 100ms (pequeño) → 8,000ms (muy grande)

4. **Contar Conversaciones por Usuario**
   ```sql
   SELECT COUNT(*) FROM conversations 
   WHERE user_id = ?
   ```
   - ⏱️ Esperado: 10ms (pequeño) → 1,000ms (muy grande)

5. **Obtener Chats Asignados a Asesor**
   ```sql
   SELECT * FROM chat_assignments 
   WHERE asesor_id = ? 
   AND status = 'active'
   ```
   - ⏱️ Esperado: 50ms (pequeño) → 4,000ms (muy grande)

6. **JOIN Usuario con Conversaciones**
   ```sql
   SELECT u.*, c.* 
   FROM users u 
   JOIN conversations c ON u.id = c.user_id 
   WHERE u.id = ?
   ```
   - ⏱️ Esperado: 100ms (pequeño) → 8,000ms (muy grande)

**Métricas que se Analizan**:
- ⏱️ Tiempo de ejecución (ms)
- 📊 Filas escaneadas
- 🔍 Uso de índices
- 🔎 Full table scans
- 💾 Uso de tablas temporales
- 🔄 Operaciones de ordenamiento
- 🔒 Tiempo de espera de locks

---

#### 2. **Detección de Cuellos de Botella** 🔴 CRITICAL

**¿Qué hace?**
Identifica qué partes del modelo se demoran más y **investiga por qué**.

**Cuándo se Activa**:
- Query toma más de 1 segundo
- Degradación de performance > 50%
- Tasa de errores > 1%

**Proceso de Investigación** (5 pasos):

**Paso 1: Análisis de EXPLAIN**
- Ejecuta `EXPLAIN ANALYZE` para ver el plan de ejecución
- Detecta:
  - ✅ Full table scans
  - ✅ Índices no usados
  - ✅ Índices incorrectos usados
  - ✅ Tablas temporales usadas
  - ✅ Filesort usado

**Paso 2: Análisis de Índices**
- Verifica si los índices necesarios existen y se usan
- Detecta:
  - ✅ Índices faltantes
  - ✅ Índices no usados
  - ✅ Índices duplicados
  - ✅ Selectividad de índices

**Paso 3: Análisis de Volumen**
- Analiza el tamaño de las tablas y crecimiento
- Detecta:
  - ✅ Crecimiento de tamaño de tablas
  - ✅ Crecimiento de tamaño de índices
  - ✅ Fragmentación
  - ✅ Cardinalidad

**Paso 4: Análisis de Bloqueos**
- Verifica si hay bloqueos que causen lentitud
- Detecta:
  - ✅ Esperas de locks
  - ✅ Deadlocks
  - ✅ Table locks
  - ✅ Row locks

**Paso 5: Análisis de Relaciones**
- Analiza si las relaciones causan problemas
- Detecta:
  - ✅ N+1 queries
  - ✅ Problemas de eager loading
  - ✅ Overhead de lazy loading
  - ✅ Operaciones en cascada

**Motor de Sugerencias**:
Después de la investigación, genera sugerencias automáticas:

- 🔍 **Índices faltantes**: Sugiere agregar índices
- ⚡ **Optimización de índices**: Sugiere modificar índices existentes
- 🚀 **Optimización de queries**: Sugiere mejorar queries
- 📊 **Particionamiento de tablas**: Sugiere particionar tablas grandes
- 📦 **Estrategia de archivado**: Sugiere archivar datos antiguos
- 💾 **Estrategia de caché**: Sugiere usar caché
- 🔗 **Optimización de pool**: Sugiere ajustar el pool de conexiones

---

### Análisis Semanal de Optimización (Sábado 05:00 AM)

Se ejecuta **cada sábado a las 5:00 AM**:

#### 1. **Optimización de Índices** 🟠 HIGH
- Analiza y sugiere optimizaciones de índices
- Identifica índices no usados
- Identifica índices duplicados

#### 2. **Optimización de Queries** 🟠 HIGH
- Analiza y sugiere optimizaciones de queries
- Detecta N+1 queries
- Sugiere mejoras de queries

#### 3. **Optimización de Esquema** 🟡 MEDIUM
- Analiza posibles mejoras en el esquema
- Sugiere mejoras de normalización
- Sugiere optimizaciones estructurales

---

## 📊 RESULTADOS Y REPORTES

### Almacenamiento de Resultados

- **Formato**: JSON
- **Ubicación**: `.agents/results/{agent_id}/`
- **Retención**: 90 días
- **Compresión**: No (por ahora)

### Reportes Generados

- **Formato**: JSON + Markdown
- **Ubicación**: `.agents/reports/{agent_id}/`
- **Dashboard**: Sí (visualización)
- **Alertas por email**: No (por ahora)
- **Alertas por Slack**: No (por ahora)

### Métricas

- **Recolección**: Sí
- **Granularidad**: Por minuto
- **Agregación**: Por hora, día, semana

---

## 🚨 ALERTAS Y NOTIFICACIONES

### Umbrales de Alerta

#### 🔴 CRITICAL
- **Fallo de prueba**: Notificación inmediata
- **Cuello de botella crítico**: Query > 5 segundos → Notificación inmediata

#### 🟠 WARNING
- **Degradación de performance**: > 50% más lento → Notificación
- **Performance degradada**: > 1 segundo → Notificación

#### 🟢 INFO
- **Crecimiento de volumen**: > 20% de crecimiento → Solo log

---

## 🔄 AUTOMATIZACIÓN

### Auto-Fix (Deshabilitado por Defecto)

- **Estado**: Deshabilitado
- **Acciones permitidas** (si se habilita):
  - Agregar índices faltantes
  - Optimizar queries
  - Actualizar estadísticas
- **Requiere aprobación**: Sí

### Auto-Suggest (Habilitado)

- **Estado**: Habilitado
- **Prioridad**: Media
- **Qué hace**: Genera sugerencias automáticamente después de análisis

---

## 📋 EJEMPLO DE RESULTADO DE ANÁLISIS

### Ejemplo: Análisis de Performance por Volumen

```json
{
  "analysis_id": "perf_volume_analysis",
  "timestamp": "2025-01-15T04:00:00Z",
  "results": {
    "q_get_user_conversations": {
      "small_volume": {
        "execution_time_ms": 45,
        "status": "ok",
        "rows_scanned": 500,
        "index_used": true
      },
      "medium_volume": {
        "execution_time_ms": 95,
        "status": "ok",
        "rows_scanned": 5000,
        "index_used": true
      },
      "large_volume": {
        "execution_time_ms": 520,
        "status": "warning",
        "rows_scanned": 50000,
        "index_used": true,
        "degradation": "13% slower than expected"
      },
      "xlarge_volume": {
        "execution_time_ms": 2500,
        "status": "critical",
        "rows_scanned": 500000,
        "index_used": true,
        "degradation": "25% slower than expected",
        "bottleneck_detected": true
      }
    },
    "bottleneck_analysis": {
      "detected_bottlenecks": [
        {
          "query": "q_get_user_conversations",
          "severity": "high",
          "volume_scenario": "xlarge_volume",
          "execution_time_ms": 2500,
          "expected_ms": 2000,
          "investigation": {
            "step_1_explain": {
              "full_table_scan": false,
              "index_used": "idx_conversations_user_id",
              "temporary_table": false,
              "filesort": true
            },
            "step_2_indexes": {
              "missing_indexes": [],
              "unused_indexes": [],
              "recommendation": "Add composite index on (user_id, created_at)"
            },
            "step_3_volume": {
              "table_size_mb": 450,
              "index_size_mb": 120,
              "growth_rate_per_day": "2.5%"
            },
            "step_4_locks": {
              "lock_waits": 0,
              "deadlocks": 0
            },
            "step_5_relations": {
              "n_plus_one_detected": false
            }
          },
          "suggestions": [
            {
              "type": "missing_index",
              "priority": "high",
              "recommendation": "Add composite index: CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at DESC)",
              "expected_improvement": "Reduce execution time by 40-60%"
            },
            {
              "type": "query_optimization",
              "priority": "medium",
              "recommendation": "Consider pagination with cursor-based approach instead of OFFSET",
              "expected_improvement": "Better performance with large datasets"
            }
          ]
        }
      ]
    }
  }
}
```

---

## 📁 ARCHIVOS RELACIONADOS

- **Configuración JSON**: `db_agent_test_performance.json` - Configuración completa
- **Configuración del Agente**: `db_agent.json` - Configuración general
- **Conocimiento**: `db_agent_knowledge.json` - Conocimiento del modelo

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Puedo cambiar los horarios de ejecución?**  
R: Sí, edita `db_agent_test_performance.json` y modifica los horarios en `schedules`.

**P: ¿Los análisis se ejecutan en producción?**  
R: Por defecto solo en desarrollo. Puedes habilitarlos en producción editando la configuración.

**P: ¿Puedo deshabilitar algún análisis?**  
R: Sí, edita `db_agent_test_performance.json` y marca `enabled: false` en el análisis específico.

**P: ¿Cómo veo los resultados?**  
R: Los resultados se guardan en `.agents/results/db/` y los reportes en `.agents/reports/db/`.

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0

