# 🗄️ AGENTE DB (DATABASE) - ESPECIFICACIÓN MEJORADA

**Proyecto**: ChatBot para Microempresarios  
**Fecha**: 2025-01-XX  
**Entorno**: Desarrollo (DEV) - Reglas adaptadas para desarrollo  
**Versión**: 2.0

---

## 🎯 RESPONSABILIDAD PRINCIPAL

Validar y optimizar modelos de datos, migraciones SQL, estructura de base de datos y naming conventions siguiendo mejores prácticas de la industria.

---

## 📊 NIVELES DE IMPORTANCIA

**Considerando entorno de DESARROLLO:**

- 🔴 **CRITICAL**: Debe cumplirse siempre - Bloquea cambios si falla
- 🟠 **HIGH**: Muy importante - Warning si falla, pero permite continuar
- 🟡 **MEDIUM**: Importante - Sugerencia, no bloquea
- 🟢 **LOW**: Buena práctica - Solo información, no afecta desarrollo

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos
- `app/models/**/*.py` - Modelos SQLAlchemy
- `app/database/**/*.py` - Configuración de conexión
- `sql/migrations/**/*.sql` - Migraciones SQL
- `scripts/database/**/*.py` - Scripts de base de datos

### Archivos Específicos
- `app/models/current.py` - Modelo actual principal
- `app/models/advanced.py` - Modelos avanzados
- `app/database/connection.py` - Conexión principal
- `sql/migrations/*.sql` - Todas las migraciones

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `validate_model(normalization=True, indexes=True, relations=True, naming=True)`

**Descripción**: Valida modelo de datos SQLAlchemy completo

**Parámetros:**
- `normalization` (bool): Verificar normalización 3NF
- `indexes` (bool): Verificar índices necesarios
- `relations` (bool): Validar relaciones y foreign keys
- `naming` (bool): Validar naming conventions

**Reglas de Validación:**

#### 🔴 CRITICAL (Bloquea si falla)

1. **Primary Key Obligatorio**
   - ✅ Cada tabla DEBE tener una primary key
   - ✅ Primary key debe ser `id` (INTEGER, autoincrement)
   - ⚠️ Error si falta o tiene nombre diferente

2. **Foreign Keys Válidos**
   - ✅ Foreign keys deben referenciar tablas existentes
   - ✅ Foreign keys deben tener mismo tipo que primary key referenciada
   - ⚠️ Error si referencia tabla inexistente o tipo incorrecto

3. **Tipos de Datos Correctos**
   - ✅ Campos de texto deben tener límites (`VARCHAR(n)` o `TEXT`)
   - ✅ Campos numéricos deben tener tipos apropiados
   - ⚠️ Error si usa `String` sin límite o tipo incorrecto

4. **Campos Obligatorios**
   - ✅ Campos marcados como `nullable=False` deben tener valor por defecto o ser requeridos
   - ⚠️ Error si campo obligatorio sin default

#### 🟠 HIGH (Warning, permite continuar)

5. **Índices en Foreign Keys**
   - ✅ Foreign keys DEBEN tener índices para performance
   - ⚠️ Warning si falta índice en foreign key
   - 💡 Sugerencia: Agregar índice automáticamente

6. **Campos de Timestamp**
   - ✅ Tablas principales deben tener `created_at` y `updated_at`
   - ⚠️ Warning si faltan campos de timestamp
   - 💡 Sugerencia: Agregar campos automáticos

7. **Normalización 3NF**
   - ✅ No debe haber dependencias transitivas
   - ⚠️ Warning si detecta violación de 3NF
   - 💡 Sugerencia: Refactorizar tabla

8. **Campos Nullable Justificados**
   - ✅ Campos nullable deben tener justificación
   - ⚠️ Warning si hay muchos campos nullable sin razón
   - 💡 Sugerencia: Revisar si realmente necesitan ser nullable

#### 🟡 MEDIUM (Sugerencia, no bloquea)

9. **Naming Conventions - Tablas**
   - ✅ Tablas en **minúsculas** y **plural** (`users`, `conversations`)
   - ✅ Usar **snake_case** para nombres compuestos (`chat_assignments`)
   - ✅ Evitar prefijos innecesarios (`tbl_`, `tab_`)
   - 💡 Sugerencia si no cumple convención

