# 🤖 Implementaciones de Agentes

Este directorio contiene las implementaciones Python de todos los agentes con tracking automático de métricas.

## 📁 Estructura

```
agentes/implementations/
├── __init__.py                 # Exports de todos los agentes
├── openai_agent.py            # OpenAI Agent
├── db_agent.py                # DB Agent
├── performance_agent.py        # Performance Agent
├── backend_agent.py            # Backend Agent
├── frontend_agent.py          # Frontend Agent
├── whatsapp_agent.py          # WhatsApp Agent
├── code_quality_agent.py      # Code Quality Agent
├── tests_agent.py             # Tests Agent
└── master_agent.py            # Master Agent
```

## 🚀 Uso Básico

### Ejemplo 1: OpenAI Agent

```python
from agentes.implementations import OpenAIAgent

# Inicializar agente
agent = OpenAIAgent()

# Validar integración (trackea métricas automáticamente)
result = agent.validate_integration()
print(f"Status: {result['status']}")
print(f"Métricas: {result['metrics']}")

# Optimizar prompt
result = agent.optimize_prompts("This is a long prompt that needs optimization")
print(f"Tokens saved: {result['tokens_saved']:.2f}")

# Monitorear costos
result = agent.monitor_costs(tokens_used=1500)
print(f"Cost: ${result['cost_usd']:.4f}")
```

### Ejemplo 2: DB Agent

```python
from agentes.implementations import DBAgent

# Inicializar agente
agent = DBAgent()

# Validar modelo
result = agent.validate_model("app/backend/models/current.py")
print(f"Status: {result['status']}")

# Ejecutar query (trackea tiempo automáticamente)
result = agent.execute_query("SELECT * FROM users LIMIT 10")
print(f"Query time: {result['query_time_ms']:.2f}ms")

# Analizar performance
result = agent.analyze_performance()
print(f"Avg query time: {result['avg_query_time_ms']:.2f}ms")
```

### Ejemplo 3: Master Agent - Agregación de Métricas

```python
from agentes.implementations import MasterAgent

# Inicializar Master Agent
master = MasterAgent()

# Recopilar métricas de un agente específico
result = master.collect_agent_metrics("openai")
print(f"OpenAI metrics: {result['metrics']}")

# Recopilar métricas de todos los agentes
result = master.collect_all_agents_metrics()
print(f"Total cost: ${result['aggregated_metrics']['totals']['total_cost_usd']:.2f}")
print(f"Total executions: {result['aggregated_metrics']['totals']['total_executions']}")

# Generar reporte consolidado
report = master.generate_cost_time_report()
print(f"Report ID: {report['report_id']}")
print(f"Report saved to: agentes/reports/master_agent_cost_time_reports/")
```

## 📊 Tracking de Métricas

Todos los agentes trackean automáticamente:

### Métricas Estándar
- **Tiempo de ejecución**: Tiempo total de ejecución en ms
- **Tiempo CPU**: Tiempo de CPU utilizado en ms
- **Memoria**: Memoria utilizada en MB
- **Costos**: Costo en USD (si aplica)
- **Operaciones**: Número de operaciones realizadas

### Métricas Personalizadas
Cada agente tiene métricas específicas de su dominio. Ver la documentación de cada agente.

## 🔄 Publicación de Métricas

Las métricas se publican automáticamente a:

1. **Redis**: Canal `agent:{agent_id}:metrics`
2. **Archivos JSON**: `agentes/data/metrics/{agent_id}_metrics_{date}.json`

## 📝 Ejemplos de Métricas Generadas

### OpenAI Agent
```json
{
  "agent_id": "openai",
  "execution_id": "openai_20250115143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "execution_time_ms": 250.5,
  "cpu_time_ms": 180.2,
  "memory_mb": 128.5,
  "cost_usd": 0.003,
  "success": true,
  "operations_count": 1,
  "custom_metrics": {
    "tokens_used": 1500,
    "api_calls": 1,
    "prompt_tokens": 1050,
    "completion_tokens": 450
  }
}
```

### DB Agent
```json
{
  "agent_id": "db",
  "execution_id": "db_20250115143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "execution_time_ms": 150.3,
  "cost_usd": null,
  "success": true,
  "operations_count": 1,
  "custom_metrics": {
    "queries_executed": 1,
    "query_time_ms": 50.2,
    "avg_query_time_ms": 50.2,
    "db_operations": 1
  }
}
```

## 🧪 Testing

Cada agente tiene una función `main()` para testing:

```bash
# Ejecutar tests individuales
python -m agentes.implementations.openai_agent
python -m agentes.implementations.db_agent
python -m agentes.implementations.master_agent

# O ejecutar directamente
python agentes/implementations/openai_agent.py
```

## 📚 Documentación Adicional

- Especificaciones de agentes: `agentes/specs/agents/`
- Biblioteca de métricas: `agentes/core/metrics_tracker.py`
- Análisis de tracking: `docs/ANALISIS_TRACKING_COSTOS_TIEMPOS.md`

## 🔧 Configuración

La configuración de cada agente se carga desde:
- `agentes/specs/agents/{agent_id}_agent.json`

Se puede especificar una ruta personalizada:
```python
agent = OpenAIAgent(config_path="ruta/personalizada/config.json")
```

## 📊 Agregación de Métricas

El Master Agent usa `MetricsAggregator` para consolidar métricas:

```python
from agentes.core import MetricsAggregator

aggregator = MetricsAggregator()

# Métricas diarias de un agente
metrics = aggregator.aggregate_daily_metrics("openai", "2025-01-15")
print(f"Total cost: ${metrics['total_cost_usd']:.2f}")
print(f"Success rate: {metrics['success_rate']:.2%}")

# Métricas de todos los agentes
all_metrics = aggregator.aggregate_all_agents_metrics(
    ["db", "backend", "openai"],
    "2025-01-15"
)
```

## ✅ Estado de Implementación

- ✅ OpenAI Agent - Implementado con tracking completo
- ✅ DB Agent - Implementado con tracking completo
- ✅ Performance Agent - Implementado con tracking completo
- ✅ Backend Agent - Implementado con tracking completo
- ✅ Frontend Agent - Implementado con tracking completo
- ✅ WhatsApp Agent - Implementado con tracking completo
- ✅ Code Quality Agent - Implementado con tracking completo
- ✅ Tests Agent - Implementado con tracking completo
- ✅ Master Agent - Implementado con agregación completa

## 🚀 Próximos Pasos

1. Integrar con sistema de file watchers
2. Configurar schedulers para ejecución automática
3. Crear dashboard de visualización de métricas
4. Implementar alertas basadas en métricas
5. Optimización usando datos históricos de métricas

