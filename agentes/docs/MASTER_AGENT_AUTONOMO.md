# 🤖 MASTER AGENT AUTÓNOMO - ANÁLISIS Y CREACIÓN AUTOMÁTICA DE AGENTES

**Proyecto**: Sistema Multi-Agente Autónomo  
**Fecha**: 2025-01-XX  
**Objetivo**: Master Agent que analiza proyectos nuevos y crea agentes automáticamente

---

## 🎯 OBJETIVO

Crear un **Master Agent completamente autónomo** que pueda:
1. ✅ Analizar un proyecto nuevo desde cero
2. ✅ Entender estructura completa (entidades, funciones, backend, frontend, BD)
3. ✅ Guardar conocimiento en formato optimizado (más rápido que MD)
4. ✅ Crear automáticamente agentes especializados
5. ✅ Configurar cada agente con reglas y archivos a monitorear
6. ✅ Funcionar independientemente sin intervención humana

---

## 📊 FLUJO COMPLETO DEL MASTER AGENT

```
┌─────────────────────────────────────────────────────────────┐
│                    PROYECTO NUEVO LLEGA                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          MASTER AGENT: ANÁLISIS COMPLETO                    │
│  • Escanea estructura de carpetas                          │
│  • Analiza código Python (AST parsing)                      │
│  • Detecta modelos de datos                                │
│  • Identifica endpoints y APIs                             │
│  • Encuentra templates y frontend                           │
│  • Detecta servicios externos                              │
│  • Analiza dependencias                                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│      GUARDAR CONOCIMIENTO EN FORMATO OPTIMIZADO             │
│  • JSON estructurado (más rápido que MD)                    │
│  • Redis para acceso rápido                                │
│  • Archivos para persistencia                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│     MASTER AGENT: CREAR AGENTES ESPECIALIZADOS              │
│  • Detecta qué agentes necesita el proyecto                │
│  • Crea configuración de cada agente                       │
│  • Define archivos a monitorear                            │
│  • Establece reglas y validaciones                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              SISTEMA LISTO PARA OPERAR                      │
│  • Agentes especializados creados                           │
│  • Configuración completa                                   │
│  • Listo para recibir requerimientos                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 FASE 1: ANÁLISIS COMPLETO DEL PROYECTO

### 1.1 Escaneo de Estructura

```python
# scripts/agents/master_analyzer.py

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class ProjectAnalyzer:
    """Analiza un proyecto completo y extrae toda la información"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.knowledge = {
            "project_structure": {},
            "entities": [],
            "functions": [],
            "endpoints": [],
            "models": [],
            "services": [],
            "templates": [],
            "static_files": [],
            "dependencies": {},
            "patterns": {}
        }
    
    def analyze_complete(self) -> Dict[str, Any]:
        """Análisis completo del proyecto"""
        
        # 1. Estructura de carpetas
        self._analyze_structure()
        
        # 2. Archivos Python
        self._analyze_python_files()
        
        # 3. Modelos de datos
        self._analyze_data_models()
        
        # 4. Endpoints y APIs
        self._analyze_endpoints()
        
        # 5. Frontend
        self._analyze_frontend()
        
        # 6. Servicios externos
        self._analyze_services()
        
        # 7. Dependencias
        self._analyze_dependencies()
        
        # 8. Patrones detectados
        self._detect_patterns()
        
        return self.knowledge
    
    def _analyze_structure(self):
        """Analiza estructura de carpetas"""
        structure = {}
        
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.project_path)
            
            structure[str(relative_path)] = {
                "type": "directory",
                "files": [f.name for f in root_path.iterdir() if f.is_file()],
                "subdirs": [d.name for d in root_path.iterdir() if d.is_dir()]
            }
        
        self.knowledge["project_structure"] = structure
    
    def _analyze_python_files(self):
        """Analiza archivos Python usando AST"""
        python_files = list(self.project_path.rglob("*.py"))
        
        for py_file in python_files:
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                
                analyzer = PythonFileAnalyzer(py_file, tree)
                file_info = analyzer.analyze()
                
                self.knowledge["functions"].extend(file_info["functions"])
                self.knowledge["entities"].extend(file_info["classes"])
                
            except Exception as e:
                print(f"Error analizando {py_file}: {e}")
    
    def _analyze_data_models(self):
        """Detecta modelos de datos"""
        models = []
        
        # Buscar archivos que probablemente contengan modelos
        model_patterns = ["**/models/**/*.py", "**/model*.py", "**/schema*.py"]
        
        for pattern in model_patterns:
            for model_file in self.project_path.rglob(pattern):
                if "__pycache__" in str(model_file):
                    continue
                
                try:
                    with open(model_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    model_analyzer = ModelAnalyzer(model_file, tree)
                    models.extend(model_analyzer.extract_models())
                    
                except Exception as e:
                    continue
        
        self.knowledge["models"] = models
    
    def _analyze_endpoints(self):
        """Detecta endpoints de APIs"""
        endpoints = []
        
        # Buscar frameworks de API
        api_files = []
        for pattern in ["**/main.py", "**/app.py", "**/api/**/*.py", "**/routes/**/*.py"]:
            api_files.extend(self.project_path.rglob(pattern))
        
        for api_file in api_files:
            if "__pycache__" in str(api_file):
                continue
            
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar FastAPI
                if "@app." in content or "from fastapi" in content:
                    endpoint_analyzer = FastAPIAnalyzer(api_file, content)
                    endpoints.extend(endpoint_analyzer.extract_endpoints())
                
                # Detectar Flask
                elif "@app.route" in content or "from flask" in content:
                    endpoint_analyzer = FlaskAnalyzer(api_file, content)
                    endpoints.extend(endpoint_analyzer.extract_endpoints())
                
            except Exception as e:
                continue
        
        self.knowledge["endpoints"] = endpoints
    
    def _analyze_frontend(self):
        """Analiza frontend"""
        templates = []
        static_files = []
        
        # Templates HTML
        for template_file in self.project_path.rglob("**/*.html"):
            templates.append({
                "path": str(template_file.relative_to(self.project_path)),
                "type": "html_template",
                "size": template_file.stat().st_size
            })
        
        # CSS
        for css_file in self.project_path.rglob("**/*.css"):
            static_files.append({
                "path": str(css_file.relative_to(self.project_path)),
                "type": "css",
                "size": css_file.stat().st_size
            })
        
        # JavaScript
        for js_file in self.project_path.rglob("**/*.js"):
            static_files.append({
                "path": str(js_file.relative_to(self.project_path)),
                "type": "javascript",
                "size": js_file.stat().st_size
            })
        
        self.knowledge["templates"] = templates
        self.knowledge["static_files"] = static_files
    
    def _analyze_services(self):
        """Detecta servicios externos"""
        services = []
        
        # Buscar archivos de servicios
        for service_file in self.project_path.rglob("**/services/**/*.py"):
            if "__pycache__" in str(service_file):
                continue
            
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar OpenAI
                if "openai" in content.lower() or "OpenAI" in content:
                    services.append({
                        "type": "openai",
                        "file": str(service_file.relative_to(self.project_path))
                    })
                
                # Detectar WhatsApp
                if "whatsapp" in content.lower():
                    services.append({
                        "type": "whatsapp",
                        "file": str(service_file.relative_to(self.project_path))
                    })
                
                # Detectar Email
                if "smtp" in content.lower() or "email" in content.lower():
                    services.append({
                        "type": "email",
                        "file": str(service_file.relative_to(self.project_path))
                    })
                
            except Exception as e:
                continue
        
        self.knowledge["services"] = services
    
    def _analyze_dependencies(self):
        """Analiza dependencias"""
        dependencies = {}
        
        # requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                dependencies["python"] = deps
        
        # package.json (si existe)
        pkg_file = self.project_path / "package.json"
        if pkg_file.exists():
            import json
            with open(pkg_file, 'r') as f:
                pkg_data = json.load(f)
                dependencies["node"] = pkg_data.get("dependencies", {})
        
        self.knowledge["dependencies"] = dependencies
    
    def _detect_patterns(self):
        """Detecta patrones arquitectónicos"""
        patterns = {
            "framework": None,
            "orm": None,
            "template_engine": None,
            "api_style": None,
            "auth_method": None
        }
        
        # Detectar framework
        if (self.project_path / "requirements.txt").exists():
            with open(self.project_path / "requirements.txt", 'r') as f:
                content = f.read()
                if "fastapi" in content:
                    patterns["framework"] = "fastapi"
                elif "flask" in content:
                    patterns["framework"] = "flask"
                elif "django" in content:
                    patterns["framework"] = "django"
        
        # Detectar ORM
        if "sqlalchemy" in str(self.knowledge["dependencies"]):
            patterns["orm"] = "sqlalchemy"
        elif "django" in str(self.knowledge["dependencies"]):
            patterns["orm"] = "django_orm"
        
        # Detectar template engine
        if any("jinja2" in str(f) for f in self.knowledge["templates"]):
            patterns["template_engine"] = "jinja2"
        
        self.knowledge["patterns"] = patterns
```

---

## 💾 FASE 2: GUARDAR CONOCIMIENTO EN FORMATO OPTIMIZADO

### Formato Recomendado: **JSON + Redis**

**Por qué JSON y no MD:**
- ✅ Parseo 10x más rápido
- ✅ Estructura verificable
- ✅ Acceso directo a datos específicos
- ✅ Fácil de consultar programáticamente

**Estructura del Knowledge Base:**

```python
# scripts/agents/knowledge_manager.py

import json
import redis
from pathlib import Path
from typing import Dict, Any

class KnowledgeManager:
    """Gestor del conocimiento del proyecto"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.knowledge_file = Path(".agents/knowledge/project_knowledge.json")
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_knowledge(self, knowledge: Dict[str, Any]):
        """Guarda conocimiento en JSON y Redis"""
        
        # 1. Guardar en archivo JSON (persistencia)
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2)
        
        # 2. Guardar en Redis (acceso rápido)
        if self.redis:
            # Guardar conocimiento completo
            self.redis.set(
                "project:knowledge:complete",
                json.dumps(knowledge),
                ex=86400  # TTL 24 horas
            )
            
            # Guardar índices para acceso rápido
            self._create_indexes(knowledge)
    
    def _create_indexes(self, knowledge: Dict[str, Any]):
        """Crea índices en Redis para acceso rápido"""
        
        # Índice de entidades
        if "entities" in knowledge:
            for entity in knowledge["entities"]:
                self.redis.hset(
                    "project:entities:index",
                    entity["name"],
                    json.dumps(entity)
                )
        
        # Índice de endpoints
        if "endpoints" in knowledge:
            for endpoint in knowledge["endpoints"]:
                key = f"project:endpoints:{endpoint['method']}:{endpoint['path']}"
                self.redis.set(key, json.dumps(endpoint), ex=86400)
        
        # Índice de modelos
        if "models" in knowledge:
            for model in knowledge["models"]:
                self.redis.hset(
                    "project:models:index",
                    model["name"],
                    json.dumps(model)
                )
        
        # Índice de archivos por tipo
        file_types = defaultdict(list)
        if "project_structure" in knowledge:
            for path, info in knowledge["project_structure"].items():
                for file in info.get("files", []):
                    ext = Path(file).suffix
                    file_types[ext].append(path)
        
        for ext, paths in file_types.items():
            self.redis.sadd(f"project:files:{ext}", *paths)