10. **Naming Conventions - Columnas**
    - ✅ Columnas en **minúsculas** y **snake_case** (`user_id`, `created_at`)
    - ✅ Foreign keys deben usar formato: `{tabla_referenciada}_id` (`user_id`, `conversation_id`)
    - ✅ Campos booleanos deben usar prefijo `is_` o `has_` (`is_active`, `has_permission`)
    - ✅ Campos de fecha deben usar sufijo `_at` o `_date` (`created_at`, `updated_at`)
    - 💡 Sugerencia si no cumple convención

11. **Naming Conventions - Índices**
    - ✅ Índices únicos: `uq_{tabla}_{columna}` (`uq_users_email`)
    - ✅ Índices regulares: `idx_{tabla}_{columna}` (`idx_messages_conversation_id`)
    - ✅ Foreign keys: `fk_{tabla}_{columna}` (`fk_messages_user_id`)
    - 💡 Sugerencia si no cumple convención

12. **Optimización de Tipos**
    - ✅ Usar `TEXT` solo para campos grandes (>255 chars)
    - ✅ Usar `VARCHAR(n)` con límite apropiado
    - ✅ Usar `Boolean` en lugar de `INT` para flags
    - 💡 Sugerencia de optimización

13. **Campos de Auditoría**
    - ✅ Tablas importantes deben tener campos de auditoría (`created_at`, `updated_at`)
    - 💡 Sugerencia agregar campos de auditoría

#### 🟢 LOW (Solo información)

14. **Documentación**
    - ✅ Clases deben tener docstrings
    - ✅ Campos complejos deben tener comentarios
    - 💡 Información sobre documentación faltante

15. **Campos de Soft Delete**
    - ✅ Considerar `deleted_at` para soft delete si es necesario
    - 💡 Información sobre soft delete

**Output:**
```json
{
  "status": "valid|invalid|warning",
  "errors": [
    {
      "type": "missing_primary_key",
      "table": "messages",
      "severity": "critical",
      "message": "Table 'messages' must have a primary key named 'id'"
    }
  ],
  "warnings": [
    {
      "type": "missing_index_on_foreign_key",
      "table": "messages",
      "column": "conversation_id",
      "severity": "high",
      "message": "Foreign key 'conversation_id' should have an index",
      "suggestion": "Add index: CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)"
    }
  ],
  "suggestions": [
    {
      "type": "naming_convention",
      "table": "ChatAssignments",
      "current": "ChatAssignments",
      "recommended": "chat_assignments",
      "severity": "medium",
      "message": "Table name should be lowercase and plural"
    }
  ],
  "info": [
    {
      "type": "missing_documentation",
      "table": "User",
      "severity": "low",
      "message": "Consider adding docstring to User class"
    }
  ]
}
```

---

### 2. `check_migrations(syntax=True, compatibility=True, rollback=False, naming=True)`

**Descripción**: Valida migraciones SQL

**Parámetros:**
- `syntax` (bool): Verificar sintaxis SQL
- `compatibility` (bool): Verificar compatibilidad con MySQL 8.0+
- `rollback` (bool): Verificar que migración sea reversible (MEDIUM en dev)
- `naming` (bool): Validar naming conventions

**Reglas de Validación:**

#### 🔴 CRITICAL (Bloquea si falla)

1. **Sintaxis SQL Válida**
   - ✅ Sintaxis SQL debe ser válida
   - ⚠️ Error si hay errores de sintaxis

2. **Compatibilidad MySQL**
   - ✅ Compatible con MySQL 8.0+
   - ⚠️ Error si usa características no soportadas

#### 🟠 HIGH (Warning, permite continuar)

3. **Uso de Transacciones**
   - ✅ Migraciones deben usar transacciones (`BEGIN`, `COMMIT`)
   - ⚠️ Warning si no usa transacciones
   - 💡 Sugerencia: Envolver en transacción

4. **Destrucción de Datos**
   - ✅ No debe hacer `DROP TABLE` sin backup
   - ✅ No debe hacer `DELETE` sin `WHERE` sin justificación
   - ⚠️ Warning si detecta operaciones destructivas
   - 💡 Sugerencia: Crear backup antes

