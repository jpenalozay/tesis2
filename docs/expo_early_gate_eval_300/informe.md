# Informe — EarlyGate vs gold (`casos_gold_criticidad_v2`)

- **Muestras:** 300
- **Tiempo total:** 696.6 s (delay 0.35s entre casos)
- **Accuracy:** 0.7900
- **F1-macro:** 0.7669
- **Cohen κ:** 0.6850

## F1 por clase

| Clase | F1 |
|-------|-----|
| play | 0.7605 |
| pausa | 0.5401 |
| stop | 1.0000 |

## Segunda pasada — precisión / recall / soporte por clase

| Clase | Precisión | Recall | Soporte |
|-------|-----------|--------|---------|
| play | 0.6135 | 1.0000 | 100 |
| pausa | 1.0000 | 0.3700 | 100 |
| stop | 1.0000 | 1.0000 | 100 |

## Segunda pasada — acierto por `source`

| Fuente | n | correctos | accuracy |
|--------|---|-----------|----------|
| `llm` | 298 | 235 | 0.7886 |
| `llm_fallback` | 1 | 1 | 1.0000 |
| `lexical` | 1 | 1 | 1.0000 |

## Matriz de confusión (filas=gold, columnas=pred)

```
[[100   0   0]
 [ 63  37   0]
 [  0   0 100]]
```

## Nota metodológica

ROC-AUC multiclase omitido: EarlyGate no entrega un vector de probabilidad por clase; F1 y κ son las métricas centrales del informe.
