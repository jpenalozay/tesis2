# 🚀 Guía de Setup: Gitea + Framework

## 📋 Resumen

Esta guía te ayudará a configurar Gitea como Document Store para el framework multi-agente con flujo GitOps completo.

## 🎯 ¿Por qué Gitea?

1. **GitOps Nativo**: Los agentes trabajan con Git, no con wikis
2. **Pull Requests**: Sistema de criticidad con revisión antes de merge
3. **Webhooks Instantáneos**: Latencia mínima para eventos
4. **Escrito en Go**: Homogéneo con la infraestructura
5. **Ligero**: Solo 10-20MB RAM vs 200MB+ de alternativas

## 🔧 Paso 1: Levantar Infraestructura

```bash
cd agentes/docker
docker-compose -f docker-compose.infra.yml up -d

# Verificar que Gitea esté corriendo
docker ps | grep gitea
```

## 🌐 Paso 2: Configurar Gitea (Primera vez)

1. **Abrir Gitea**: http://localhost:3000

2. **Instalación Inicial**:
   - Database Type: **PostgreSQL**
   - Host: **postgres:5432**
   - Username: **postgres**
   - Password: **postgres**
   - Database Name: **gitea**
   - Server Domain: **localhost**
   - HTTP Port: **3000**
   - Application URL: **http://localhost:3000/**

3. **Crear Usuario Admin**:
   - Username: `admin`
   - Password: `admin123` (cámbialo después)
   - Email: `admin@localhost`

4. **Crear Organización**:
   - Click en "+" → "New Organization"
   - Name: `framework`
   - Visibility: Private

## 🔑 Paso 3: Generar Token de API

1. **Settings** → **Applications** → **Generate New Token**
2. **Token Name**: `framework-api`
3. **Permissions**: Seleccionar:
   - `repo` (all)
   - `admin:repo_hook` (all)
   - `admin:org` (all)
4. **Generate Token** → Copiar el token

## 📁 Paso 4: Crear Repositorio de Documentos

1. **Organization `framework`** → **New Repository**
2. **Repository Name**: `docs-architecture`
3. **Description**: "Architecture documents for multi-agent framework"
4. **Visibility**: Private
5. **Initialize**: ✅ Initialize with README
6. **Default Branch**: `main`
7. **Create Repository**

## 📝 Paso 5: Crear Estructura de Documentos

Crear los siguientes archivos en el repo `docs-architecture`:

```
docs-architecture/
├── README.md
├── SRS/
│   └── requirements.md
├── HLD/
│   ├── architecture.md
│   └── tech-stack.md
├── ADR/
│   └── 001-use-gitea.md
├── DATA/
│   ├── erd.md
│   └── redis-schema.md
├── API/
│   └── openapi.yaml
└── LLD/
    └── components.md
```

## ⚙️ Paso 6: Configurar Framework

Editar `agentes/config/go_services.yaml`:

```yaml
gitea:
  base_url: "http://localhost:3000"
  token: "TU_TOKEN_AQUI"  # Token generado en Paso 3
  owner: "framework"
  repo: "docs-architecture"
  webhook_url: "http://host.docker.internal:8080/api/webhooks/gitea"
```

## 🚀 Paso 7: Iniciar Servicios Go

```bash
cd agentes

# Compilar
go build -o bin/framework go/cmd/main.go

# Ejecutar
./bin/framework

# O en desarrollo
go run go/cmd/main.go
```

Deberías ver:
```
🚀 Starting Framework Go Services...
Connecting to NATS...
Connecting to Redis and Postgres...
Connecting to Gitea...
Setting up event subscriptions...
Starting HTTP server on port 8080...
🚀 Server starting on :8080
```

## 🔗 Paso 8: Verificar Webhook

El framework automáticamente creará el webhook en Gitea. Para verificar:

1. **Gitea** → **framework/docs-architecture** → **Settings** → **Webhooks**
2. Deberías ver un webhook apuntando a: `http://host.docker.internal:8080/api/webhooks/gitea`
3. **Events**: `push`, `pull_request`

## 🧪 Paso 9: Probar el Flujo GitOps

### Test 1: Editar Documento (Push Directo)

