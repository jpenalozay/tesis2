# 📂 FILE WATCHERS - Documentación Completa

## 🎯 Objetivo

Sistema de file watchers que monitorea automáticamente los archivos del proyecto y activa los agentes correspondientes cuando se detectan cambios en archivos monitoreados según la configuración de cada agente.

---

## 📦 Instalación

### Requisito: Biblioteca watchdog

```bash
pip install watchdog
```

O agregar a `requirements.txt`:

```
watchdog>=3.0.0
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│     FileWatcherManager (Manager)        │
│  - Carga configuraciones de agentes     │
│  - Gestiona múltiples watchers          │
│  - Coordina observers                   │
└─────────────────────────────────────────┘
           │
           ├─────────────────┬──────────────┐
           │                 │              │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌───▼──────┐
    │ DB Watcher  │  │Backend      │  │Frontend  │
    │             │  │Watcher      │  │Watcher   │
    │ - Patterns  │  │ - Patterns  │  │ - Patterns│
    │ - Triggers  │  │ - Triggers  │  │ - Triggers│
    │ - Debounce  │  │ - Debounce  │  │ - Debounce│
    └──────┬──────┘  └──────┬──────┘  └───┬──────┘
           │                 │              │
           └─────────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │  File Changes  │
                    │  (watchdog)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Activation      │
                    │ Callback        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Agent Execution │
                    │ (validate, etc) │
                    └─────────────────┘
```

---

## 📋 Componentes Principales

### 1. `FileWatcherManager`

Gestor centralizado que:
- Carga configuraciones de todos los agentes
- Crea watchers individuales para cada agente
- Gestiona observers de watchdog
- Proporciona interfaz unificada

**Uso**:
```python
from agentes.core.file_watcher import FileWatcherManager

manager = FileWatcherManager()
manager.setup_all_watchers()
manager.start()
```

### 2. `AgentFileWatcher`

Watcher individual para un agente específico:
- Monitorea archivos según configuración
- Implementa debounce
- Verifica exclusiones
- Llama al callback de activación

### 3. `AgentFileConfig`

Dataclass con configuración de monitoreo:
- `patterns`: Patrones glob de archivos
- `specific_files`: Archivos específicos
- `exclude_patterns`: Patrones a excluir
- `directories`: Directorios a monitorear
- `triggers`: Eventos que activan (created, modified, deleted)
- `debounce_ms`: Tiempo de espera entre activaciones

### 4. `activate_agent_on_file_change`

Función que activa el agente apropiado:
- Determina qué función ejecutar según tipo de archivo
- Crea instancia del agente si no existe
- Ejecuta la función correspondiente
- Maneja errores y logging

---

## 🔧 Configuración de Agentes

Cada agente configura su monitoreo en su archivo JSON:

```json
{
  "agent_id": "backend",
  "monitoring": {
    "files": {
      "patterns": [
        "app/backend/**/*.py"
      ],
      "specific": [
        "app/main.py"
      ],
      "exclude": [
        "**/__pycache__/**",
        "**/*.pyc"
      ]
    },
    "directories": [
      "app/backend"
    ],
    "triggers": {
      "on_file_modified": true,
      "on_file_created": true,
      "on_file_deleted": false,
      "debounce_ms": 2000
    }
  }
}
```

### Patrones Soportados

- `**/*.py` - Todos los archivos Python recursivamente
- `app/backend/**/*.py` - Python en backend y subdirectorios
- `app/main.py` - Archivo específico
- `**/__pycache__/**` - Excluir directorios

### Triggers

- `on_file_modified` / `file_modified`: Activar al modificar
- `on_file_created` / `file_created`: Activar al crear
- `on_file_deleted` / `file_deleted`: Activar al eliminar
- `debounce_ms`: Milisegundos de espera entre activaciones (default: 2000)

---

## 🚀 Uso

### Ejecución Simple

```bash
# Desde el directorio raíz del proyecto
python -m agentes.watchers.main
```

### Uso Programático Básico

```python
from agentes.core.agent_activation import start_file_watchers

# Iniciar todos los watchers
manager = start_file_watchers()

# Los watchers corren en segundo plano
# Detener con Ctrl+C o:
manager.stop()
```

### Uso Programático Avanzado

```python
from agentes.core.file_watcher import FileWatcherManager

# Crear gestor personalizado
manager = FileWatcherManager(
    specs_dir="agentes/specs/agents",
    root_dir="/ruta/al/proyecto"
)

# Callback personalizado
def mi_callback(agent_id: str, file_path: str):
    print(f"Cambio detectado: {file_path}")
    print(f"Activando agente: {agent_id}")
    # Tu lógica personalizada aquí

manager.set_activation_callback(mi_callback)
manager.setup_all_watchers()
manager.start()

# Mantener ejecución
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    manager.stop()
```

---

## 📊 Comportamiento por Agente

### DB Agent
- **Archivos `.py` en `models/`** → Ejecuta `validate_model()`
- **Archivos `.py` en `database/`** → Ejecuta `validate_model()`
- **Archivos `.sql`** → Solo notifica (no ejecuta validación)

### Backend Agent
- **Archivos `.py` en `backend/`** → Ejecuta `validate_code()`

### Frontend Agent
- **Archivos `.html`** → Ejecuta `validate_html()`
- **Archivos `.css`** → Ejecuta `validate_css()`
- **Archivos `.js`** → Ejecuta `validate_javascript()`

