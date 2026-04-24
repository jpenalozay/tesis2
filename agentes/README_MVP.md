# 🚀 Framework Multi-Agente MVP - Guía de Uso

## 📋 Descripción

Framework de desarrollo automatizado basado en inteligencia artificial multi-agente. Utiliza DeepSeek LLM para generar código de calidad empresarial con supervisión y auditoría completa.

## ✨ Características

- **Protocolo TOON**: 30-60% más eficiente que JSON
- **Risk Scoring Matemático**: Evaluación tridimensional de riesgo
- **5 Agentes Especializados**: Arquitecto, Sentinel, Coder, Linter, Tester
- **Auditoría Completa**: Trazabilidad end-to-end
- **CLI Funcional**: Interfaz de línea de comandos

## 🔧 Instalación

### 1. Instalar dependencias

```bash
cd agentes
pip install -r requirements.txt
```

### 2. Configurar API Key

Edita el archivo `.env` y agrega tu API key de DeepSeek:

```bash
DEEPSEEK_API_KEY=tu_api_key_aqui
```

### 3. Verificar instalación

```bash
python cli/main_cli.py config
```

## 📖 Uso

### Crear una tarea

```bash
python cli/main_cli.py create "Crear una función para calcular factorial en Python"
```

### Crear tarea y guardar archivos

```bash
python cli/main_cli.py create "Crear una API REST para gestión de usuarios" --output ./output
```

### Ver estado de una tarea

```bash
python cli/main_cli.py status task_abc123
```

### Listar tareas

```bash
# Todas las tareas
python cli/main_cli.py list

# Solo completadas
python cli/main_cli.py list --status completed

# Limitar resultados
python cli/main_cli.py list --limit 5
```

### Ver logs de auditoría

```bash
python cli/main_cli.py logs task_abc123
```

## 🔄 Flujo de Trabajo

1. **Arquitecto**: Convierte requerimiento → Blueprint TOON
2. **Sentinel**: Calcula risk score (0-100)
3. **Routing**: Auto/Peer/Human según riesgo
4. **Coder**: Genera código Python
5. **Linter**: Analiza calidad
6. **Tester**: Genera tests unitarios
7. **Auditor**: Registra todo el proceso

## 📊 Niveles de Riesgo

- **🟢 0-30 (Auto-Approve)**: Automatización completa
- **🟡 31-70 (Peer Review)**: Revisión por IA
- **🔴 71-100 (Human Approval)**: Requiere aprobación humana

## 📁 Estructura de Salida

```
output/
├── src/
│   ├── services/
│   │   └── user_service.py
│   ├── repositories/
│   │   └── user_repository.py
│   └── dtos/
│       └── user_dto.py
└── tests/
    └── test_user.py
```

## 🧪 Ejemplos

### Ejemplo 1: Función Simple

```bash
python cli/main_cli.py create "Crear una función que valide emails" -o ./output
```

**Resultado**:
- Risk score: ~25 (bajo)
- Archivos: 2-3 archivos Python
- Tests: 3-5 tests unitarios
- Tiempo: ~30 segundos

### Ejemplo 2: API REST

```bash
python cli/main_cli.py create "Crear una API REST con FastAPI para gestión de tareas (CRUD)" -o ./output
```

**Resultado**:
- Risk score: ~45 (medio)
- Archivos: 6-8 archivos Python
- Tests: 10-15 tests
- Tiempo: ~60 segundos

### Ejemplo 3: Sistema de Pagos

```bash
python cli/main_cli.py create "Crear un sistema de procesamiento de pagos con Stripe" -o ./output
```

**Resultado**:
- Risk score: ~85 (alto)
- Archivos: 10+ archivos
- Tests: 20+ tests
- Tiempo: ~90 segundos
- ⚠️ Requiere aprobación humana (simulada en MVP)

## 🔍 Troubleshooting

### Error: "DEEPSEEK_API_KEY no configurada"

Solución: Verifica que el archivo `.env` existe y contiene la API key.

### Error: "Database locked"

Solución: Cierra otras instancias del CLI que puedan estar usando la base de datos.

### Error: "Module not found"

Solución: Asegúrate de ejecutar desde el directorio `agentes/`:

```bash
cd agentes
python cli/main_cli.py ...
```

## 📝 Notas

- **MVP**: Esta es una versión MVP enfocada en demostrar viabilidad
- **Lenguajes**: Solo Python por ahora (JavaScript en desarrollo)
- **Visual Verifier**: No incluido en MVP
- **Notificaciones**: Solo por consola (email/slack en roadmap)

## 🚀 Próximos Pasos

1. Ejecutar tests: `pytest tests/`
2. Ver ejemplos en `examples/`
3. Leer documentación completa en `docs/`

## 📞 Soporte

Para más información, consulta:
- `resumen_framework.md` - Especificación completa
- `implementation_plan.md` - Plan de implementación
- `ARQUITECTURA_AGENTES_COMPLETA.md` - Arquitectura detallada

---

**Versión**: 1.0.0-mvp  
**Fecha**: Noviembre 2024
