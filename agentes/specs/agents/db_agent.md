# 🗄️ AGENTE DB - GUÍA COMPLETA PARA DESARROLLADORES

**Versión**: 2.0  
**Entorno**: Desarrollo (DEV)  
**Última actualización**: 2025-01-XX

---

## 📖 ¿QUÉ ES EL AGENTE DB?

El **Agente DB** es un agente especializado que se encarga de validar y optimizar todo lo relacionado con la base de datos del proyecto. Su trabajo es asegurar que los modelos de datos, migraciones SQL y estructura de base de datos sigan las mejores prácticas.

---

## 🎯 ¿QUÉ HACE EL AGENTE DB?

### Funciones Principales

1. **Validar Modelos de Datos**
   - Verifica que cada tabla tenga primary key
   - Valida foreign keys y relaciones
   - Revisa tipos de datos correctos
   - Sugiere mejoras de normalización

2. **Validar Migraciones SQL**
   - Verifica sintaxis SQL correcta
   - Asegura compatibilidad con MySQL 8.0+
   - Detecta operaciones peligrosas

3. **Optimizar Queries**
   - Detecta problemas de performance (N+1 queries)
   - Sugiere índices faltantes
   - Analiza queries lentas

4. **Validar Naming Conventions**
   - Nombres de tablas correctos
   - Nombres de columnas correctos
   - Nombres de índices correctos

5. **Validar Configuración de Conexión**
   - Tamaño del pool de conexiones
   - Timeouts apropiados
   - Configuración óptima

---

## 📁 ¿QUÉ ARCHIVOS MONITOREA?

El Agente DB vigila estos archivos automáticamente:

### Patrones de Archivos
- `app/backend/models/**/*.py` - Todos los modelos SQLAlchemy
- `app/backend/database/**/*.py` - Configuración de conexión
- `sql/migrations/**/*.sql` - Migraciones SQL
- `scripts/database/**/*.py` - Scripts de base de datos

### Archivos Específicos Importantes
- `app/backend/models/current.py` - Modelo principal actual
- `app/backend/models/advanced.py` - Modelos avanzados
- `app/backend/database/connection.py` - Conexión principal
- Cualquier archivo `.sql` en `sql/migrations/`

---

## 🔔 ¿CUÁNDO SE ACTIVA EL AGENTE DB?

El agente se activa automáticamente cuando:

1. **Modificas un modelo** (`app/backend/models/*.py`)
   - Agregas una nueva tabla
   - Cambias una columna
   - Modificas relaciones

2. **Creas o modificas una migración** (`sql/migrations/*.sql`)
   - Nueva migración SQL
   - Cambios en migración existente

3. **Modificas la conexión** (`app/backend/database/connection.py`)
   - Cambios en configuración del pool
   - Cambios en timeouts

---

## 📊 NIVELES DE IMPORTANCIA

El Agente DB clasifica sus validaciones en 4 niveles:

### 🔴 CRITICAL (Crítico)
**Bloquea cambios si falla**

- ✅ Primary key obligatorio en cada tabla
- ✅ Foreign keys deben ser válidos
- ✅ Tipos de datos correctos
- ✅ Sintaxis SQL válida
- ✅ Compatibilidad MySQL

**Ejemplo**: Si creas una tabla sin primary key, el agente bloqueará el cambio.

---

### 🟠 HIGH (Alto)
**Muestra warning pero permite continuar**

- ⚠️ Índices faltantes en foreign keys
- ⚠️ Campos de timestamp faltantes (`created_at`, `updated_at`)
- ⚠️ Problemas de normalización
- ⚠️ Migraciones sin transacciones
- ⚠️ N+1 query problems

**Ejemplo**: Si falta un índice en un foreign key, el agente mostrará un warning y sugerirá agregarlo, pero no bloquea el desarrollo.

---

### 🟡 MEDIUM (Medio)
**Sugerencias que no bloquean**

- 💡 Naming conventions (nombres de tablas, columnas)
- 💡 Índices faltantes sugeridos
- 💡 Rollback en migraciones (opcional en dev)
- 💡 Optimizaciones de tipos de datos

