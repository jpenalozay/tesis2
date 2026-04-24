# 📚 DOCUMENTACIÓN GENERAL - ÍNDICE

**Ubicación**: `agentes/docs/`

---

## 📖 DOCUMENTOS DISPONIBLES

### 1. **ARQUITECTURA_AGENTES_COMPLETA.md**
**Propósito**: Arquitectura completa del sistema multi-agente

**Contenido**:
- Análisis del enfoque propuesto
- Definición de los 9 agentes especializados
- Comparación de formatos de comunicación (JSON, YAML, TOML, SQLite, MD)
- Recomendación final: Formato híbrido JSON + Markdown
- Estructura de archivos propuesta

**Cuándo leerlo**: 
- Para entender la arquitectura completa del sistema
- Al iniciar el proyecto de agentes
- Para tomar decisiones arquitectónicas

---

### 2. **ESPECIFICACION_AGENTES_COMPLETA.md**
**Propósito**: Especificación inicial de todos los agentes

**Contenido**:
- Funciones principales de cada agente
- Reglas de validación básicas
- Parámetros de configuración
- Formatos de feedback

**Cuándo leerlo**:
- Para ver la especificación inicial de todos los agentes
- Como referencia rápida de funciones disponibles
- Para entender el alcance completo del sistema

---

### 3. **MASTER_AGENT_AUTONOMO.md**
**Propósito**: Sistema de Master Agent autónomo (futuro)

**Contenido**:
- Análisis completo de proyectos nuevos
- Creación automática de agentes
- Guardado de conocimiento en formato optimizado
- Sistema de inicialización automática

**Cuándo leerlo**:
- Para entender el sistema de Master Agent (implementación futura)
- Para planificar la automatización completa
- Como referencia de arquitectura avanzada

**Nota**: ⚠️ Esta funcionalidad está planificada para el futuro

---

### 4. **REDIS_VS_ARCHIVOS_COMUNICACION.md**
**Propósito**: Análisis de comunicación entre agentes

**Contenido**:
- Comparación Redis vs Archivos JSON
- Performance metrics (10-200x más rápido con Redis)
- Arquitectura híbrida recomendada
- Implementación práctica
- Ejemplos de código

**Cuándo leerlo**:
- Para entender cómo comunican los agentes entre sí
- Para implementar el sistema de comunicación
- Para optimizar la performance del sistema

---

## 🎯 FLUJO DE LECTURA RECOMENDADO

### Para Nuevos Desarrolladores:
1. **ARQUITECTURA_AGENTES_COMPLETA.md** - Entender el sistema completo
2. **ESPECIFICACION_AGENTES_COMPLETA.md** - Ver qué hace cada agente
3. **REDIS_VS_ARCHIVOS_COMUNICACION.md** - Entender la comunicación
4. Especificaciones específicas de cada agente en `specs/agents/`

### Para Implementar un Agente:
1. Especificación del agente en `specs/agents/`
2. Ejemplo de configuración en `config/examples/`
3. **REDIS_VS_ARCHIVOS_COMUNICACION.md** - Para comunicación
4. **ARQUITECTURA_AGENTES_COMPLETA.md** - Para contexto general

---

**Última actualización**: 2025-01-XX