5. **Orden de Operaciones**
   - ✅ Crear tablas antes de agregar foreign keys
   - ✅ Crear índices después de insertar datos
   - ⚠️ Warning si orden incorrecto

#### 🟡 MEDIUM (Sugerencia, no bloquea)

6. **Rollback (Opcional en DEV)**
   - ✅ Migraciones deberían tener rollback definido
   - 💡 Sugerencia agregar rollback (no crítico en dev)

7. **Naming Conventions - Archivos**
   - ✅ Archivos deben usar formato: `{timestamp}_{description}.sql`
   - ✅ Ejemplo: `20250115_add_message_type.sql`
   - ✅ Descripción en snake_case
   - 💡 Sugerencia si no cumple convención

8. **Comentarios en Migraciones**
   - ✅ Migraciones deben tener comentarios explicativos
   - 💡 Sugerencia agregar comentarios

#### 🟢 LOW (Solo información)

9. **Versionado**
   - ✅ Considerar numeración de versiones
   - 💡 Información sobre versionado

**Output:**
```json
{
  "status": "valid|invalid|warning",
  "migration_file": "sql/migrations/add_message_type.sql",
  "errors": [
    {
      "type": "syntax_error",
      "line": 5,
      "severity": "critical",
      "message": "SQL syntax error: Unexpected token"
    }
  ],
  "warnings": [
    {
      "type": "missing_transaction",
      "severity": "high",
      "message": "Migration should use transactions",
      "suggestion": "Wrap migration in BEGIN...COMMIT"
    }
  ],
  "suggestions": [
    {
      "type": "naming_convention",
      "current": "add_column.sql",
      "recommended": "20250115_add_message_type.sql",
      "severity": "medium",
      "message": "Migration file should include timestamp"
    }
  ]
}
```

---

### 3. `optimize_queries(analyze=True, suggest_indexes=True)`

**Descripción**: Analiza y optimiza queries SQL

**Parámetros:**
- `analyze` (bool): Analizar queries existentes en código
- `suggest_indexes` (bool): Sugerir índices faltantes

**Reglas de Validación:**

#### 🟠 HIGH (Warning, permite continuar)

1. **N+1 Query Problem**
   - ✅ Detectar queries en loops
   - ⚠️ Warning si detecta N+1 problem
   - 💡 Sugerencia: Usar eager loading o joins

2. **SELECT * en Producción**
   - ✅ Evitar `SELECT *` (aunque en dev es aceptable)
   - ⚠️ Warning si usa `SELECT *`
   - 💡 Sugerencia: Seleccionar columnas específicas

#### 🟡 MEDIUM (Sugerencia, no bloquea)

3. **Índices Faltantes**
   - ✅ Columnas usadas en `WHERE` deben tener índices
   - ✅ Columnas usadas en `JOIN` deben tener índices
   - 💡 Sugerencia agregar índices

4. **LIKE con Wildcard Inicial**
   - ✅ Evitar `LIKE '%pattern%'` (requiere fulltext index)
   - 💡 Sugerencia: Usar `LIKE 'pattern%'` o fulltext index

5. **Queries sin WHERE**
   - ✅ Queries sin `WHERE` deben justificarse
   - 💡 Sugerencia revisar si realmente necesita todos los registros

#### 🟢 LOW (Solo información)

6. **Optimización de Joins**
   - ✅ Considerar orden de joins para performance
   - 💡 Información sobre optimización

**Output:**
```json
{
  "status": "optimized|needs_optimization",
  "optimizations": [
    {
      "type": "missing_index",
      "query": "SELECT * FROM messages WHERE conversation_id = ?",
      "table": "messages",
      "column": "conversation_id",
      "severity": "medium",
      "suggestion": "Add index: CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)"
    },
    {
      "type": "n_plus_one",
      "file": "app/main.py",
      "line": 165,
      "severity": "high",
      "description": "Query executed in loop",
      "suggestion": "Use eager loading: session.query(Message).options(joinedload(Message.conversation)).all()"
    }
  ]
}
```

---

### 4. `validate_connection_pool(pool_size=True, timeout=True)`

**Descripción**: Valida configuración de conexión a BD

