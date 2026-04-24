# gRPC Communication Layer - Setup Guide

## 📦 Componentes Implementados

### 1. Proto Definitions (`proto/services.proto`)
- Definiciones completas de servicios y mensajes
- 4 servicios principales:
  - `ProcessRequirement` - Procesar requerimiento completo
  - `GetTaskStatus` - Obtener estado de tarea
  - `ListTasks` - Listar tareas recientes
  - `GetAuditLogs` - Obtener logs de auditoría

### 2. Python gRPC Server (`core/grpc_server.py`)
- Servidor gRPC que expone el framework
- Integración con Coordinator v3
- Manejo de audit logs
- Cache de tareas en memoria

### 3. Go gRPC Client (`go/grpc/client.go`)
- Cliente Go para comunicarse con Python
- Métodos para todos los servicios
- Manejo de errores y timeouts
- Ejemplo de uso incluido

---

## 🚀 Setup e Instalación

### Prerequisitos

**Python:**
```bash
pip install grpcio grpcio-tools
```

**Go:**
```bash
go get -u google.golang.org/grpc
go get -u google.golang.org/protobuf
```

### Compilar Proto Files

**Para Python:**
```bash
cd agentes
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=. \
  --grpc_python_out=. \
  proto/services.proto
```

Esto genera:
- `services_pb2.py` - Mensajes
- `services_pb2_grpc.py` - Servicios

**Para Go:**
```bash
cd agentes
protoc \
  --go_out=. \
  --go_opt=paths=source_relative \
  --go-grpc_out=. \
  --go-grpc_opt=paths=source_relative \
  proto/services.proto
```

Esto genera:
- `proto/services.pb.go` - Mensajes
- `proto/services_grpc.pb.go` - Servicios

---

## 🏃 Ejecutar

### 1. Iniciar Servidor Python

```bash
cd agentes
python core/grpc_server.py
```

Output esperado:
```
INFO:root:gRPC Servicer initialized
INFO:root:gRPC server started on port 50051
```

### 2. Ejecutar Cliente Go

```bash
cd agentes/go/grpc
go run client.go
```

Output esperado:
```
Conectando al framework...
✓ Conectado al framework

Procesando requerimiento...
======================================================================
RESULTADO DEL FRAMEWORK
======================================================================
Task ID: abc123...
Status: completed
Time: 15234ms

RESUMEN:
  Arquitectura: calculator (3 componentes)
  Riesgo: 35.0 (LOW) - auto_approve
  Tests: 8/10 passed (85% coverage)
  Calidad: 92.5/100 (3 issues)
======================================================================

✓ Completado
```

---

## 📡 API Reference

### ProcessRequirement

Procesa un requerimiento completo a través de todos los agentes.

**Request:**
```protobuf
message RequirementRequest {
  string requirement = 1;
  map<string, string> context = 2;
  bool enable_peer_review = 3;
  bool enable_executable_feedback = 4;
}
```

**Response:**
```protobuf
message ProcessResult {
  string task_id = 1;
  string status = 2;
  int64 total_time_ms = 3;
  Summary summary = 12;
  string error = 13;
}
```

**Ejemplo Go:**
```go
result, err := client.ProcessRequirement(
    ctx,
    "Crear una calculadora",
    nil,
    true,  // peer review
    true,  // executable feedback
)
```

### GetTaskStatus

Obtiene el estado actual de una tarea.

**Request:**
```protobuf
message TaskStatusRequest {
  string task_id = 1;
}
```

**Response:**
```protobuf
message TaskStatus {
  string task_id = 1;
  string status = 2;
  int32 progress_percent = 3;
  string current_agent = 4;
  int64 elapsed_time_ms = 5;
}
```

**Ejemplo Go:**
```go
status, err := client.GetTaskStatus(ctx, taskID)
fmt.Printf("Status: %s (%d%%)\n", status.Status, status.ProgressPercent)
```

