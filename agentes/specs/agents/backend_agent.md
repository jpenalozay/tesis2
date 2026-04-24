# 🔧 AGENTE BACKEND - GUÍA COMPLETA PARA DESARROLLADORES

**Versión**: 1.0  
**Entorno**: Desarrollo (DEV)  
**Última actualización**: 2025-01-XX

---

## 📖 ¿QUÉ ES EL AGENTE BACKEND?

El **Agente Backend** es un agente especializado que se encarga de validar, crear y modificar código backend del proyecto. Su trabajo es asegurar que el código siga mejores prácticas, sea seguro y mantenga la arquitectura correcta.

---

## 🎯 ¿QUÉ HACE EL AGENTE BACKEND?

### Funciones Principales

1. **Validar Código**
   - Verifica sintaxis Python
   - Valida seguridad
   - Verifica mejores prácticas
   - Revisa dependencias

2. **Validar Endpoints API**
   - Verifica definición de rutas
   - Valida autenticación y autorización
   - Verifica validación de inputs
   - Revisa manejo de errores
   - Valida formato de respuestas

3. **Validar Seguridad**
   - Autenticación y autorización
   - Sanitización de inputs
   - Prevención de SQL injection
   - Protección XSS
   - Seguridad de contraseñas
   - Seguridad de sesiones
   - Gestión de secrets

4. **Generar Código**
   - Crea endpoints siguiendo patrones
   - Genera servicios siguiendo estructura
   - Incluye seguridad automáticamente
   - Genera documentación

5. **Modificar Código**
   - Modifica código manteniendo compatibilidad
   - Preserva funcionalidad existente
   - Sigue patrones del proyecto
   - Actualiza dependencias si es necesario

6. **Analizar Arquitectura**
   - Analiza estructura del backend
   - Detecta problemas de diseño
   - Sugiere mejoras
   - Valida dependencias

---

## 📁 ¿QUÉ ARCHIVOS MONITOREA?

El Agente Backend vigila estos archivos automáticamente:

### Patrones de Archivos
- `app/backend/**/*.py` - Todo el código Python del backend
- `app/main.py` - Punto de entrada principal
- `app/backend/api/**/*.py` - Rutas API organizadas
- `app/backend/services/**/*.py` - Servicios de negocio
- `app/backend/core/**/*.py` - Configuración central

### Archivos Específicos Importantes
- `app/main.py` - Aplicación principal FastAPI (1,286 líneas)
- `app/backend/api/routes/web.py` - Router principal web
- `app/backend/core/security.py` - Autenticación y seguridad
- `app/backend/services/internal/user_service.py` - Gestión de usuarios
- `app/backend/services/external/openai_service.py` - Servicio OpenAI
- `app/backend/services/external/whatsapp_service.py` - Servicio WhatsApp
- `app/backend/services/external/email_service.py` - Servicio Email
- `app/backend/core/config.py` - Configuración centralizada

---

## 🔔 ¿CUÁNDO SE ACTIVA EL AGENTE BACKEND?

El agente se activa automáticamente cuando:

1. **Modificas código Python** (`app/backend/**/*.py`)
   - Agregas un nuevo endpoint
   - Modificas un endpoint existente
   - Creas un nuevo servicio
   - Cambias configuración

2. **Creas un nuevo archivo** (`app/backend/**/*.py`)
   - Nuevo endpoint
   - Nuevo servicio
   - Nuevo módulo

3. **Modificas configuración** (`app/backend/core/config.py`)
   - Cambios en configuración
   - Variables de entorno

---

## 📊 NIVELES DE IMPORTANCIA

El Agente Backend clasifica sus validaciones en 4 niveles:

### 🔴 CRITICAL (Crítico)
**Bloquea cambios si falla**

- ✅ Autenticación requerida en endpoints sensibles
- ✅ Autorización verificada en endpoints administrativos
- ✅ Validación de inputs en todos los endpoints
- ✅ Prevención de SQL injection
- ✅ Contraseñas hasheadas
- ✅ Secrets no hardcodeados
- ✅ Manejo de errores en todos los endpoints

**Ejemplo**: Si creas un endpoint sin autenticación, el agente bloqueará el cambio.

---

### 🟠 HIGH (Alto)
**Muestra warning pero permite continuar**

- ⚠️ Formato de respuesta consistente
- ⚠️ Sanitización de inputs
- ⚠️ Rate limiting en endpoints públicos
- ⚠️ Seguridad de sesiones
- ⚠️ Dependency injection correcta
- ⚠️ Uso consistente de async/await

**Ejemplo**: Si falta rate limiting en un endpoint público, el agente mostrará un warning pero no bloquea.

---

### 🟡 MEDIUM (Medio)
**Sugerencias que no bloquean**

- 💡 Documentación (docstrings)
- 💡 Type hints
- 💡 Organización del código
- 💡 Logging
- 💡 Mensajes de error informativos

**Ejemplo**: Si falta un docstring, el agente sugerirá agregarlo pero no bloquea.

---

### 🟢 LOW (Bajo)
**Solo información**

- 📝 Comentarios en código complejo

**Ejemplo**: El agente sugiere agregar comentarios pero es completamente opcional.