1. **Gitea** → **docs-architecture** → **SRS/requirements.md**
2. **Edit** → Cambiar algo → **Commit Changes**
3. **Ver logs del framework**:
   ```
   📝 Push event: Push to refs/heads/main by admin (1 commits)
   ✅ Published document.updated event: <uuid>
   ```

### Test 2: Pull Request (Flujo de Revisión)

1. **Gitea** → **docs-architecture** → **New Branch**: `feature/update-srs`
2. **Editar** SRS/requirements.md en la nueva rama
3. **Create Pull Request**:
   - Title: "Update SRS: Add new requirement"
   - Base: `main`
   - Head: `feature/update-srs`
4. **Ver logs del framework**:
   ```
   🔍 PR event: opened - PR #1: Update SRS: Add new requirement (feature/update-srs -> main)
   ✅ Published document.review_requested event: <uuid>
   ```
5. **Merge PR** → Ver logs:
   ```
   ✅ Merge event: PR #1: Update SRS: Add new requirement
   ✅ Published document.approved event: <uuid>
   ```

## 📊 Paso 10: Verificar Eventos

### Ver estadísticas:
```bash
curl http://localhost:8080/api/stats
```

### Ver eventos en NATS:
```bash
# Instalar NATS CLI
go install github.com/nats-io/natscli/nats@latest

# Ver streams
nats stream list

# Ver eventos
nats stream view EVENTS
```

### Ver estado en Redis:
```bash
redis-cli
> KEYS *
> GET task:<task-id>
```

## 🔄 Flujo Completo de GitOps

```
┌─────────────────────────────────────────────────────────┐
│  1. Humano edita SRS.md en Gitea                        │
│     - Opción A: Commit directo a main (solo admin)     │
│     - Opción B: Nueva rama + Pull Request (recomendado)│
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. Gitea dispara Webhook                               │
│     - Event: pull_request.opened                        │
│     - Payload: PR info, changed files                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. Go Server recibe webhook                            │
│     - Parsea evento                                     │
│     - Publica a NATS: document.review_requested         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. Agente Sentinel (Python) despierta                  │
│     - Lee cambios desde Gitea API                       │
│     - Calcula riesgo del cambio                         │
│     - Genera recomendaciones                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  5. Decisión de Aprobación                              │
│     - Riesgo BAJO: Auto-merge                           │
│     - Riesgo MEDIO: Peer review                         │
│     - Riesgo ALTO: Human approval                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  6. PR Merged (Gitea)                                   │
│     - Webhook: pull_request.closed + merged=true        │
│     - Go Server publica: document.approved              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  7. Agente Coordinador reacciona                        │
│     - Detecta que SRS cambió                            │
│     - Busca código afectado                             │
│     - Crea tarea: "Refactorizar según nuevo SRS"        │
│     - Despierta Agente Coder                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  8. Ciclo se repite                                     │
│     - Coder genera código                               │
│     - Crea PR en repo de código                         │
│     - Webhook dispara tests                             │
│     - ...                                               │
└─────────────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Error: "Webhook delivery failed"
```bash
# Verificar que el servidor Go esté corriendo
curl http://localhost:8080/health

# Verificar conectividad desde Gitea
docker exec -it framework-gitea sh
wget -O- http://host.docker.internal:8080/health
```

### Error: "Failed to create webhook"
- El webhook ya existe (normal)
- O el token no tiene permisos `admin:repo_hook`

### Error: "401 Unauthorized" en Gitea API
- Token inválido o expirado
- Regenerar token en Gitea UI

### Webhook no dispara eventos
1. **Gitea** → **Webhooks** → Click en el webhook → **Recent Deliveries**
2. Ver el payload y la respuesta
3. Si hay error 500, revisar logs del servidor Go

## 📚 Próximos Pasos

1. ✅ Gitea configurado y funcionando
2. ⏳ Implementar Agente Reviewer (Python)
3. ⏳ Conectar Coordinador Python con eventos de Gitea
4. ⏳ Crear templates de documentos (SRS, HLD, etc.)
5. ⏳ Implementar flujo completo de aprobación

## 🎓 Recursos

- [Gitea API Docs](https://docs.gitea.io/en-us/api-usage/)
- [Gitea Webhooks](https://docs.gitea.io/en-us/webhooks/)
- [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream)

---

**¿Listo para probar?** Ejecuta `docker-compose up -d` y sigue los pasos! 🚀
