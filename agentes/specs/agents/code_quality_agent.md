# 🔍 CODE QUALITY AGENT - Especificación Completa

**ID**: `code_quality`  
**Versión**: 1.0  
**Prioridad**: Media  
**Estado**: Habilitado  

---

## 📋 DESCRIPCIÓN GENERAL

El **Code Quality Agent** es un agente especializado en validar calidad de código, estilo PEP 8, detección de duplicación, refactoring y convenciones. Su responsabilidad principal es asegurar que el código sea limpio, mantenible y siga las mejores prácticas.

---

## 🎯 RESPONSABILIDADES PRINCIPALES

1. **Validación PEP 8**: Estilo de código, longitud de líneas, imports, nombres
2. **Detección de Duplicación**: Bloques duplicados, funciones similares, patrones repetidos
3. **Sugerencias de Refactoring**: Complejidad, longitud de funciones, mejoras de código
4. **Verificación de Convenciones**: Nombres, estructura, organización
5. **Análisis de Complejidad**: Complejidad ciclomática, funciones complejas
6. **Verificación de Documentación**: Docstrings, comentarios, documentación
7. **Sugerencias de Mejoras**: Legibilidad, mantenibilidad, performance

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos

```json
{
  "patterns": [
    "app/**/*.py",
    "scripts/**/*.py"
  ]
}
```

### Archivos Específicos

- `app/main.py` - Aplicación principal
- `app/backend/**/*.py` - Todo el código backend

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `validate_pep8()`

**Descripción**: Valida PEP 8 compliance

**Reglas de Validación**:
- ✅ Líneas <= 120 caracteres
- ✅ Imports ordenados correctamente
- ✅ Nombres siguen convenciones
- ✅ Espaciado correcto
- ✅ Uso de whitespace apropiado
- ✅ Comentarios siguen estilo
- ✅ Docstrings apropiados

**Output**:
```json
{
  "status": "compliant|needs_fixes",
  "pep8_issues": [
    {
      "file": "app/main.py",
      "line": 45,
      "code": "E501",
      "message": "Line too long (125 > 120 characters)",
      "recommendation": "Break line into multiple lines"
    }
  ]
}
```

---

### 2. `detect_duplication()`

**Descripción**: Detecta código duplicado

**Reglas de Validación**:
- ✅ Detectar bloques duplicados
- ✅ Detectar funciones similares
- ✅ Detectar patrones repetidos
- ✅ Sugerir extracción de código común

**Output**:
```json
{
  "status": "clean|has_duplicates",
  "duplications": [
    {
      "file1": "app/main.py",
      "file2": "app/services/user_service.py",
      "lines1": [45, 60],
      "lines2": [30, 45],
      "similarity": 0.95,
      "recommendation": "Extract common code to shared function"
    }
  ]
}
```

---

### 3. `suggest_refactoring()`

**Descripción**: Sugiere refactoring basado en complejidad y longitud

**Reglas de Validación**:
- ✅ Funciones <= 50 líneas
- ✅ Complejidad ciclomática <= 10
- ✅ Clases <= 500 líneas
- ✅ Métodos <= 30 líneas
- ✅ Evitar funciones muy largas
- ✅ Evitar clases muy grandes
- ✅ Sugerir extracción de métodos

**Output**:
```json
{
  "status": "good|needs_refactoring",
  "refactoring_suggestions": [
    {
      "file": "app/main.py",
      "function": "process_message",
      "complexity": 15,
      "length": 85,
      "recommendation": "Extract sub-functions to reduce complexity",
      "priority": "high"
    }
  ]
}
```

---

### 4. `check_conventions()`

**Descripción**: Verifica convenciones de código del proyecto

**Reglas de Validación**:
- ✅ Nombres de archivos siguen convenciones
- ✅ Nombres de funciones siguen convenciones
- ✅ Nombres de clases siguen convenciones
- ✅ Estructura de archivos apropiada
- ✅ Imports organizados correctamente

---

### 5. `analyze_complexity()`

**Descripción**: Analiza complejidad ciclomática del código

**Reglas de Validación**:
- ✅ Detectar funciones complejas
- ✅ Detectar clases complejas
- ✅ Sugerir simplificación
- ✅ Identificar código difícil de mantener

---

### 6. `check_documentation()`

**Descripción**: Verifica documentación del código

**Reglas de Validación**:
- ✅ Funciones públicas deben tener docstrings
- ✅ Clases deben tener docstrings
- ✅ Módulos deben tener docstrings
- ✅ Docstrings deben seguir formato apropiado

---

### 7. `suggest_improvements()`

**Descripción**: Sugiere mejoras generales de código

---

## ⚙️ CONFIGURACIÓN

### Parámetros de Configuración

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

## 📤 FORMATO DE FEEDBACK

```json
{
  "agent": "code_quality",
  "trigger_id": "code_quality-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/main.py",
  "results": {
    "pep8_compliance": 92,
    "code_duplication": 3,
    "average_complexity": 7,
    "refactoring_suggestions": 5
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 🧪 TESTING Y PERFORMANCE

### Análisis Automatizado

- **Análisis de Calidad**: Diario a las 10:00 AM

### Métricas Monitoreadas

- **PEP 8 Compliance**: Objetivo 90%
- **Duplicación de Código**: Máximo 5%
- **Complejidad**: Promedio máximo 8, individual máximo 10

---

## ✅ RESUMEN DE CARACTERÍSTICAS DEL AGENTE CODE QUALITY

### Funcionalidades Principales
- ✅ Validación PEP 8 completa
- ✅ Detección de duplicación
- ✅ Sugerencias de refactoring
- ✅ Análisis de complejidad
- ✅ Verificación de documentación
- ✅ Sugerencias de mejoras

### Monitoreo
- ✅ Monitoreo automático de cambios en código
- ✅ Activación automática al modificar archivos
- ✅ Análisis continuo de calidad

---

**Última actualización**: 2025-01-XX

