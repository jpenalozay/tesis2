# 🚀 Framework Multi-Agente v2.5

> **Plataforma de desarrollo de software automatizada con IA multi-agente, supervisión humana jerárquica y auditoría completa.**

---

## 📚 Documentación Completa

**⚠️ IMPORTANTE**: Para entender completamente este proyecto, lee:

### 📘 [PROYECTO_COMPLETO.md](docs/PROYECTO_COMPLETO.md)

Este documento contiene **TODA** la información necesaria para:
- ✅ Entender la arquitectura completa
- ✅ Configurar el entorno
- ✅ Ejecutar el sistema
- ✅ Continuar el desarrollo
- ✅ Troubleshooting

**Tamaño**: 1000+ líneas  
**Secciones**: 13 capítulos completos  
**Propósito**: Manual de transferencia para otra IA o desarrollador

---

## ⚡ Quick Start

### 1. Levantar Infraestructura

```bash
cd docker
docker-compose -f docker-compose.infra.yml up -d
```

### 2. Configurar Gitea (Primera vez)

1. Abrir http://localhost:3000
2. Completar instalación inicial
3. Crear organización `framework`
4. Crear repositorio `docs-architecture`
5. Generar token de API
6. Actualizar `config/go_services.yaml` con el token

### 3. Compilar y Ejecutar Go Services

```bash
go build -o bin/framework go/cmd/main.go
./bin/framework  # o bin\framework.exe en Windows
```

### 4. Probar MVP Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

pip install -r requirements.txt
python cli/main_cli.py create "Crear API REST para usuarios" --output ./output
```

---

## 📊 Estado del Proyecto

| Fase | Estado | Completado |
|------|--------|------------|
| **Fase 0: MVP Python** | ✅ | 100% |
| **Fase 1: Infraestructura Go** | ✅ | 85% |
| **Fase 2: Migración a Go** | ⏳ | 0% |
| **Fase 3: Optimización** | ⏳ | 0% |
| **Fase 4: Testing** | ⏳ | 30% |
| **Fase 5: Deployment** | ⏳ | 0% |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│  PYTHON (50%) - Agentes IA              │
│  Coordinador, Arquitecto, Sentinel,     │
│  Coder, Linter, Tester, Reviewer        │
└─────────────────────────────────────────┘
              ↓ gRPC (futuro)
┌─────────────────────────────────────────┐
│  GO (50%) - Infraestructura             │
│  Event Bus, State Manager, Gitea,       │
│  HTTP Server, Webhooks                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  DOCKER - Servicios                     │
│  NATS, Redis, Postgres, Gitea           │
└─────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
agentes/
├── docs/
│   └── PROYECTO_COMPLETO.md    ⭐ LEER PRIMERO
├── python/                      # Agentes IA
│   ├── core/
│   ├── implementations/
│   └── cli/
├── go/                          # Infraestructura
│   ├── cmd/
│   ├── eventbus/
│   ├── state/
│   ├── gitea/
│   └── server/
├── docker/
│   └── docker-compose.infra.yml
├── config/
│   ├── framework_config.yaml
│   └── go_services.yaml
└── scripts/
    ├── setup_gitea.bat
    └── test_phase1.bat
```

---

## 🎯 Decisiones Arquitectónicas Clave

### ¿Por qué Python + Go? (No Rust)

- **Python (50%)**: Agentes IA, integración LLM, lógica de negocio
- **Go (50%)**: Infraestructura, Event Bus, State Manager, Webhooks
- **Rust eliminado**: Solo 5-10% mejor que Go, complejidad no justificada

### ¿Por qué Gitea? (No MinIO)

- ✅ Git nativo (commits, branches, PRs)
- ✅ Webhooks instantáneos (<10ms)
- ✅ Pull Requests para sistema de criticidad
- ✅ Escrito en Go (homogéneo)
- ✅ 10-20MB RAM vs 200MB+ de MinIO

### ¿Por qué NATS JetStream?

- ✅ 11M msgs/sec (110x más rápido que Redis Streams)
- ✅ Latencia <1ms p99
- ✅ At-least-once delivery
- ✅ Clustering nativo

---

## 🔧 Configuración

### Variables de Entorno (`.env`)

```bash
DEEPSEEK_API_KEY=sk-477fe86ab91e40d6809f25da6b4769ac
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DATABASE_PATH=./data/framework.db
```

### Servicios Docker

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| NATS | 4222, 8222 | Event Bus |
| Redis | 6379 | Estado caliente |
| Postgres | 5432 | Estado frío |
| Gitea | 3000 | Document Store |
| Framework | 8080 | HTTP Server |

---

## 🧪 Testing

```bash
# Go tests
go test ./go/... -v

# Python tests
pytest tests/ -v

# Integration tests
scripts\test_phase1.bat  # Windows
bash scripts/test_phase1.sh  # Linux/Mac
```

---

## 📖 Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| [PROYECTO_COMPLETO.md](docs/PROYECTO_COMPLETO.md) | ⭐ Manual completo (LEER PRIMERO) |
| [SETUP_GITEA.md](SETUP_GITEA.md) | Guía de setup de Gitea |
| [README_MVP.md](README_MVP.md) | Guía de usuario del MVP |
| [resumen_framework.md](resumen_framework.md) | Especificación técnica v2.5 |

---

## 🚀 Próximos Pasos

1. ⏳ Implementar gRPC server (Go)
2. ⏳ Cliente Python para gRPC
3. ⏳ Conectar agentes Python con Event Bus Go
4. ⏳ Tests end-to-end completos
5. ⏳ Deployment con Kubernetes

---

## 🆘 Troubleshooting

Ver sección 12 de [PROYECTO_COMPLETO.md](docs/PROYECTO_COMPLETO.md#12-troubleshooting)

**Problemas comunes**:
- Docker no está corriendo → Iniciar Docker Desktop
- Puerto en uso → `docker-compose down`
- Webhook falla → Verificar `curl http://localhost:8080/health`

---

## 📞 Soporte

- **Documentación completa**: `docs/PROYECTO_COMPLETO.md`
- **API Key DeepSeek**: `sk-477fe86ab91e40d6809f25da6b4769ac`
- **Gitea**: http://localhost:3000

---

**Versión**: 2.5.0  
**Estado**: Fase 1 completada al 85%  
**Última actualización**: 2024-12-02
