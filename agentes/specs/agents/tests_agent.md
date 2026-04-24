# 🧪 TESTS AGENT - Especificación Completa

**ID**: `tests`  
**Versión**: 1.0  
**Prioridad**: Alta  
**Estado**: Habilitado  

---

## 📋 DESCRIPCIÓN GENERAL

El **Tests Agent** es un agente especializado en validar tests, coverage, calidad de pruebas y sugerir tests faltantes. Su responsabilidad principal es asegurar que el código tenga buena cobertura de tests y que los tests sean de alta calidad.

---

## 🎯 RESPONSABILIDADES PRINCIPALES

1. **Ejecución de Tests**: Ejecutar tests y calcular coverage
2. **Sugerencias de Tests**: Detectar tests faltantes y edge cases
3. **Validación de Calidad**: Calidad de tests existentes
4. **Análisis de Coverage**: Coverage y sugerencias de mejoras
5. **Verificación de Performance**: Performance de tests
6. **Validación de Estructura**: Estructura de tests
7. **Sugerencias de Mejoras**: Mejoras para tests

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos

```json
{
  "patterns": [
    "**/test_*.py",
    "**/*_test.py",
    "tests/**/*.py",
    "app/**/*.py"
  ]
}
```

### Archivos Específicos

- `scripts/tests/**/*.py` - Tests del proyecto

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `run_tests()`

**Descripción**: Ejecuta tests y calcula coverage

**Reglas de Validación**:
- ✅ Ejecutar todos los tests
- ✅ Calcular coverage
- ✅ Reportar resultados
- ✅ Detectar tests fallidos
- ✅ Identificar tests lentos

**Output**:
```json
{
  "status": "passed|failed",
  "tests_run": 45,
  "tests_passed": 43,
  "tests_failed": 2,
  "coverage": 85.5,
  "failed_tests": [
    {
      "test": "test_user_creation",
      "file": "tests/test_user_service.py",
      "error": "AssertionError: Expected user.active to be True"
    }
  ]
}
```

---

### 2. `suggest_tests()`

**Descripción**: Sugiere tests faltantes y edge cases

**Reglas de Validación**:
- ✅ Detectar funciones sin tests
- ✅ Detectar clases sin tests
- ✅ Sugerir edge cases
- ✅ Sugerir tests de integración
- ✅ Sugerir tests de performance
- ✅ Sugerir tests de seguridad

**Output**:
```json
{
  "status": "complete|incomplete",
  "missing_tests": [
    {
      "file": "app/main.py",
      "function": "api_chat",
      "recommendation": "Add test for invalid input",
      "priority": "high"
    }
  ],
  "edge_cases": [
    {
      "file": "app/main.py",
      "function": "process_message",
      "recommendation": "Add test for empty message",
      "priority": "medium"
    }
  ]
}
```

---

### 3. `validate_test_quality()`

**Descripción**: Valida calidad de tests existentes

**Reglas de Validación**:
- ✅ Tests deben ser claros y legibles
- ✅ Tests deben tener nombres descriptivos
- ✅ Tests deben ser independientes
- ✅ Tests deben usar fixtures apropiadas
- ✅ Tests deben tener assertions apropiadas
- ✅ Tests no deben tener lógica compleja

---

### 4. `analyze_coverage()`

**Descripción**: Analiza coverage y sugiere mejoras

**Reglas de Validación**:
- ✅ Coverage debe ser >= 80%
- ✅ Código crítico debe tener coverage >= 90%
- ✅ Detectar áreas sin coverage
- ✅ Sugerir tests para aumentar coverage
- ✅ Analizar coverage por módulo

**Output**:
```json
{
  "overall_coverage": 85.5,
  "target_coverage": 80,
  "coverage_by_module": {
    "app/main.py": 75,
    "app/backend/services/user_service.py": 90
  },
  "missing_coverage": [
    {
      "file": "app/main.py",
      "lines": [45, 60],
      "recommendation": "Add tests for error handling"
    }
  ]
}
```

---

### 5. `check_test_performance()`

**Descripción**: Verifica performance de tests

**Reglas de Validación**:
- ✅ Tests deben ejecutarse rápidamente
- ✅ Detectar tests lentos
- ✅ Sugerir optimizaciones
- ✅ Detectar tests que usan recursos pesados

---

### 6. `validate_test_structure()`

**Descripción**: Valida estructura de tests

**Reglas de Validación**:
- ✅ Tests deben seguir estructura apropiada
- ✅ Tests deben estar organizados
- ✅ Tests deben usar fixtures apropiadas
- ✅ Tests deben tener setup/teardown apropiado

---

### 7. `suggest_improvements()`

**Descripción**: Sugiere mejoras para tests

---

## ⚙️ CONFIGURACIÓN

### Parámetros de Configuración

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

## 📤 FORMATO DE FEEDBACK

```json
{
  "agent": "tests",
  "trigger_id": "tests-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "results": {
    "tests_run": 45,
    "tests_passed": 43,
    "tests_failed": 2,
    "coverage": 85.5,
    "test_quality_score": 88
  },
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 🧪 TESTING Y PERFORMANCE

### Análisis Automatizado

- **Ejecución de Tests**: Diario a las 11:00 AM
- **Análisis de Coverage**: Diario a las 12:00 PM

### Métricas Monitoreadas

- **Coverage**: Objetivo 80%, crítico 90%
- **Performance de Tests**: Promedio máximo 1s, individual máximo 5s
- **Calidad de Tests**: Objetivo 85%

---

## ✅ RESUMEN DE CARACTERÍSTICAS DEL AGENTE TESTS

### Funcionalidades Principales
- ✅ Ejecución automatizada de tests
- ✅ Cálculo de coverage
- ✅ Sugerencias de tests faltantes
- ✅ Validación de calidad de tests
- ✅ Análisis de performance
- ✅ Sugerencias de mejoras

### Monitoreo
- ✅ Monitoreo automático de cambios en código
- ✅ Activación automática al modificar archivos
- ✅ Análisis continuo de coverage y calidad

---

**Última actualización**: 2025-01-XX