### ListTasks

Lista tareas recientes.

**Request:**
```protobuf
message ListTasksRequest {
  int32 limit = 1;
  int32 offset = 2;
}
```

**Response:**
```protobuf
message TaskList {
  repeated TaskInfo tasks = 1;
  int32 total = 2;
}
```

**Ejemplo Go:**
```go
tasks, err := client.ListTasks(ctx, 10, 0)
for _, task := range tasks.Tasks {
    fmt.Printf("%s: %s\n", task.TaskId, task.Status)
}
```

### GetAuditLogs

Obtiene logs de auditoría.

**Request:**
```protobuf
message AuditLogsRequest {
  string task_id = 1;
  int32 limit = 2;
}
```

**Response:**
```protobuf
message AuditLogs {
  repeated AuditEvent events = 1;
  int32 total = 2;
}
```

**Ejemplo Go:**
```go
logs, err := client.GetAuditLogs(ctx, taskID, 100)
for _, event := range logs.Events {
    fmt.Printf("%s: %s.%s\n", event.Timestamp, event.Actor, event.Action)
}
```

---

## 🔧 Configuración Avanzada

### Cambiar Puerto

**Python Server:**
```python
serve(port=50052)  # Default: 50051
```

**Go Client:**
```go
client, err := NewClient("localhost:50052")
```

### Agregar Autenticación

**Python Server:**
```python
import grpc

# Crear credenciales SSL
server_credentials = grpc.ssl_server_credentials(
    [(private_key, certificate_chain)]
)

server.add_secure_port(f'[::]:{port}', server_credentials)
```

**Go Client:**
```go
import "google.golang.org/grpc/credentials"

creds, err := credentials.NewClientTLSFromFile("cert.pem", "")
conn, err := grpc.Dial(
    address,
    grpc.WithTransportCredentials(creds),
)
```

### Timeouts

**Go Client:**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

result, err := client.ProcessRequirement(ctx, ...)
```

---

## 🧪 Testing

### Test Python Server

```python
# test_grpc_server.py
import grpc
import services_pb2
import services_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = services_pb2_grpc.AgentFrameworkStub(channel)

request = services_pb2.RequirementRequest(
    requirement="Test requirement",
    enable_peer_review=False,
    enable_executable_feedback=False
)

response = stub.ProcessRequirement(request)
print(f"Task ID: {response.task_id}")
print(f"Status: {response.status}")
```

### Test Go Client

```go
// Incluido en client.go main()
go run client.go
```

---

## 📊 Performance

### Benchmarks Esperados

- **Latencia:** ~50-100ms (sin procesamiento)
- **Throughput:** ~100 req/s (servidor Python single-threaded)
- **Tamaño Mensaje:** ~1-10KB (comprimido con protobuf)

### Optimizaciones

1. **Connection Pooling:**
```go
// Reusar conexiones
var globalClient *Client

func GetClient() *Client {
    if globalClient == nil {
        globalClient, _ = NewClient("localhost:50051")
    }
    return globalClient
}
```

2. **Streaming (Futuro):**
```protobuf
rpc ProcessRequirementStream(RequirementRequest) returns (stream ProcessUpdate);
```

---

## 🐛 Troubleshooting

### Error: "module 'docker' has no attribute 'from_env'"

**Solución:** Instalar docker SDK correcto
```bash
pip install docker
```

### Error: "proto files not compiled"

**Solución:** Compilar proto files
```bash
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. proto/services.proto
```

### Error: "connection refused"

**Solución:** Verificar que el servidor esté corriendo
```bash
# Terminal 1
python core/grpc_server.py

# Terminal 2
go run go/grpc/client.go
```

---

## 📚 Referencias

- [gRPC Python](https://grpc.io/docs/languages/python/)
- [gRPC Go](https://grpc.io/docs/languages/go/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)

---

**Versión:** 1.0  
**Última Actualización:** 3 de Diciembre de 2024