**Parámetros:**
- `pool_size` (bool): Verificar tamaño del pool
- `timeout` (bool): Verificar timeouts

**Reglas de Validación:**

#### 🟠 HIGH (Warning, permite continuar)

1. **Tamaño del Pool**
   - ✅ Pool size debe ser entre 5-50
   - ✅ Max overflow debe ser <= pool_size * 2
   - ⚠️ Warning si está fuera de rango recomendado

2. **Timeouts**
   - ✅ Timeout debe ser >= 5 segundos
   - ⚠️ Warning si timeout muy bajo

#### 🟡 MEDIUM (Sugerencia, no bloquea)

3. **Pool Recycle**
   - ✅ Pool recycle debe ser <= 3600 segundos (1 hora)
   - 💡 Sugerencia si está fuera de rango

4. **Pool Pre Ping**
   - ✅ Debe estar habilitado para detectar conexiones cerradas
   - 💡 Sugerencia habilitar pool_pre_ping

**Output:**
```json
{
  "status": "valid|needs_adjustment",
  "current_config": {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": true,
    "timeout": 30
  },
  "warnings": [],
  "recommendations": []
}
```

---

### 5. `validate_naming_conventions(tables=True, columns=True, indexes=True)`

**Descripción**: Valida naming conventions según mejores prácticas

**Parámetros:**
- `tables` (bool): Validar nombres de tablas
- `columns` (bool): Validar nombres de columnas
- `indexes` (bool): Validar nombres de índices

**Reglas de Naming:**

#### Tablas (MEDIUM - Sugerencia)

- ✅ **Minúsculas** y **plural** (`users`, `conversations`, `messages`)
- ✅ **Snake_case** para nombres compuestos (`chat_assignments`, `user_sessions`)
- ✅ Sin prefijos innecesarios (`tbl_`, `tab_`)
- ✅ Nombres descriptivos y claros

#### Columnas (MEDIUM - Sugerencia)

- ✅ **Minúsculas** y **snake_case** (`user_id`, `created_at`, `is_active`)
- ✅ Foreign keys: `{tabla_referenciada}_id` (`user_id`, `conversation_id`)
- ✅ Booleanos: Prefijo `is_`, `has_`, `can_` (`is_active`, `has_permission`)
- ✅ Timestamps: Sufijo `_at` o `_date` (`created_at`, `updated_at`, `deleted_at`)
- ✅ Nombres descriptivos (evitar abreviaciones innecesarias)

#### Índices (MEDIUM - Sugerencia)

- ✅ Únicos: `uq_{tabla}_{columna}` (`uq_users_email`, `uq_users_phone`)
- ✅ Regulares: `idx_{tabla}_{columna}` (`idx_messages_conversation_id`)
- ✅ Compuestos: `idx_{tabla}_{col1}_{col2}` (`idx_messages_user_conv`)
- ✅ Foreign keys: `fk_{tabla}_{columna}` (en constraints)

**Output:**
```json
{
  "status": "compliant|needs_improvement",
  "naming_issues": [
    {
      "type": "table_naming",
      "current": "ChatAssignments",
      "recommended": "chat_assignments",
      "severity": "medium",
      "rule": "Tables should be lowercase and plural"
    },
    {
      "type": "column_naming",
      "table": "users",
      "current": "active",
      "recommended": "is_active",
      "severity": "medium",
      "rule": "Boolean columns should use 'is_' prefix"
    },
    {
      "type": "index_naming",
      "current": "users_email_unique",
      "recommended": "uq_users_email",
      "severity": "medium",
      "rule": "Unique indexes should use 'uq_' prefix"
    }
  ]
}
```

---

## ⚙️ PARÁMETROS DE CONFIGURACIÓN