```

---

## 🤖 FASE 3: CREAR AGENTES AUTOMÁTICAMENTE

### 3.1 Detectar Qué Agentes Necesita el Proyecto

```python
# scripts/agents/agent_creator.py

class AgentCreator:
    """Crea agentes especializados basándose en el análisis del proyecto"""
    
    def __init__(self, knowledge: Dict[str, Any]):
        self.knowledge = knowledge
        self.agents_config = {}
    
    def create_agents(self) -> Dict[str, Dict]:
        """Crea configuración de agentes necesarios"""
        
        agents = {}
        
        # Agente DB (si hay modelos de datos)
        if self.knowledge.get("models") or self._has_database_files():
            agents["db"] = self._create_db_agent()
        
        # Agente Backend (si hay endpoints)
        if self.knowledge.get("endpoints"):
            agents["backend"] = self._create_backend_agent()
        
        # Agente Frontend (si hay templates)
        if self.knowledge.get("templates") or self.knowledge.get("static_files"):
            agents["frontend"] = self._create_frontend_agent()
        
        # Agente OpenAI (si hay integración OpenAI)
        if self._has_service("openai"):
            agents["openai"] = self._create_openai_agent()
        
        # Agente WhatsApp (si hay integración WhatsApp)
        if self._has_service("whatsapp"):
            agents["whatsapp"] = self._create_whatsapp_agent()
        
        # Agente Performance (siempre necesario)
        agents["performance"] = self._create_performance_agent()
        
        # Agente Tests (siempre necesario)
        agents["tests"] = self._create_tests_agent()
        
        # Agente Code Quality (siempre necesario)
        agents["code_quality"] = self._create_code_quality_agent()
        
        return agents
    
    def _create_db_agent(self) -> Dict:
        """Crea configuración del agente DB"""
        model_files = []
        migration_files = []
        
        # Encontrar archivos de modelos
        for model in self.knowledge.get("models", []):
            model_files.append(model["file"])
        
        # Buscar migraciones SQL
        for pattern in ["**/migrations/**/*.sql", "**/migrations/**/*.py"]:
            migration_files.extend(list(Path(".").rglob(pattern)))
        
        return {
            "name": "db",
            "type": "database",
            "enabled": True,
            "monitored_files": {
                "patterns": [
                    "**/models/**/*.py",
                    "**/database/**/*.py",
                    "**/migrations/**/*.sql"
                ],
                "specific": model_files
            },
            "monitored_directories": [
                "app/models",
                "app/database",
                "sql/migrations"
            ],
            "rules": {
                "validate_normalization": True,
                "check_indexes": True,
                "validate_relations": True,
                "check_migrations": True
            },
            "actions": [
                "validate_model",
                "check_migrations",
                "optimize_queries",
                "suggest_indexes"
            ]
        }
    
    def _create_backend_agent(self) -> Dict:
        """Crea configuración del agente Backend"""
        api_files = []
        endpoint_files = []
        
        # Encontrar archivos con endpoints
        for endpoint in self.knowledge.get("endpoints", []):
            api_files.append(endpoint["file"])
        
        # Buscar archivos principales de API
        for pattern in ["**/main.py", "**/app.py", "**/api/**/*.py"]:
            endpoint_files.extend([str(p) for p in Path(".").rglob(pattern)])
        
        return {
            "name": "backend",
            "type": "api",
            "enabled": True,
            "monitored_files": {
                "patterns": [
                    "**/main.py",
                    "**/app.py",
                    "**/api/**/*.py",
                    "**/routes/**/*.py",
                    "**/webapp/**/*.py"
                ],
                "specific": list(set(api_files + endpoint_files))
            },
            "monitored_directories": [
                "app",
                "app/webapp",
                "app/api"
            ],
            "rules": {
                "validate_endpoints": True,
                "check_security": True,
                "validate_data": True,
                "check_error_handling": True
            },
            "actions": [
                "validate_endpoint",
                "check_security",
                "validate_data",
                "check_error_handling"
            ],
            "framework": self.knowledge["patterns"].get("framework", "unknown")
        }
    
    def _create_frontend_agent(self) -> Dict:
        """Crea configuración del agente Frontend"""
        template_files = [t["path"] for t in self.knowledge.get("templates", [])]
        static_files = [s["path"] for s in self.knowledge.get("static_files", [])]
        
        return {
            "name": "frontend",
            "type": "ui",
            "enabled": True,
            "monitored_files": {
                "patterns": [
                    "**/*.html",
                    "**/*.css",
                    "**/*.js"
                ],
                "specific": template_files + static_files
            },
            "monitored_directories": [
                "app/webapp/templates",
                "app/webapp/static"
            ],
            "rules": {
                "validate_html": True,
                "check_accessibility": True,
                "validate_css": True,
                "check_responsive": True
            },
            "actions": [
                "validate_html",
                "check_accessibility",
                "optimize_css",
                "validate_javascript"
            ],
            "template_engine": self.knowledge["patterns"].get("template_engine")
        }
    
    def _has_service(self, service_name: str) -> bool:
        """Verifica si el proyecto tiene un servicio específico"""
        services = self.knowledge.get("services", [])
        return any(s.get("type") == service_name for s in services)
    
    def _has_database_files(self) -> bool:
        """Verifica si hay archivos de base de datos"""
        db_patterns = ["**/models/**/*.py", "**/database/**/*.py", "**/*.sql"]
        return any(Path(".").rglob(pattern) for pattern in db_patterns)
