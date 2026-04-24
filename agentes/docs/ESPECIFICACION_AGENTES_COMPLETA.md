# 🤖 ESPECIFICACIÓN COMPLETA DE AGENTES

**Proyecto**: ChatBot para Microempresarios  
**Fecha**: 2025-01-XX  
**Objetivo**: Definir funciones, reglas y parámetros de cada agente

---

## 📋 AGENTES DEFINIDOS

1. [Agente DB (Database)](#1-agente-db-database)
2. [Agente Backend](#2-agente-backend)
3. [Agente Frontend/UX](#3-agente-frontendux)
4. [Agente Performance & Stability](#4-agente-performance--stability)
5. [Agente OpenAI](#5-agente-openai)
6. [Agente WhatsApp](#6-agente-whatsapp)
7. [Agente Code Quality](#7-agente-code-quality)
8. [Agente Tests](#8-agente-tests)
9. [Agente Maestro (Coordinator)](#9-agente-maestro-coordinator)

---

## 1. AGENTE DB (Database)

### 🎯 Responsabilidad Principal
Validar y optimizar modelos de datos, migraciones SQL y estructura de base de datos.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/models/**/*.py`
- `app/database/**/*.py`
- `sql/migrations/**/*.sql`
- `scripts/database/**/*.py`

**Archivos Específicos:**
- `app/models/current.py`
- `app/models/advanced.py`
- `app/database/connection.py`
- `sql/migrations/*.sql`

### 🔧 Funciones Principales

#### 1.1 `validate_model(normalization=True, indexes=True, relations=True)`
**Descripción**: Valida modelo de datos SQLAlchemy

**Parámetros:**
- `normalization` (bool): Verificar normalización 3NF
- `indexes` (bool): Verificar índices necesarios
- `relations` (bool): Validar relaciones y foreign keys

**Reglas de Validación:**
- ✅ Cada tabla debe tener primary key
- ✅ Foreign keys deben tener índices
- ✅ Campos `created_at` y `updated_at` deben existir
- ✅ Campos de texto deben tener límites de longitud
- ✅ Campos numéricos deben tener tipos apropiados
- ✅ No debe haber dependencias transitivas (3NF)
- ✅ Campos nullable deben justificarse

**Output:**
```json
{
  "status": "valid|invalid|warning",
  "errors": [],
  "warnings": [],
  "suggestions": [
    {
      "type": "missing_index",
      "table": "messages",
      "column": "conversation_id",
      "recommendation": "Add index for foreign key"
    }
  ]
}
```

#### 1.2 `check_migrations(syntax=True, compatibility=True, rollback=True)`
**Descripción**: Valida migraciones SQL

**Parámetros:**
- `syntax` (bool): Verificar sintaxis SQL
- `compatibility` (bool): Verificar compatibilidad con MySQL
- `rollback` (bool): Verificar que migración sea reversible

**Reglas de Validación:**
- ✅ Sintaxis SQL válida
- ✅ Compatible con MySQL 8.0+
- ✅ Usa transacciones (`BEGIN`, `COMMIT`)
- ✅ Tiene rollback definido
- ✅ No destruye datos sin backup
- ✅ Índices se crean después de datos

**Output:**
```json
{
  "status": "valid|invalid",
  "errors": [],
  "warnings": [],
  "migration_file": "sql/migrations/add_message_type.sql"
}
```

#### 1.3 `optimize_queries(analyze=True, suggest_indexes=True)`
**Descripción**: Analiza y optimiza queries SQL

**Parámetros:**
- `analyze` (bool): Analizar queries existentes
- `suggest_indexes` (bool): Sugerir índices faltantes

**Reglas:**
- ✅ Queries sin `WHERE` deben justificarse
- ✅ `SELECT *` debe evitarse
- ✅ Queries con `JOIN` deben tener índices apropiados
- ✅ Queries con `LIKE '%pattern%'` deben tener índice fulltext

**Output:**
```json
{
  "optimizations": [
    {
      "query": "SELECT * FROM messages WHERE conversation_id = ?",
      "issue": "missing_index",
      "suggestion": "Add index on conversation_id"
    }
  ]
}
```

#### 1.4 `validate_connection_pool(pool_size=True, timeout=True)`
**Descripción**: Valida configuración de conexión a BD

**Parámetros:**
- `pool_size` (bool): Verificar tamaño del pool
- `timeout` (bool): Verificar timeouts

**Reglas:**
- ✅ Pool size debe ser entre 5-50
- ✅ Max overflow debe ser <= pool_size * 2
- ✅ Timeout debe ser >= 5 segundos
- ✅ Pool recycle debe ser <= 3600 segundos

**Output:**
```json
{
  "status": "valid|invalid",
  "current_config": {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_recycle": 1800
  },
  "recommendations": []
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "db",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "validate_on_save": false,
    "auto_suggest_indexes": true,
    "strict_mode": false,
    "allowed_orms": ["sqlalchemy", "django_orm"],
    "database_type": "mysql",
    "min_pool_size": 5,
    "max_pool_size": 50
  }
}
```

### 📤 Formato de Feedback

```json
{
  "agent": "db",
  "trigger_id": "db-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed|error|warning",
  "file_analyzed": "app/models/current.py",
  "results": {
    "model_validation": {...},
    "migration_validation": {...},
    "optimizations": [...]
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 2. AGENTE BACKEND

### 🎯 Responsabilidad Principal
Validar endpoints, seguridad, lógica de negocio y estructura de APIs.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/main.py`
- `app/webapp/**/*.py`
- `app/api/**/*.py`
- `app/core/**/*.py`
- `app/services/**/*.py`

**Archivos Específicos:**
- `app/main.py`
- `app/webapp/__init__.py`
- `app/webapp/security.py`
- `app/core/config.py`

### 🔧 Funciones Principales

#### 2.1 `validate_endpoint(endpoint_data, security=True, validation=True)`
**Descripción**: Valida un endpoint REST

**Parámetros:**
- `endpoint_data`: Información del endpoint
- `security` (bool): Verificar seguridad
- `validation` (bool): Verificar validación de datos

**Reglas de Validación:**
- ✅ Endpoints deben tener autenticación (excepto públicos)
- ✅ Parámetros deben validarse
- ✅ Respuestas deben tener códigos HTTP apropiados
- ✅ Errores deben manejarse correctamente
- ✅ No debe exponer información sensible en errores
- ✅ Debe tener rate limiting en endpoints públicos
- ✅ Debe validar tipos de datos

**Output:**
```json
{
  "endpoint": "/api/chat",
  "method": "POST",
  "status": "valid|invalid|warning",
  "security_issues": [
    {
      "type": "missing_authentication",
      "severity": "high",
      "recommendation": "Add @requires_auth decorator"
    }
  ],
  "validation_issues": []
}
```

#### 2.2 `check_security(vulnerabilities=True, auth=True, data_validation=True)`
**Descripción**: Verifica seguridad del código

**Parámetros:**
- `vulnerabilities` (bool): Buscar vulnerabilidades comunes
- `auth` (bool): Verificar autenticación/autorización
- `data_validation` (bool): Verificar validación de datos

**Reglas de Seguridad:**
- ✅ No debe haber SQL injection (usar parámetros)
- ✅ No debe haber XSS en respuestas
- ✅ Contraseñas deben hashearse (bcrypt)
- ✅ Tokens deben validarse correctamente
- ✅ Sesiones deben expirar
- ✅ CORS debe estar configurado correctamente
- ✅ Headers de seguridad deben estar presentes

**Output:**
```json
{
  "status": "secure|vulnerable|warning",
  "vulnerabilities": [
    {
      "type": "sql_injection",
      "file": "app/webapp/user_management.py",
      "line": 45,
      "severity": "high",
      "recommendation": "Use parameterized queries"
    }
  ],
  "auth_issues": [],
  "validation_issues": []
}
```

#### 2.3 `validate_data_validation(input_validation=True, output_validation=True)`
**Descripción**: Valida validación de datos

**Parámetros:**
- `input_validation` (bool): Verificar validación de entrada
- `output_validation` (bool): Verificar validación de salida

**Reglas:**
- ✅ Todos los inputs deben validarse
- ✅ Tipos deben verificarse
- ✅ Ranges deben validarse
- ✅ Strings deben sanitizarse
- ✅ JSON debe validarse antes de procesar

**Output:**
```json
{
  "status": "valid|invalid",
  "missing_validations": [
    {
      "file": "app/main.py",
      "function": "api_chat",
      "parameter": "text",
      "recommendation": "Add length validation (max 5000 chars)"
    }
  ]
}
```

#### 2.4 `check_error_handling(try_except=True, logging=True)`
**Descripción**: Verifica manejo de errores

**Parámetros:**
- `try_except` (bool): Verificar try/except apropiados
- `logging` (bool): Verificar logging de errores

**Reglas:**
- ✅ Operaciones críticas deben tener try/except
- ✅ Errores deben loguearse apropiadamente
- ✅ Errores no deben exponer stack traces a usuarios
- ✅ Errores deben tener códigos HTTP apropiados
- ✅ Errores de BD deben manejarse correctamente

**Output:**
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
  ]
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "backend",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "strict_security": true,
    "framework": "fastapi",
    "require_authentication": true,
    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
    "rate_limiting": {
      "enabled": true,
      "default_limit": 60,
      "per_minute": true
    }
  }
}
```

### 📤 Formato de Feedback

```json
{
  "agent": "backend",
  "trigger_id": "backend-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/main.py",
  "results": {
    "endpoints_validated": 25,
    "security_issues": 2,
    "validation_issues": 1,
    "error_handling_issues": 0
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 3. AGENTE FRONTEND/UX

### 🎯 Responsabilidad Principal
Validar templates HTML, CSS, JavaScript, accesibilidad y UX.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/webapp/templates/**/*.html`
- `app/webapp/static/css/**/*.css`
- `app/webapp/static/js/**/*.js`
- `app/webapp/static/manifest.json`

**Archivos Específicos:**
- `app/webapp/templates/*.html`
- `app/webapp/static/css/styles.css`
- `app/webapp/static/js/language.js`

### 🔧 Funciones Principales

#### 3.1 `validate_html(semantic=True, accessibility=True, structure=True)`
**Descripción**: Valida HTML semántico y accesibilidad

**Parámetros:**
- `semantic` (bool): Verificar HTML semántico
- `accessibility` (bool): Verificar accesibilidad WCAG
- `structure` (bool): Verificar estructura

**Reglas de Validación:**
- ✅ Debe usar elementos semánticos (`<header>`, `<nav>`, `<main>`, etc.)
- ✅ Imágenes deben tener `alt` text
- ✅ Formularios deben tener labels asociados
- ✅ Links deben tener texto descriptivo
- ✅ Debe tener estructura jerárquica correcta (`h1` → `h2` → `h3`)
- ✅ Debe tener `lang` attribute en `<html>`
- ✅ Debe ser compatible con screen readers

**Output:**
```json
{
  "file": "app/webapp/templates/panel.html",
  "status": "valid|invalid|warning",
  "accessibility_issues": [
    {
      "type": "missing_alt",
      "element": "img",
      "line": 45,
      "recommendation": "Add alt='Description of image'"
    }
  ],
  "semantic_issues": []
}
```

#### 3.2 `validate_css(optimization=True, responsive=True, best_practices=True)`
**Descripción**: Valida CSS

**Parámetros:**
- `optimization` (bool): Verificar optimización
- `responsive` (bool): Verificar responsive design
- `best_practices` (bool): Verificar mejores prácticas

**Reglas:**
- ✅ No debe haber estilos duplicados
- ✅ Debe usar media queries para responsive
- ✅ Debe evitar `!important` innecesarios
- ✅ Debe usar variables CSS cuando sea posible
- ✅ Selectores deben ser específicos pero no demasiado
- ✅ Debe tener fallbacks para propiedades nuevas

**Output:**
```json
{
  "file": "app/webapp/static/css/styles.css",
  "status": "valid|needs_optimization",
  "duplicates": [
    {
      "property": "color: #333",
      "occurrences": 5,
      "recommendation": "Create CSS variable"
    }
  ],
  "responsive_issues": []
}
```

#### 3.3 `validate_javascript(syntax=True, best_practices=True, performance=True)`
**Descripción**: Valida JavaScript

**Parámetros:**
- `syntax` (bool): Verificar sintaxis
- `best_practices` (bool): Verificar mejores prácticas
- `performance` (bool): Verificar performance

**Reglas:**
- ✅ Debe usar `const`/`let` en lugar de `var`
- ✅ Debe evitar globals
- ✅ Debe manejar errores apropiadamente
- ✅ Debe evitar memory leaks
- ✅ Debe usar eventos eficientemente
- ✅ Debe validar inputs del usuario

**Output:**
```json
{
  "file": "app/webapp/static/js/language.js",
  "status": "valid|needs_improvement",
  "syntax_errors": [],
  "best_practices_issues": [
    {
      "type": "var_usage",
      "line": 12,
      "recommendation": "Use const or let instead of var"
    }
  ]
}
```

#### 3.4 `check_responsive_design(breakpoints=True, mobile=True)`
**Descripción**: Verifica diseño responsive

**Parámetros:**
- `breakpoints` (bool): Verificar breakpoints
- `mobile` (bool): Verificar versión móvil

**Reglas:**
- ✅ Debe tener breakpoints para mobile, tablet, desktop
- ✅ Debe funcionar en pantallas pequeñas (320px+)
- ✅ Touch targets deben ser >= 44x44px
- ✅ Texto debe ser legible sin zoom

**Output:**
```json
{
  "status": "responsive|needs_improvement",
  "breakpoints": {
    "mobile": true,
    "tablet": true,
    "desktop": true
  },
  "issues": []
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "frontend",
  "enabled": true,
  "priority": "medium",
  "config": {
    "validate_on_change": true,
    "accessibility_level": "WCAG2AA",
    "template_engine": "jinja2",
    "responsive_breakpoints": {
      "mobile": 768,
      "tablet": 1024,
      "desktop": 1280
    },
    "min_touch_target": 44
  }
}
```

### 📤 Formato de Feedback

```json
{
  "agent": "frontend",
  "trigger_id": "frontend-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/webapp/templates/panel.html",
  "results": {
    "html_validation": {...},
    "css_validation": {...},
    "js_validation": {...},
    "accessibility_score": 85
  }
}
```

---

## 4. AGENTE PERFORMANCE & STABILITY

### 🎯 Responsabilidad Principal
Optimizar performance, detectar cuellos de botella, validar manejo de errores y logging.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/**/*.py`
- `app/core/logging.py`
- `logs/**/*.log`
- `scripts/utils/monitor_services.py`

### 🔧 Funciones Principales

#### 4.1 `analyze_performance(queries=True, async_await=True, caching=True)`
**Descripción**: Analiza performance del código

**Parámetros:**
- `queries` (bool): Analizar queries SQL
- `async_await` (bool): Verificar uso de async/await
- `caching` (bool): Verificar uso de cache

**Reglas:**
- ✅ Queries deben evitar N+1 problems
- ✅ Operaciones I/O deben ser async
- ✅ Debe usar cache cuando sea apropiado
- ✅ No debe bloquear el event loop
- ✅ Debe usar connection pooling

**Output:**
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
  ]
}
```

#### 4.2 `check_error_handling(try_except=True, logging=True, recovery=True)`
**Descripción**: Verifica manejo de errores y recovery

**Parámetros:**
- `try_except` (bool): Verificar try/except
- `logging` (bool): Verificar logging
- `recovery` (bool): Verificar recovery mechanisms

**Reglas:**
- ✅ Errores deben loguearse con contexto
- ✅ Debe tener retry logic para operaciones críticas
- ✅ Debe tener circuit breakers para servicios externos
- ✅ Errores no deben causar crashes

**Output:**
```json
{
  "status": "good|needs_improvement",
  "missing_error_handling": [],
  "logging_issues": []
}
```

#### 4.3 `validate_logging(levels=True, format=True, context=True)`
**Descripción**: Valida sistema de logging

**Parámetros:**
- `levels` (bool): Verificar niveles de log
- `format` (bool): Verificar formato
- `context` (bool): Verificar contexto

**Reglas:**
- ✅ Debe usar niveles apropiados (DEBUG, INFO, WARNING, ERROR)
- ✅ Logs deben tener contexto suficiente
- ✅ No debe loguear información sensible
- ✅ Debe tener formato estructurado

**Output:**
```json
{
  "status": "good|needs_improvement",
  "logging_issues": []
}
```

### ⚙️ Parámetros de Configuración

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

## 5. AGENTE OPENAI

### 🎯 Responsabilidad Principal
Validar integración OpenAI, optimizar prompts, gestionar tokens y costos.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/services/openai_service.py`
- `app/services/openai_advanced.py`
- `app/core/config.py` (solo sección OpenAI)

### 🔧 Funciones Principales

#### 5.1 `validate_integration(api_key=True, assistant_id=True, error_handling=True)`
**Descripción**: Valida integración con OpenAI API

**Parámetros:**
- `api_key` (bool): Verificar API key
- `assistant_id` (bool): Verificar Assistant ID
- `error_handling` (bool): Verificar manejo de errores

**Reglas:**
- ✅ API key debe estar configurada
- ✅ Debe manejar errores de API apropiadamente
- ✅ Debe tener timeouts configurados
- ✅ Debe tener retry logic para rate limits

**Output:**
```json
{
  "status": "valid|invalid",
  "integration_issues": []
}
```

#### 5.2 `optimize_prompts(token_count=True, clarity=True, effectiveness=True)`
**Descripción**: Optimiza prompts para reducir tokens

**Parámetros:**
- `token_count` (bool): Verificar conteo de tokens
- `clarity` (bool): Verificar claridad
- `effectiveness` (bool): Verificar efectividad

**Reglas:**
- ✅ Prompts deben ser claros y concisos
- ✅ Debe evitar tokens innecesarios
- ✅ Debe usar instrucciones específicas
- ✅ Debe incluir ejemplos cuando sea apropiado

**Output:**
```json
{
  "status": "optimized|needs_optimization",
  "suggestions": [
    {
      "prompt": "Generate a response...",
      "current_tokens": 150,
      "optimized_tokens": 120,
      "savings": "20%"
    }
  ]
}
```

#### 5.3 `monitor_costs(tracking=True, limits=True)`
**Descripción**: Monitorea costos de OpenAI

**Parámetros:**
- `tracking` (bool): Verificar tracking de costos
- `limits` (bool): Verificar límites

**Reglas:**
- ✅ Debe trackear tokens usados
- ✅ Debe calcular costos
- ✅ Debe tener límites configurados
- ✅ Debe alertar sobre costos altos

**Output:**
```json
{
  "status": "tracking|not_tracking",
  "costs": {
    "daily": 0.50,
    "monthly": 15.00,
    "limit": 100.00
  }
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "openai",
  "enabled": true,
  "priority": "medium",
  "config": {
    "validate_on_change": true,
    "max_tokens_per_request": 1500,
    "cost_tracking": true,
    "monthly_limit": 100.00,
    "optimize_prompts": true
  }
}
```

---

## 6. AGENTE WHATSAPP

### 🎯 Responsabilidad Principal
Validar integración WhatsApp Business API, webhooks, manejo de mensajes.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/services/whatsapp_service.py`
- `app/services/whatsapp_advanced.py`
- `app/core/config.py` (solo sección WhatsApp)
- `logs/whatsapp_service.log`

### 🔧 Funciones Principales

#### 6.1 `validate_webhook(structure=True, security=True, error_handling=True)`
**Descripción**: Valida estructura de webhook

**Parámetros:**
- `structure` (bool): Verificar estructura
- `security` (bool): Verificar seguridad
- `error_handling` (bool): Verificar manejo de errores

**Reglas:**
- ✅ Webhook debe validar verify token
- ✅ Debe manejar eventos correctamente
- ✅ Debe tener rate limiting
- ✅ Debe responder 200 OK rápidamente

**Output:**
```json
{
  "status": "valid|invalid",
  "webhook_issues": []
}
```

#### 6.2 `validate_message_handling(incoming=True, outgoing=True, states=True)`
**Descripción**: Valida manejo de mensajes

**Parámetros:**
- `incoming` (bool): Verificar mensajes entrantes
- `outgoing` (bool): Verificar mensajes salientes
- `states` (bool): Verificar estados de entrega

**Reglas:**
- ✅ Debe procesar mensajes entrantes correctamente
- ✅ Debe enviar mensajes correctamente
- ✅ Debe trackear estados (sent, delivered, read)
- ✅ Debe manejar errores de envío

**Output:**
```json
{
  "status": "valid|invalid",
  "message_handling_issues": []
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "whatsapp",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "webhook_timeout": 5,
    "rate_limit": 1000,
    "track_delivery_states": true
  }
}
```

---

## 7. AGENTE CODE QUALITY

### 🎯 Responsabilidad Principal
Validar calidad de código, estilo PEP 8, refactoring, convenciones.

### 📁 Archivos Monitoreados

**Patrones:**
- `app/**/*.py`
- `scripts/**/*.py`

### 🔧 Funciones Principales

#### 7.1 `validate_pep8(strict=True, line_length=True)`
**Descripción**: Valida PEP 8 compliance

**Parámetros:**
- `strict` (bool): Modo estricto
- `line_length` (bool): Verificar longitud de líneas

**Reglas:**
- ✅ Líneas <= 120 caracteres
- ✅ Imports ordenados correctamente
- ✅ Nombres siguen convenciones
- ✅ Espaciado correcto

**Output:**
```json
{
  "status": "compliant|needs_fixes",
  "pep8_issues": []
}
```

#### 7.2 `detect_duplication(min_lines=5)`
**Descripción**: Detecta código duplicado

**Parámetros:**
- `min_lines` (int): Mínimo de líneas para considerar duplicado

**Output:**
```json
{
  "status": "clean|has_duplicates",
  "duplications": []
}
```

#### 7.3 `suggest_refactoring(complexity=True, length=True)`
**Descripción**: Sugiere refactoring

**Parámetros:**
- `complexity` (bool): Verificar complejidad ciclomática
- `length` (bool): Verificar longitud de funciones

**Reglas:**
- ✅ Funciones <= 50 líneas
- ✅ Complejidad ciclomática <= 10
- ✅ Clases <= 500 líneas

**Output:**
```json
{
  "status": "good|needs_refactoring",
  "refactoring_suggestions": []
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "code_quality",
  "enabled": true,
  "priority": "medium",
  "config": {
    "validate_on_change": true,
    "pep8_strict": false,
    "max_line_length": 120,
    "max_function_length": 50,
    "max_complexity": 10
  }
}
```

---

## 8. AGENTE TESTS

### 🎯 Responsabilidad Principal
Validar tests, coverage, calidad de pruebas.

### 📁 Archivos Monitoreados

**Patrones:**
- `scripts/tests/**/*.py`
- `app/**/*.py` (para detectar qué necesita tests)

### 🔧 Funciones Principales

#### 8.1 `run_tests(test_files=None, coverage=True)`
**Descripción**: Ejecuta tests

**Parámetros:**
- `test_files` (list): Archivos específicos a testear
- `coverage` (bool): Calcular coverage

**Output:**
```json
{
  "status": "passed|failed",
  "tests_run": 45,
  "tests_passed": 43,
  "tests_failed": 2,
  "coverage": 85.5
}
```

#### 8.2 `suggest_tests(missing=True, edge_cases=True)`
**Descripción**: Sugiere tests faltantes

**Parámetros:**
- `missing` (bool): Detectar tests faltantes
- `edge_cases` (bool): Sugerir edge cases

**Output:**
```json
{
  "status": "complete|incomplete",
  "missing_tests": [
    {
      "file": "app/main.py",
      "function": "api_chat",
      "recommendation": "Add test for invalid input"
    }
  ]
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "tests",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "min_coverage": 80,
    "test_framework": "pytest",
    "run_on_save": false
  }
}
```

---

## 9. AGENTE MAESTRO (Coordinator)

### 🎯 Responsabilidad Principal
Coordinar agentes, tomar decisiones arquitectónicas, gestionar tareas.

### 📁 Archivos Monitoreados

**Todos los archivos del proyecto** (vista general)

### 🔧 Funciones Principales

#### 9.1 `coordinate_task(task_data)`
**Descripción**: Coordina una tarea entre múltiples agentes

**Parámetros:**
- `task_data`: Información de la tarea

**Output:**
```json
{
  "task_id": "task-001",
  "status": "in_progress",
  "agents_assigned": ["db", "backend", "frontend"],
  "dependencies": []
}
```

#### 9.2 `validate_integration(agents_results)`
**Descripción**: Valida integración final de cambios

**Parámetros:**
- `agents_results`: Resultados de todos los agentes

**Output:**
```json
{
  "status": "valid|invalid",
  "integration_issues": []
}
```

### ⚙️ Parámetros de Configuración

```json
{
  "agent": "master",
  "enabled": true,
  "priority": "highest",
  "config": {
    "coordinate_automatically": true,
    "validate_before_completion": true,
    "require_all_agents_approval": false
  }
}
```

---

**Autor**: Composer AI  
**Fecha**: 2025-01-XX  
**Versión**: 1.0

