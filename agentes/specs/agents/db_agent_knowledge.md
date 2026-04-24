# 🧠 AGENTE DB - BASE DE CONOCIMIENTO Y SUGERENCIAS INTELIGENTES

**Versión**: 2.0  
**Última actualización**: 2025-01-XX

---

## 🎯 ¿QUÉ ES EL CONOCIMIENTO DEL AGENTE DB?

El Agente DB mantiene un **conocimiento completo** del modelo de datos actual en un archivo JSON (`db_agent_knowledge.json`). Este conocimiento incluye:

- ✅ Todas las tablas y sus columnas
- ✅ Relaciones entre tablas
- ✅ Índices existentes
- ✅ Patrones detectados
- ✅ Mejores prácticas conocidas

---

## 🧠 ¿CÓMO FUNCIONA EL CONOCIMIENTO?

### 1. Conocimiento del Modelo Actual

El agente mantiene un "mapa mental" completo del modelo en `db_agent_knowledge.json`:

**Información almacenada**:
- Estructura completa de cada tabla
- Tipos de datos de cada columna
- Relaciones y foreign keys
- Índices existentes
- Patrones detectados
- Estadísticas del modelo

**Ejemplo de conocimiento**:
```json
{
  "current_model": {
    "tables": [
      {
        "name": "users",
        "columns": [...],
        "relationships": [...],
        "indexes": [...]
      }
    ]
  }
}
```

---

### 2. Análisis y Comparación

Cuando modificas el modelo, el agente:

1. **Lee el modelo actualizado**
2. **Compara con su conocimiento** anterior
3. **Detecta cambios** (nuevas tablas, columnas, relaciones)
4. **Busca patrones comunes** en su conocimiento
5. **Compara con mejores prácticas** conocidas
6. **Genera sugerencias** inteligentes

---

### 3. Sugerencias Inteligentes

El agente puede sugerir mejoras basándose en:

#### 🎯 Patrones Comunes Detectados

**Ejemplo**: Si agregas una tabla `conversations`, el agente detecta:
- ✅ Es un patrón común de gestión de conversaciones
- 💡 Sugiere agregar `last_message_at` (patrón común)
- 💡 Sugiere usar `ENUM` para `status` en lugar de `VARCHAR`
- 💡 Sugiere índices compuestos comunes

#### 🏢 Ejemplos de la Industria

El agente conoce patrones de:
- **Intercom**: Separación users vs contacts
- **Zendesk**: Ticket-like conversation management
- **Crisp**: Rich media support
- **Freshchat**: Tags y categorías

**Ejemplo**: Si modificas `messages`, el agente puede sugerir:
- 💡 Agregar `message_type` (patrón de Crisp)
- 💡 Agregar `media_url` para archivos adjuntos
- 💡 Agregar campo `metadata` JSON

---

## 🔍 FUNCIÓN: `analyze_and_suggest()`

### ¿Qué hace?

Analiza cambios en el modelo y genera sugerencias inteligentes basadas en:
- ✅ Conocimiento del modelo actual
- ✅ Patrones comunes detectados
- ✅ Mejores prácticas conocidas
- ✅ Ejemplos de la industria

### ¿Cuándo se activa?

Se activa automáticamente cuando:
- ✅ Agregas una nueva tabla
- ✅ Modificas una tabla existente
- ✅ Agregas una nueva columna
- ✅ Agregas una nueva relación
- ✅ Cambias tipos de datos

### Output de ejemplo:

```json
{
  "analysis": {
    "changes_detected": [
      {
        "type": "table_modified",
        "table": "messages",
        "changes": ["column_added: message_type"]
      }
    ],
    "patterns_detected": [
      {
        "pattern": "message_storage",
        "confidence": "high",
        "matches": 0.85
      }
    ],
    "suggestions": [
      {
        "type": "missing_field",
        "table": "messages",
        "field": "last_message_at",
        "reason": "Common pattern for conversation sorting",
        "priority": "high",
        "source": "industry_pattern",
        "example": "Used in Intercom, Zendesk, Crisp"
      },
      {
        "type": "type_optimization",
        "table": "messages",
        "field": "role",
        "current": "VARCHAR(10)",
        "recommended": "ENUM('user', 'assistant', 'system')",
        "reason": "Better performance and data integrity",
        "priority": "medium"
      },
      {
        "type": "missing_index",
        "table": "messages",
        "recommended": "idx_messages_conversation_created",
        "columns": ["conversation_id", "created_at"],
        "reason": "Common composite index for message queries",
        "priority": "high"
      }
    ],
    "improvements_based_on": [
      "common_patterns",
      "industry_examples",
      "best_practices"
    ]
  }
}
```

---

## 📊 PATRONES QUE EL AGENTE CONOCE

### 1. Patrón de Gestión de Usuarios

**Campos típicos**:
- `id`, `email`, `username`, `password_hash`
- `is_active`, `created_at`, `updated_at`

**Sugerencias comunes**:
- 💡 Agregar `email_verified` (verificación de email)
- 💡 Agregar `last_login_at` (tracking de actividad)
- 💡 Agregar `failed_login_attempts` (seguridad)

---

### 2. Patrón de Conversaciones

**Campos típicos**:
- `id`, `user_id`, `status`, `created_at`, `updated_at`
- `last_message_at` (común pero puede faltar)

**Sugerencias comunes**:
- 💡 Usar `ENUM` para `status` en lugar de `VARCHAR`
- 💡 Agregar `last_message_at` para ordenar conversaciones
- 💡 Agregar índices compuestos (`user_id`, `status`)

---

### 3. Patrón de Mensajes

**Campos típicos**:
- `id`, `conversation_id`, `user_id`, `content`, `role`
- `created_at`