```

---

## 🚀 FASE 4: CONFIGURACIÓN COMPLETA

### Guardar Configuración de Agentes

```python
# scripts/agents/master_agent.py

class MasterAgent:
    """Master Agent autónomo que analiza y configura proyectos"""
    
    def __init__(self, project_path: str, redis_client=None):
        self.project_path = Path(project_path)
        self.redis = redis_client
        self.analyzer = ProjectAnalyzer(project_path)
        self.knowledge_manager = KnowledgeManager(redis_client)
        self.agent_creator = None
    
    def initialize_project(self):
        """Inicializa un proyecto nuevo completamente"""
        
        print("🔍 Fase 1: Analizando proyecto completo...")
        knowledge = self.analyzer.analyze_complete()
        
        print("💾 Fase 2: Guardando conocimiento...")
        self.knowledge_manager.save_knowledge(knowledge)
        
        print("🤖 Fase 3: Creando agentes especializados...")
        self.agent_creator = AgentCreator(knowledge)
        agents_config = self.agent_creator.create_agents()
        
        print("⚙️ Fase 4: Configurando agentes...")
        self._configure_agents(agents_config)
        
        print("✅ Proyecto inicializado correctamente!")
        print(f"   📊 Agentes creados: {len(agents_config)}")
        print(f"   📁 Archivos analizados: {self._count_files()}")
        print(f"   🗄️ Modelos detectados: {len(knowledge.get('models', []))}")
        print(f"   🔌 Endpoints detectados: {len(knowledge.get('endpoints', []))}")
        
        return {
            "knowledge": knowledge,
            "agents": agents_config
        }
    
    def _configure_agents(self, agents_config: Dict):
        """Configura todos los agentes creados"""
        
        # Guardar configuración en archivos
        config_dir = Path(".agents/config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        for agent_name, agent_config in agents_config.items():
            # Guardar en archivo JSON
            config_file = config_dir / f"{agent_name}_config.json"
            with open(config_file, 'w') as f:
                json.dump(agent_config, f, indent=2)
            
            # Guardar en Redis para acceso rápido
            if self.redis:
                self.redis.hset(
                    "agents:config",
                    agent_name,
                    json.dumps(agent_config)
                )
        
        # Guardar configuración maestra
        master_config = {
            "project_path": str(self.project_path),
            "agents": list(agents_config.keys()),
            "created_at": datetime.now().isoformat()
        }
        
        master_config_file = config_dir / "master_config.json"
        with open(master_config_file, 'w') as f:
            json.dump(master_config, f, indent=2)
```

---

## 📋 ESTRUCTURA DE ARCHIVOS GENERADA

```
.agents/
├── knowledge/
│   └── project_knowledge.json    # Conocimiento completo del proyecto
│
├── config/
│   ├── master_config.json        # Configuración maestra
│   ├── db_config.json            # Config del agente DB
│   ├── backend_config.json       # Config del agente Backend
│   ├── frontend_config.json     # Config del agente Frontend
│   └── ...
│
└── agents/
    ├── db/
    │   └── rules.json            # Reglas específicas del agente DB
    ├── backend/
    │   └── rules.json
    └── ...
```

---

## 🎯 USO DEL MASTER AGENT

### Ejemplo de Uso

```python
# scripts/agents/initialize_project.py

from master_agent import MasterAgent
import redis

# Inicializar Redis (opcional)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Crear Master Agent
master = MasterAgent(project_path=".", redis_client=redis_client)

# Inicializar proyecto completo
result = master.initialize_project()

print("\n📊 Resumen:")
print(f"   Agentes creados: {len(result['agents'])}")
print(f"   Modelos detectados: {len(result['knowledge']['models'])}")
print(f"   Endpoints detectados: {len(result['knowledge']['endpoints'])}")
```

---

## ✅ VENTAJAS DEL ENFOQUE AUTÓNOMO

1. **Análisis Completo**: Entiende TODO el proyecto automáticamente
2. **Sin Configuración Manual**: No requiere intervención humana
3. **Adaptativo**: Se adapta a cualquier tipo de proyecto
4. **Rápido**: Análisis completo en segundos
5. **Escalable**: Funciona con proyectos pequeños o grandes

---

## 🚀 PRÓXIMOS PASOS

1. Implementar `ProjectAnalyzer` completo
2. Implementar `KnowledgeManager` con Redis
3. Implementar `AgentCreator` automático
4. Crear `MasterAgent` principal
5. Testing con proyectos reales

---

**Autor**: Composer AI  
**Fecha**: 2025-01-XX  
**Versión**: 1.0

