# Docker Compose para Sistema de Agentes

Este directorio contiene la configuración Docker Compose para los servicios necesarios para el sistema de agentes.

## Servicios

- **Redis**: Comunicación en tiempo real entre agentes
- **Redis Commander**: Interface web para administrar Redis (opcional)

## Uso

```bash
# Solo Redis
docker-compose up -d redis

# Redis + Redis Commander
docker-compose --profile tools up -d
```

Ver `README.md` para documentación completa.