**Sugerencias comunes**:
- 💡 Agregar `message_type` (text, image, file, audio, video)
- 💡 Agregar `metadata` JSON para información adicional
- 💡 Agregar índices compuestos (`conversation_id`, `created_at`)

---

### 4. Patrón de Auditoría

**Campos típicos**:
- `id`, `user_id`, `action`, `resource_type`, `resource_id`
- `created_at`, `ip_address`

**Sugerencias comunes**:
- 💡 Agregar índice en `created_at` para búsquedas temporales
- 💡 Agregar campo `session_id` para tracking

---

## 🔄 FLUJO DE ANÁLISIS AUTOMÁTICO

```
1. Modificas app/models/current.py
   ↓
2. File Watcher detecta cambio
   ↓
3. Agente DB lee el modelo actualizado
   ↓
4. Compara con conocimiento previo (db_agent_knowledge.json)
   ↓
5. Detecta cambios específicos
   ↓
6. Analiza patrones en el conocimiento
   ↓
7. Compara con mejores prácticas conocidas
   ↓
8. Genera sugerencias inteligentes
   ↓
9. Actualiza conocimiento base
   ↓
10. Envía feedback con sugerencias
```

---

## 💡 EJEMPLOS DE SUGERENCIAS INTELIGENTES

### Ejemplo 1: Agregar Campo a Tabla

**Cambio realizado**:
```python
class Message(Base):
    # Agregas un nuevo campo
    message_type: Mapped[str] = mapped_column(String(20), nullable=True)
```

**El agente detecta**:
- ✅ Nuevo campo `message_type` agregado
- ✅ Es parte del patrón "message_storage"

**Sugerencias generadas**:
```json
{
  "suggestions": [
    {
      "type": "type_optimization",
      "field": "message_type",
      "current": "VARCHAR(20)",
      "recommended": "ENUM('text', 'image', 'file', 'audio', 'video')",
      "reason": "Better performance and data integrity for fixed values",
      "priority": "medium",
      "source": "best_practice"
    },
    {
      "type": "missing_field",
      "field": "media_url",
      "reason": "Common pattern when message_type is not 'text'",
      "priority": "medium",
      "source": "industry_pattern_crisp"
    },
    {
      "type": "missing_field",
      "field": "metadata",
      "type": "JSON",
      "reason": "Common pattern for storing message metadata",
      "priority": "low",
      "source": "industry_pattern"
    }
  ]
}
```

---

### Ejemplo 2: Nueva Tabla

**Cambio realizado**:
```python
class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
```

**El agente detecta**:
- ✅ Nueva tabla `notifications`
- ✅ Patrón común de notificaciones

**Sugerencias generadas**:
```json
{
  "suggestions": [
    {
      "type": "missing_field",
      "field": "is_read",
      "type": "BOOLEAN",
      "reason": "Standard field for notification tracking",
      "priority": "high",
      "source": "common_pattern"
    },
    {
      "type": "missing_field",
      "field": "read_at",
      "type": "DATETIME",
      "reason": "Common for tracking when notification was read",
      "priority": "medium",
      "source": "common_pattern"
    },
    {
      "type": "missing_field",
      "field": "notification_type",
      "type": "ENUM",
      "reason": "Common pattern for categorizing notifications",
      "priority": "medium",
      "source": "best_practice"
    },
    {
      "type": "missing_index",
      "recommended": "idx_notifications_user_read",
      "columns": ["user_id", "is_read"],
      "reason": "Common query pattern: get unread notifications",
      "priority": "high",
      "source": "query_pattern"
    }
  ]
}
```

---

## 🎯 NIVELES DE SUGERENCIAS

### 🔴 CRITICAL (Crítico)
- Campos obligatorios faltantes
- Índices críticos faltantes
- Relaciones incorrectas

### 🟠 HIGH (Alto)
- Campos comunes que mejoran funcionalidad
- Índices importantes para performance
- Optimizaciones de tipos

### 🟡 MEDIUM (Medio)
- Campos opcionales útiles
- Optimizaciones menores
- Mejoras de naming

### 🟢 LOW (Bajo)
- Campos opcionales para casos avanzados
- Optimizaciones futuras
- Mejoras cosméticas

---

## 🔄 ACTUALIZACIÓN DEL CONOCIMIENTO

El agente actualiza automáticamente su conocimiento cuando:

1. **Detecta cambios en el modelo**
   - Nueva tabla agregada
   - Nueva columna agregada
   - Relación modificada

2. **Aplica migraciones**
   - Después de aplicar una migración SQL
   - Verifica que el conocimiento coincida con la BD real

3. **Validación periódica**
   - Compara conocimiento con modelo real
   - Detecta inconsistencias

---

## 📁 ARCHIVOS RELACIONADOS

- **Conocimiento Base**: `db_agent_knowledge.json` - Conocimiento completo del modelo
- **Configuración**: `db_agent.json` - Configuración del agente
- **Guía**: `db_agent.md` - Esta guía

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿El agente busca en internet automáticamente?**  
R: Por defecto NO, pero puedes habilitarlo en la configuración. El agente usa su conocimiento interno primero.

**P: ¿Cómo sé qué sugerencias son importantes?**  
R: Cada sugerencia tiene un `priority` (critical, high, medium, low). Las HIGH y CRITICAL son las más importantes.

**P: ¿El agente modifica mi código automáticamente?**  
R: No, solo sugiere. Tú decides qué cambios aplicar.

**P: ¿Cómo actualizo el conocimiento del agente?**  
R: Se actualiza automáticamente cuando detecta cambios. También puedes forzar una actualización.

---

**Última actualización**: 2025-01-XX  
**Versión**: 2.0