### Performance Agent
- **Archivos `.py`** → Ejecuta `analyze_performance()`

### OpenAI Agent
- **Archivos relacionados con OpenAI** → Ejecuta `validate_integration()`

### WhatsApp Agent
- **Archivos relacionados con WhatsApp** → Ejecuta `validate_integration()`

### Code Quality Agent
- **Archivos `.py`** → Ejecuta `validate_pep8()`

### Tests Agent
- **Archivos de test** → Solo notifica (no ejecuta tests automáticamente)

### Master Agent
- **Cualquier cambio** → Coordina con otros agentes

---

## 🔍 Logging

El sistema produce logs detallados:

```
2025-01-15 14:30:22 - watcher.db - INFO - 📁 Archivo creado: app/backend/models/new_model.py -> Activando db
2025-01-15 14:30:22 - agentes.activation - INFO - 🔄 Activando db por cambio en: app/backend/models/new_model.py
2025-01-15 14:30:23 - agentes.activation - INFO - ✅ DB Agent: Validación de modelo completada
2025-01-15 14:30:23 - agentes.activation - INFO - ✅ Agente db procesado exitosamente
```

### Niveles de Log

- **INFO**: Actividades normales (archivos detectados, agentes activados)
- **DEBUG**: Detalles técnicos (directorios monitoreados, patrones verificados)
- **WARNING**: Advertencias (directorios no encontrados, agentes deshabilitados)
- **ERROR**: Errores (errores de ejecución, callbacks fallidos)

---

## ⚙️ Personalización

### Cambiar Callback de Activación

```python
from agentes.core.file_watcher import FileWatcherManager

def mi_callback_personalizado(agent_id: str, file_path: str):
    # Tu lógica personalizada
    print(f"Personalizado: {agent_id} -> {file_path}")
    # Ejecutar agente manualmente, enviar notificación, etc.

manager = FileWatcherManager()
manager.set_activation_callback(mi_callback_personalizado)
manager.setup_all_watchers()
manager.start()
```

### Monitorear Solo Algunos Agentes

```python
from agentes.core.file_watcher import FileWatcherManager

manager = FileWatcherManager()

# Cargar solo configuración de DB Agent
db_config = manager.load_agent_config("db")
if db_config:
    manager.setup_watcher("db", db_config)

manager.start()
```

---

## 🐛 Troubleshooting

### "watchdog no instalado"

```bash
pip install watchdog
```

### "No se configuraron watchers"

**Causas posibles**:
1. Los archivos JSON de configuración no existen
2. Los agentes tienen `"enabled": false`
3. Los directorios monitoreados no existen

**Solución**:
```python
# Verificar configuraciones cargadas
from agentes.core.file_watcher import FileWatcherManager

manager = FileWatcherManager()
configs = manager.load_all_agent_configs()
print(f"Configuraciones cargadas: {len(configs)}")
for agent_id, config in configs.items():
    print(f"  - {agent_id}: {len(config.patterns)} patrones")
```

### "Agente no se activa"

**Verificar**:
1. Los patrones en `monitoring.files.patterns` coinciden con el archivo
2. Los triggers están habilitados (`on_file_modified: true`)
3. El archivo no está en exclusiones
4. El debounce no está bloqueando (esperar 2 segundos mínimo)

**Debug**:
```python
from agentes.core.file_watcher import AgentFileWatcher, AgentFileConfig

# Verificar si un archivo sería monitoreado
config = AgentFileConfig(
    agent_id="test",
    patterns=["app/**/*.py"],
    specific_files=[],
    exclude_patterns=["**/__pycache__/**"],
    directories=["app"],
    triggers={"on_file_modified": True}
)

watcher = AgentFileWatcher("test", config, lambda a, f: None)
print(watcher._should_monitor_file("app/backend/test.py"))  # True
print(watcher._should_monitor_file("app/__pycache__/test.pyc"))  # False
```

### "Múltiples activaciones del mismo archivo"

**Causa**: El debounce no está funcionando correctamente

**Solución**: Aumentar `debounce_ms` en la configuración del agente:

```json
{
  "triggers": {
    "debounce_ms": 5000  // Esperar 5 segundos entre activaciones
  }
}
```

---

## 📈 Performance

- **Memoria**: ~1-2 MB por watcher activo
- **CPU**: Mínimo, solo cuando hay cambios de archivos
- **Eficiencia**: Usa eventos nativos del sistema operativo (watchdog)
- **Escalabilidad**: Puede monitorear miles de archivos sin problemas

---

## 🔒 Seguridad

- Solo monitorea archivos locales
- No ejecuta código externo
- Los callbacks deben ser confiables
- Validación de rutas para evitar directory traversal

---

## ✅ Verificación

### Verificar que el Sistema Funciona

```python
# Test básico
from agentes.core.file_watcher import FileWatcherManager

manager = FileWatcherManager()
configs = manager.load_all_agent_configs()

print(f"✅ Configuraciones cargadas: {len(configs)}")
for agent_id in configs.keys():
    print(f"  - {agent_id}")

# Verificar que watchdog está disponible
from agentes.core.file_watcher import WATCHDOG_AVAILABLE
print(f"✅ Watchdog disponible: {WATCHDOG_AVAILABLE}")
```

---

## 📚 Ejemplos Completos

Ver `agentes/watchers/main.py` para ejemplo completo de ejecución.

---

**Última actualización**: 2025-01-15  
**Versión**: 1.0
