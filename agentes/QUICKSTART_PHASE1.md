# Framework Multi-Agente - Guía de Setup Rápido (Fase 1)

## 🚀 Inicio Rápido

### 1. Levantar Infraestructura

```bash
# Levantar servicios (NATS, Redis, Postgres, MinIO)
cd agentes/docker
docker-compose -f docker-compose.infra.yml up -d

# Verificar que todos los servicios estén corriendo
docker-compose -f docker-compose.infra.yml ps
```

### 2. Instalar Dependencias Go

```bash
cd agentes
go mod tidy
go mod download
```

### 3. Compilar Servicios Go

```bash
# Compilar todos los servicios
cd go
go build -o ../bin/eventbus ./eventbus
go build -o ../bin/state ./state
go build -o ../bin/docstore ./docstore
```

### 4. Ejecutar Tests

```bash
# Tests unitarios
go test ./... -v

# Tests con coverage
go test ./... -cover -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## 📊 Verificar Servicios

### NATS
```bash
# Monitoring UI
open http://localhost:8222

# CLI
nats stream list
```

### Redis
```bash
# CLI
redis-cli ping
# Debería responder: PONG
```

### PostgreSQL
```bash
# CLI
psql -h localhost -U postgres -d framework
# Password: postgres
```

### MinIO
```bash
# Console UI
open http://localhost:9001
# User: minioadmin
# Pass: minioadmin
```

## 🧪 Tests de Integración

```bash
# Test Event Bus
go test ./go/eventbus -v

# Test State Manager
go test ./go/state -v

# Test Document Store
go test ./go/docstore -v
```

## 📝 Próximos Pasos

1. ✅ Infraestructura levantada
2. ⏳ Implementar gRPC server
3. ⏳ Crear cliente Python para gRPC
4. ⏳ Tests de integración Python ↔ Go
5. ⏳ Benchmarks de performance

## 🔧 Troubleshooting

### Error: "Cannot connect to Docker daemon"
```bash
# Iniciar Docker Desktop
# O en Linux:
sudo systemctl start docker
```

### Error: "Port already in use"
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :4222  # Windows
lsof -i :4222                 # Linux/Mac

# Detener servicios existentes
docker-compose -f docker-compose.infra.yml down
```

### Error: "go: module not found"
```bash
# Limpiar caché de Go
go clean -modcache
go mod tidy
go mod download
```

## 📚 Documentación

- [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream)
- [Redis](https://redis.io/docs/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [MinIO](https://min.io/docs/minio/linux/index.html)
- [gRPC Go](https://grpc.io/docs/languages/go/)