**Ejemplo**: Si una tabla se llama `ChatAssignments` en lugar de `chat_assignments`, el agente sugerirá el cambio pero no bloquea.

---

### 🟢 LOW (Bajo)
**Solo información**

- 📝 Documentación faltante
- 📝 Sugerencias de soft delete
- 📝 Información general

**Ejemplo**: El agente sugiere agregar documentación a una clase, pero es completamente opcional.

---

## 📝 REGLAS DE NAMING CONVENTIONS

### Tablas ✅
- **Minúsculas** y **plural**: `users`, `conversations`, `messages`
- **Snake_case** para nombres compuestos: `chat_assignments`, `user_sessions`
- **Sin prefijos** innecesarios: ❌ `tbl_users`, ✅ `users`

**Ejemplos**:
- ✅ `users` (correcto)
- ✅ `chat_assignments` (correcto)
- ❌ `Users` (debe ser minúsculas)
- ❌ `ChatAssignments` (debe ser minúsculas y snake_case)
- ❌ `user` (debe ser plural)

---

### Columnas ✅
- **Minúsculas** y **snake_case**: `user_id`, `created_at`, `is_active`
- **Foreign keys**: Formato `{tabla}_id` (`user_id`, `conversation_id`)
- **Booleanos**: Prefijo `is_`, `has_`, `can_` (`is_active`, `has_permission`)
- **Timestamps**: Sufijo `_at` o `_date` (`created_at`, `updated_at`)

**Ejemplos**:
- ✅ `user_id` (foreign key correcto)
- ✅ `is_active` (booleano correcto)
- ✅ `created_at` (timestamp correcto)
- ❌ `userId` (debe ser snake_case)
- ❌ `active` (booleano debe tener prefijo `is_`)
- ❌ `createDate` (debe ser `created_at`)

---

### Índices ✅
- **Únicos**: `uq_{tabla}_{columna}` (`uq_users_email`, `uq_users_phone`)
- **Regulares**: `idx_{tabla}_{columna}` (`idx_messages_conversation_id`)
- **Foreign keys**: `fk_{tabla}_{columna}` (en constraints)

**Ejemplos**:
- ✅ `uq_users_email` (índice único correcto)
- ✅ `idx_messages_conversation_id` (índice regular correcto)
- ❌ `users_email_unique` (debe usar prefijo `uq_`)

---

## 🔧 FUNCIONES DEL AGENTE DB

### 1. `validate_model()`
**¿Qué hace?**: Valida que un modelo SQLAlchemy esté bien estructurado

**Qué valida**:
- ✅ Primary key presente
- ✅ Foreign keys válidos
- ✅ Tipos de datos correctos
- ✅ Índices en foreign keys
- ✅ Campos de timestamp
- ✅ Normalización 3NF

**Ejemplo de uso**:
Cuando modificas `app/models/current.py`, el agente ejecuta automáticamente esta función.

---

### 2. `check_migrations()`
**¿Qué hace?**: Valida que las migraciones SQL sean correctas

**Qué valida**:
- ✅ Sintaxis SQL válida
- ✅ Compatibilidad MySQL 8.0+
- ✅ Uso de transacciones
- ✅ Orden de operaciones

**Ejemplo de uso**:
Cuando creas `sql/migrations/add_message_type.sql`, el agente valida automáticamente.

---

### 3. `optimize_queries()`
**¿Qué hace?**: Detecta problemas de performance en queries

**Qué detecta**:
- ⚠️ N+1 query problems (queries en loops)
- ⚠️ `SELECT *` sin justificación
- 💡 Índices faltantes
- 💡 Queries sin `WHERE`

**Ejemplo de uso**:
El agente analiza el código buscando queries SQL y sugiere optimizaciones.

---

### 4. `validate_connection_pool()`
**¿Qué hace?**: Valida la configuración del pool de conexiones

**Qué valida**:
- ⚠️ Tamaño del pool (debe ser 5-50)
- ⚠️ Timeouts apropiados (>= 5 segundos)
- 💡 Pool recycle (<= 3600 segundos)

**Ejemplo de uso**:
Cuando modificas `app/database/connection.py`, el agente valida la configuración.

---

### 5. `validate_naming_conventions()`
**¿Qué hace?**: Valida que los nombres sigan las convenciones