---

## 🔒 REGLAS DE SEGURIDAD

### Autenticación

**Endpoints que REQUIEREN autenticación**:
- `/api/admin/**` - Todas las rutas administrativas
- `/api/asesor/**` - Rutas de asesores
- `/api/profile/**` - Perfil de usuario
- `/api/chat` - Enviar mensajes
- `/api/conversations` - Listar conversaciones
- `/api/messages` - Obtener mensajes

**Endpoints OPCIONALES**:
- `/health` - Health check
- `/api/settings/mode` - Modo global (según rol)

---

### Autorización

**Solo Admin**:
- `/api/admin/**` - Todas las rutas administrativas

**Admin o Asesor**:
- `/api/settings/mode` - Cambiar modo global
- `/api/review/**` - Cola de revisión

**Solo Asesor**:
- `/api/asesor/**` - Rutas de asesores

---

### Validación de Inputs

**Todos los inputs deben ser validados**:
- ✅ Tipos de datos correctos
- ✅ Rangos válidos
- ✅ Strings sanitizados
- ✅ SQL injection prevention
- ✅ XSS protection

---

## 🛠️ GENERACIÓN DE CÓDIGO

El Agente Backend puede generar código siguiendo patrones:

### Endpoint Template

```python
@app.post('/api/example')
async def example_endpoint(
    payload: dict = Body(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Descripción del endpoint
    
    Args:
        payload: Datos del request
        user: Usuario autenticado
        session: Sesión de base de datos
    
    Returns:
        dict: Respuesta JSON
    """
    try:
        # Validación
        if not payload.get('field'):
            return JSONResponse(
                {'ok': False, 'error': 'missing_field'}, 
                status_code=400
            )
        
        # Lógica del negocio
        result = do_something(payload, user, session)
        
        return {'ok': True, 'data': result}
    except Exception as e:
        session.rollback()
        return JSONResponse(
            {'ok': False, 'error': str(e)}, 
            status_code=500
        )
```

---

## 📋 ENDPOINTS ACTUALES DEL PROYECTO

### Endpoints de Sistema
- `GET /health` - Health check
- `GET /api/settings/mode` - Obtener modo global
- `PUT /api/settings/mode` - Cambiar modo global

### Endpoints de Mensajes
- `GET /api/messages` - Obtener mensajes de conversación
- `POST /api/chat` - Enviar mensaje

### Endpoints de Conversaciones
- `GET /api/conversations` - Listar conversaciones
- `GET /api/conversations/{conv_id}` - Obtener conversación
- `PUT /api/conversations/{conv_id}/mode` - Cambiar modo de conversación

### Endpoints de Revisión
- `GET /api/review/queue` - Cola de revisión
- `POST /api/review/{message_id}/approve` - Aprobar mensaje

### Endpoints de Admin
- `POST /api/admin/users` - Crear usuario
- `GET /api/admin/users` - Listar usuarios
- `PUT /api/admin/users/{user_id}` - Actualizar usuario
- `DELETE /api/admin/users/{user_id}` - Eliminar usuario
- `POST /api/admin/users/{user_id}/toggle-status` - Cambiar estado
- `POST /api/admin/bulk-assign-chats` - Asignar chats masivamente
- `GET /api/admin/stats` - Estadísticas administrativas

### Endpoints de Asesor
- `GET /api/asesor/stats` - Estadísticas del asesor
- `POST /api/asesor/chats` - Obtener chats asignados
- `POST /api/asesor/complete-chat/{assignment_id}` - Completar chat

### Endpoints de Perfil
- `POST /api/profile/update` - Actualizar perfil
- `POST /api/profile/change-password` - Cambiar contraseña

### Endpoints Internos
- `POST /internal/send` - Enviar mensaje interno
- `POST /internal/notify` - Notificación interna
- `WebSocket /ws` - WebSocket para chat en tiempo real

---

## ✅ EJEMPLOS PRÁCTICOS

### Ejemplo 1: Crear Nuevo Endpoint

**❌ INCORRECTO**:
```python
@app.post('/api/test')
async def test_endpoint(data: dict):
    # Sin autenticación
    # Sin validación
    # Sin manejo de errores
    return data
```

**El Agente Backend detectará**:
- 🔴 Error CRITICAL: Falta autenticación
- 🔴 Error CRITICAL: Falta validación de inputs
- 🔴 Error CRITICAL: Falta manejo de errores

**✅ CORRECTO**:
```python
@app.post('/api/test')
async def test_endpoint(
    payload: dict = Body(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Endpoint de prueba con seguridad"""
    try:
        # Validación
        if not payload.get('field'):
            return JSONResponse(
                {'ok': False, 'error': 'missing_field'}, 
                status_code=400
            )
        
        # Lógica
        result = process_data(payload, user, session)
        
        return {'ok': True, 'data': result}
    except Exception as e:
        session.rollback()
        return JSONResponse(
            {'ok': False, 'error': str(e)}, 
            status_code=500
        )
```

---

### Ejemplo 2: SQL Injection

**❌ INCORRECTO**:
```python
query = f"SELECT * FROM users WHERE phone = '{phone}'"
result = session.execute(text(query))
```

