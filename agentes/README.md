# Código del framework (`agentes/`)

La documentación **principal para revisión del curso / tribunal** está en el **[`README.md` en la raíz del repositorio](../README.md)**.

## Qué usar para la línea de criticidad (tesis)

| Ruta | Rol |
|------|-----|
| [`core/early_gate.py`](core/early_gate.py) | Gate temprano `play` / `pausa` / `stop` (LLM + léxico). |
| [`core/llm_client_v3.py`](core/llm_client_v3.py) | Cliente DeepSeek (`DEEPSEEK_API_KEY`). |
| [`core/coordinator_v3_gated.py`](core/coordinator_v3_gated.py) | Orquestador que adjunta la salida del gate. |
| [`core/coordinator_v3.py`](core/coordinator_v3.py) | Pipeline completo multi-agente (Arquitecto, Sentinel, etc.). |

Dependencias Python adicionales: [`requirements.txt`](requirements.txt). El resto del directorio (`implementations/`, `config/`, etc.) soporta el pipeline completo del framework.