**Qué valida**:
- 💡 Nombres de tablas (minúsculas, plural, snake_case)
- 💡 Nombres de columnas (minúsculas, snake_case)
- 💡 Nombres de índices (prefijos correctos)

**Ejemplo de uso**:
Cada vez que se modifica un modelo, el agente verifica los nombres.

---

## 📤 ¿QUÉ OUTPUT GENERA EL AGENTE DB?

El agente genera feedback en formato JSON que puedes ver en:

- **Redis**: `agent:feedback:db:{task_id}` (comunicación rápida)
- **Archivo**: `.agents/communications/db_feedback.json` (persistencia)

### Ejemplo de Feedback:

```json
{
  "agent": "db",
  "status": "completed",
  "file_analyzed": "app/models/current.py",
  "results": {
    "model_validation": {
      "status": "valid",
      "errors": [],
      "warnings": [
        {
          "type": "missing_index_on_foreign_key",
          "table": "messages",
          "column": "conversation_id",
          "message": "Foreign key 'conversation_id' should have an index",
          "suggestion": "Add index: CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)"
        }
      ]
    }
  },
  "summary": {
    "total_errors": 0,
    "total_warnings": 1,
    "can_proceed": true,
    "blocked": false
  }
}
```

---

## ✅ EJEMPLOS PRÁCTICOS

### Ejemplo 1: Crear Nueva Tabla

**❌ INCORRECTO**:
```python
class ChatAssignments(Base):  # Nombre incorrecto
    __tablename__ = 'ChatAssignments'  # Debe ser minúsculas y plural
    Active = mapped_column(Boolean)  # Debe ser 'is_active'
```

**El Agente DB detectará**:
- 🟡 Sugerencia: Tabla debe ser `chat_assignments`
- 🟡 Sugerencia: Columna debe ser `is_active`

**✅ CORRECTO**:
```python
class ChatAssignment(Base):
    __tablename__ = 'chat_assignments'  # Minúsculas y plural
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Prefijo 'is_'
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())  # Sufijo '_at'
```

---

### Ejemplo 2: Foreign Key sin Índice

**❌ INCORRECTO**:
```python
class Message(Base):
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id'), 
        index=False  # ❌ Falta índice
    )
```

**El Agente DB detectará**:
- 🟠 Warning: Foreign key debería tener índice
- 💡 Sugerencia: Agregar `index=True`

**✅ CORRECTO**:
```python
class Message(Base):
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id'), 
        index=True  # ✅ Índice agregado
    )
```

---

### Ejemplo 3: Migración SQL

**❌ INCORRECTO**:
```sql
-- Sin transacción
ALTER TABLE messages ADD COLUMN message_type VARCHAR(20);
```

**El Agente DB detectará**:
- 🟠 Warning: Debe usar transacciones

**✅ CORRECTO**:
```sql
BEGIN;
ALTER TABLE messages ADD COLUMN message_type VARCHAR(20) NULL;
COMMIT;
```

---

## 🚨 ¿QUÉ PASA SI EL AGENTE DETECTA ERRORES CRÍTICOS?

Si el agente detecta errores **CRITICAL**:

1. **Bloquea el cambio** (no permite continuar)
2. **Genera feedback** con el error específico
3. **Sugiere solución** automáticamente
4. **Notifica al Maestro** para coordinación

**Ejemplo de error crítico**:
```json
{
  "status": "invalid",
  "errors": [
    {
      "type": "missing_primary_key",
      "table": "messages",
      "severity": "critical",
      "message": "Table 'messages' must have a primary key named 'id'",
      "blocked": true
    }
  ],
  "can_proceed": false,
  "blocked": true
}
```

---

## 💡 CONSEJOS PARA DESARROLLADORES

1. **Sigue las naming conventions** desde el inicio
   - Ahorra tiempo en correcciones
   - Hace el código más legible

2. **Presta atención a los warnings HIGH**
   - Aunque no bloquean, mejoran performance
   - Evitan problemas futuros

3. **Revisa las sugerencias MEDIUM**
   - Son buenas prácticas
   - No son obligatorias pero mejoran calidad