**El Agente Backend detectará**:
- 🔴 Error CRITICAL: SQL injection vulnerability

**✅ CORRECTO**:
```python
query = text("SELECT * FROM users WHERE phone = :phone")
result = session.execute(query, {"phone": phone})
```

---

### Ejemplo 3: Contraseña sin Hash

**❌ INCORRECTO**:
```python
user = User(password=password)  # Sin hash
```

**El Agente Backend detectará**:
- 🔴 Error CRITICAL: Password not hashed

**✅ CORRECTO**:
```python
from app.webapp.security import hash_password
password_hash = hash_password(password)
user = User(password_hash=password_hash)
```

---

## 📤 ¿QUÉ OUTPUT GENERA EL AGENTE BACKEND?

El agente genera feedback en formato JSON que puedes ver en:

- **Redis**: `agent:feedback:backend:{task_id}` (comunicación rápida)
- **Archivo**: `.agents/communications/backend_feedback.json` (persistencia)

### Ejemplo de Feedback:

```json
{
  "agent": "backend",
  "status": "completed",
  "file_analyzed": "app/main.py",
  "results": {
    "code_validation": {
      "status": "valid",
      "errors": [],
      "warnings": [
        {
          "type": "missing_rate_limiting",
          "endpoint": "/api/test",
          "message": "Endpoint público debería tener rate limiting",
          "suggestion": "Agregar @limiter.limit decorator"
        }
      ]
    },
    "security_validation": {
      "status": "valid",
      "errors": [],
      "warnings": []
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

## 🚨 ¿QUÉ PASA SI EL AGENTE DETECTA ERRORES CRÍTICOS?

Si el agente detecta errores **CRITICAL**:

1. **Bloquea el cambio** (no permite continuar)
2. **Genera feedback** con el error específico
3. **Sugiere solución** automáticamente
4. **Notifica al Maestro** para coordinación

---

## 📁 ARCHIVOS RELACIONADOS

- **Configuración JSON**: `agentes/specs/agents/backend_agent.json`
- **Conocimiento**: `agentes/specs/agents/backend_agent_knowledge.json`
- **Pruebas**: `agentes/specs/agents/backend_agent_test_performance.json`

---

## 🔗 COMUNICACIÓN CON OTROS AGENTES

El Agente Backend se comunica con:

- **DB**: Notifica cambios en modelos que requieren actualización de endpoints
- **Frontend**: Informa cambios en APIs que afectan el frontend
- **Tests**: Notifica cambios que requieren nuevos tests
- **Maestro**: Envía feedback después de validaciones

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿El agente puede generar código automáticamente?**  
R: Sí, puede generar código siguiendo patrones y mejores prácticas. Puedes pedirle que cree endpoints, servicios, etc.

**P: ¿El agente modifica mi código automáticamente?**  
R: Solo cuando se lo pides explícitamente. Por defecto solo valida y sugiere.

**P: ¿Cómo veo el feedback del agente?**  
R: Se guarda en `.agents/communications/backend_feedback.json` y también en Redis.

**P: ¿El agente valida solo endpoints o también servicios?**  
R: Valida todo el código backend: endpoints, servicios, módulos, configuración.

---

## 📋 RESUMEN DE CARACTERÍSTICAS DEL AGENTE BACKEND

### ✅ Funcionalidades Principales

1. **Validación de Código**
   - ✅ Validación de sintaxis Python
   - ✅ Validación de seguridad
   - ✅ Verificación de mejores prácticas
   - ✅ Revisión de dependencias

2. **Validación de Endpoints**
   - ✅ Validación de rutas FastAPI
   - ✅ Verificación de autenticación/autorización
   - ✅ Validación de inputs
   - ✅ Manejo de errores
   - ✅ Formato de respuestas

3. **Validación de Seguridad**
   - ✅ Autenticación y autorización
   - ✅ Prevención SQL injection
   - ✅ Protección XSS
   - ✅ Seguridad de contraseñas
   - ✅ Seguridad de sesiones
   - ✅ Gestión de secrets

4. **Generación de Código**
   - ✅ Genera endpoints siguiendo patrones
   - ✅ Genera servicios siguiendo estructura
   - ✅ Incluye seguridad automáticamente
   - ✅ Genera documentación

5. **Modificación de Código**
   - ✅ Mantiene compatibilidad hacia atrás
   - ✅ Preserva funcionalidad
   - ✅ Sigue patrones del proyecto

6. **Análisis de Arquitectura**
   - ✅ Analiza estructura del backend
   - ✅ Detecta problemas de diseño
   - ✅ Sugiere mejoras

### 📊 Niveles de Validación

- 🔴 **CRITICAL**: Bloquea cambios si falla
- 🟠 **HIGH**: Muestra warnings pero permite continuar
- 🟡 **MEDIUM**: Sugerencias que no bloquean
- 🟢 **LOW**: Solo información

### 🔄 Automatización

- ✅ Activación automática al modificar archivos
- ✅ Actualización automática del conocimiento
- ✅ Generación automática de sugerencias
- ✅ Validación automática de seguridad

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0