```json
{
  "agent": "db",
  "enabled": true,
  "priority": "high",
  "environment": "development",
  "config": {
    "validate_on_change": true,
    "validate_on_save": false,
    "auto_suggest_indexes": true,
    "strict_mode": false,
    "allowed_orms": ["sqlalchemy"],
    "database_type": "mysql",
    "database_version": "8.0+",
    "min_pool_size": 5,
    "max_pool_size": 50,
    "naming_conventions": {
      "enabled": true,
      "strictness": "medium",
      "table_plural": true,
      "table_lowercase": true,
      "column_snake_case": true,
      "boolean_prefix": "is_",
      "timestamp_suffix": "_at"
    },
    "validation_levels": {
      "critical": {
        "block_on_failure": true,
        "required": true
      },
      "high": {
        "block_on_failure": false,
        "show_warning": true,
        "suggest_fix": true
      },
      "medium": {
        "block_on_failure": false,
        "show_suggestion": true,
        "allow_continue": true
      },
      "low": {
        "block_on_failure": false,
        "show_info": true,
        "optional": true
      }
    },
    "migration_settings": {
      "require_rollback": false,
      "require_transactions": true,
      "strict_naming": false,
      "allow_destructive": true,
      "warn_on_destructive": true
    }
  }
}
```

---

## 📤 FORMATO DE FEEDBACK COMPLETO

```json
{
  "agent": "db",
  "trigger_id": "db-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed|error|warning",
  "file_analyzed": "app/models/current.py",
  "environment": "development",
  "results": {
    "model_validation": {
      "status": "valid|invalid|warning",
      "errors": [],
      "warnings": [],
      "suggestions": [],
      "info": []
    },
    "migration_validation": {
      "status": "valid|invalid|warning",
      "errors": [],
      "warnings": [],
      "suggestions": []
    },
    "naming_validation": {
      "status": "compliant|needs_improvement",
      "issues": []
    },
    "optimizations": [],
    "connection_pool": {
      "status": "valid|needs_adjustment",
      "config": {},
      "recommendations": []
    }
  },
  "summary": {
    "total_errors": 0,
    "total_warnings": 2,
    "total_suggestions": 5,
    "total_info": 1,
    "can_proceed": true,
    "blocked": false
  }
}
```

---

## 🎯 RESUMEN DE REGLAS POR IMPORTANCIA

### 🔴 CRITICAL (Bloquea si falla)
- Primary key obligatorio
- Foreign keys válidos
- Tipos de datos correctos
- Campos obligatorios sin default
- Sintaxis SQL válida
- Compatibilidad MySQL

### 🟠 HIGH (Warning, permite continuar)
- Índices en foreign keys
- Campos de timestamp
- Normalización 3NF
- Uso de transacciones en migraciones
- Destrucción de datos sin backup
- N+1 query problems
- SELECT * en queries
- Tamaño del pool de conexiones

### 🟡 MEDIUM (Sugerencia, no bloquea)
- Naming conventions (tablas, columnas, índices)
- Optimización de tipos
- Campos de auditoría
- Rollback en migraciones (opcional en dev)
- Índices faltantes
- Optimización de queries

### 🟢 LOW (Solo información)
- Documentación
- Soft delete
- Versionado de migraciones
- Optimización de joins

---

## 📋 EJEMPLOS DE VALIDACIÓN

### Ejemplo 1: Primary Key Faltante (CRITICAL)

```python
# ❌ INCORRECTO
class Message(Base):
    __tablename__ = 'messages'
    content: Mapped[str] = mapped_column(Text)
    # ERROR: Falta primary key

# ✅ CORRECTO
class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text)
```

### Ejemplo 2: Naming Convention (MEDIUM)

```python
# ⚠️ SUGERENCIA DE MEJORA
class ChatAssignments(Base):  # Debería ser 'chat_assignments'
    __tablename__ = 'ChatAssignments'  # Debería ser minúsculas y plural
    Active: Mapped[bool] = mapped_column(Boolean)  # Debería ser 'is_active'
    
# ✅ CORRECTO
class ChatAssignment(Base):
    __tablename__ = 'chat_assignments'  # Minúsculas y plural
    is_active: Mapped[bool] = mapped_column(Boolean)  # Prefijo 'is_'
```

### Ejemplo 3: Índice Faltante (HIGH)

```python
# ⚠️ WARNING
class Message(Base):
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id'), 
        index=False  # Warning: Foreign key sin índice
    )

# ✅ CORRECTO
class Message(Base):
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id'), 
        index=True  # Índice agregado
    )
```

---

**Autor**: Composer AI  
**Fecha**: 2025-01-XX  
**Versión**: 2.0 - Mejorada con Naming Conventions y Niveles de Importancia