4. **Usa los ejemplos del agente**
   - El agente siempre sugiere código correcto
   - Puedes copiar las sugerencias directamente

---

## 🔗 ARCHIVOS RELACIONADOS

- **Configuración JSON**: `agentes/specs/agents/db_agent.json`
- **Especificación Técnica**: `agentes/specs/agents/AGENTE_DB_ESPECIFICACION_MEJORADA.md`
- **Ejemplo de Config**: `agentes/config/examples/db_agent_config.json`

---

## 📞 COMUNICACIÓN CON OTROS AGENTES

El Agente DB se comunica con:

- **Maestro**: Envía feedback después de validaciones
- **Backend**: Notifica si hay cambios en modelos que afectan APIs
- **Tests**: Informa cambios que requieren nuevos tests

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿El agente bloquea mi desarrollo si hay warnings?**  
R: No, solo bloquea si hay errores CRITICAL. Los warnings y sugerencias no bloquean.

**P: ¿Puedo desactivar alguna validación?**  
R: Sí, puedes configurarlo en `db_agent.json` ajustando `enabled: false` en la función específica.

**P: ¿Cómo veo el feedback del agente?**  
R: Se guarda en `.agents/communications/db_feedback.json` y también en Redis para acceso rápido.

**P: ¿El agente modifica mi código automáticamente?**  
R: No, solo valida y sugiere. Los cambios los haces tú basándote en las sugerencias.

---

## 📋 RESUMEN DE CARACTERÍSTICAS DEL AGENTE DB

### ✅ Funcionalidades Principales

1. **Validación de Modelos**
   - ✅ Validación completa de modelos SQLAlchemy
   - ✅ Verificación de primary keys, foreign keys, tipos de datos
   - ✅ Validación de normalización 3NF
   - ✅ Detección de índices faltantes

2. **Validación de Migraciones**
   - ✅ Validación de sintaxis SQL
   - ✅ Compatibilidad MySQL 8.0+
   - ✅ Verificación de transacciones

3. **Optimización de Queries**
   - ✅ Detección de N+1 queries
   - ✅ Sugerencias de índices faltantes
   - ✅ Análisis de performance

4. **Naming Conventions**
   - ✅ Validación de nombres de tablas (minúsculas, plural, snake_case)
   - ✅ Validación de nombres de columnas (snake_case, prefijos correctos)
   - ✅ Validación de nombres de índices (prefijos uq_/idx_/fk_)

5. **Análisis Inteligente**
   - ✅ Conocimiento completo del modelo actual
   - ✅ Comparación con mejores prácticas
   - ✅ Sugerencias basadas en patrones comunes
   - ✅ Ejemplos de la industria (Intercom, Zendesk, Crisp)

6. **Pruebas Automatizadas**
   - ✅ Pruebas diarias (02:00 AM)
   - ✅ Pruebas semanales (Domingo 03:00 AM)
   - ✅ Tests de conexión, integridad, migraciones

7. **Análisis de Performance**
   - ✅ Análisis horario de queries lentas
   - ✅ Análisis diario de performance por volumen
   - ✅ Detección automática de cuellos de botella
   - ✅ Investigación de problemas (5 pasos)
   - ✅ Sugerencias de optimización automáticas

### 📊 Niveles de Validación

- 🔴 **CRITICAL**: Bloquea cambios si falla
- 🟠 **HIGH**: Muestra warnings pero permite continuar
- 🟡 **MEDIUM**: Sugerencias que no bloquean
- 🟢 **LOW**: Solo información

### 🔄 Automatización

- ✅ Activación automática al modificar archivos
- ✅ Actualización automática del conocimiento
- ✅ Análisis automático según horarios programados
- ✅ Generación automática de sugerencias

### 📁 Archivos

- `db_agent.json` - Configuración completa
- `db_agent.md` - Guía para desarrolladores
- `db_agent_knowledge.json` - Conocimiento del modelo (35KB)
- `db_agent_knowledge.md` - Guía de conocimiento
- `db_agent_test_performance.json` - Configuración de pruebas (25KB)
- `db_agent_test_performance.md` - Guía de pruebas y performance

---

**Última actualización**: 2025-01-XX  
**Versión**: 2.0

