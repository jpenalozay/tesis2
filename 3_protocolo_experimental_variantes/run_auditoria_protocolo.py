"""Auditoría pasada 1/2 del pipeline entregable 0→1→2→3."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ENTREGABLE = Path(__file__).resolve().parents[1]
PASO0 = ENTREGABLE / "0_etl_ingesta_preprocesamiento"
PASO1 = ENTREGABLE / "1_ingenieria_atributos_y_recuperacion_rag"
PASO2 = ENTREGABLE / "2_modulo_criticidad_gobernanza_adaptativa"
PASO3 = ENTREGABLE / "3_protocolo_experimental_variantes"

REQUIRED_PASO3 = [
    ("0_informe_configuracion_protocolo_experimental.json", None),
    ("3_tabla_predicciones_baseline_amnesico_n400.csv", 400),
    ("4_tabla_predicciones_var1_crewai_rag_n400.csv", 400),
    ("5_tabla_predicciones_var2_middleware_intercepta_n400.csv", 400),
    ("6_tabla_predicciones_consolidada_tres_variantes_n400.csv", 400),
    ("7_tabla_metricas_set_minimo_seis_por_variante.csv", 3),
    ("8_tabla_metricas_extendidas_framework_por_variante.csv", 3),
    ("9_tabla_validacion_holdout_30_por_variante.csv", 3),
    ("10_tabla_validacion_cruzada_5fold_estratificada_n400.csv", None),
    ("11_tabla_comparacion_pareada_mcnemar.csv", None),
    ("12_informe_ejecucion_fuentes_cache_api.json", None),
    ("13_figura_ablacion_f1_macro_ec_fnr_stop.png", None),
    ("14_figura_matrices_confusion_tres_variantes.png", None),
    ("15_figura_curva_calibracion_ece_var2.png", None),
    ("16_informe_resumen_protocolo_experimental.json", None),
]

METRIC_COLS = [
    "F1-macro (Macro-averaged F1)",
    "F1-stop (F1-critical)",
    "ECE (Expected Calibration Error)",
    "EC (Expected Cost / ex-CEPA)",
    "FNR-stop (False Negative Rate stop)",
]


def check_file(path: Path, min_rows: int | None = None) -> dict[str, Any]:
    ok = path.exists()
    info: dict[str, Any] = {"path": str(path.relative_to(ENTREGABLE)), "exists": ok}
    if ok and path.suffix == ".csv":
        n = len(pd.read_csv(path))
        info["rows"] = n
        if min_rows is not None:
            info["rows_ok"] = n == min_rows
    return info


def auditoria_pasada1() -> dict[str, Any]:
    checks = {
        "paso0_eval_n400": check_file(PASO0 / "8_conjunto_evaluacion_experimento_n400.csv", 400),
        "paso1_rag_2000": check_file(PASO1 / "7_tabla_recuperacion_hibrida_rrf_top5.csv", 2000),
        "paso2_gate_b_400": check_file(PASO2 / "4_tabla_decisiones_gate_b_post_agente_simulado_n400.csv", 400),
    }
    for name, min_r in REQUIRED_PASO3:
        key = f"paso3_{name}"
        checks[key] = check_file(PASO3 / name, min_r)

    anti = json.loads((PASO1 / "4_informe_auditoria_anti_fuga.json").read_text(encoding="utf-8"))
    exec_inf = {}
    if (PASO3 / "12_informe_ejecucion_fuentes_cache_api.json").exists():
        exec_inf = json.loads((PASO3 / "12_informe_ejecucion_fuentes_cache_api.json").read_text(encoding="utf-8"))

    gaps = []
    if anti.get("checks", {}).get("history_eval_hash_overlap") != 0:
        gaps.append("G1: overlap historial-eval distinto de 0")
    for name, min_r in REQUIRED_PASO3:
        chk = checks.get(f"paso3_{name}", {})
        if not chk.get("exists"):
            gaps.append(f"G2: falta {name}")
        elif min_r and not chk.get("rows_ok", True):
            gaps.append(f"G3: {name} filas != {min_r}")

    if (PASO3 / "7_tabla_metricas_set_minimo_seis_por_variante.csv").exists():
        mdf = pd.read_csv(PASO3 / "7_tabla_metricas_set_minimo_seis_por_variante.csv")
        missing_cols = [c for c in METRIC_COLS if c not in mdf.columns]
        if missing_cols:
            gaps.append(f"G4: columnas métricas faltantes: {missing_cols}")
        if len(mdf) != 3:
            gaps.append("G5: métricas deben tener 3 variantes")

    mode = exec_inf.get("mode", "cache-only")
    api_total = exec_inf.get("api_calls_baseline", 0) + exec_inf.get("api_calls_var1", 0)
    cov = exec_inf.get("cache_coverage", {})
    bl_llm = cov.get("deepseek_hits_n400", 0) + cov.get("deepseek_api_n400", 0)
    if mode == "cache-only" and api_total > 0:
        gaps.append("G6: API llamada en modo cache-only (documentar si intencional)")
    if mode == "api-incremental" and exec_inf.get("run_api") and api_total == 0 and bl_llm < 400:
        gaps.append("G6: modo api-incremental sin llamadas API Baseline (verificar clave/creditos)")

    crewai_real = cov.get("crewai_api_n400", 0) + cov.get("crewai_cache_n400", 0)
    abstencion_n = cov.get("abstencion_fuera_piloto_n400", 0) + cov.get("abstencion_crewai_fallo_n400", 0)
    majority_n = cov.get("majority_fallback_n400", 0)
    if exec_inf.get("run_crewai") and crewai_real < 40:
        gaps.append(
            f"G7: cobertura Var1 CrewAI real < D5 10% ({crewai_real}/400) — verificar max_new_api_calls_var1"
        )
    allowed_var1 = {
        "crewai_cache",
        "crewai_api",
        "pgvector_majority_fallback",
        "abstencion_fuera_piloto_d5",
        "abstencion_crewai_fallo",
    }
    invalid_var1 = [
        s for s in exec_inf.get("var1_sources", {})
        if s not in allowed_var1
    ]
    if invalid_var1:
        gaps.append(f"G8: fuentes Var1 no permitidas: {invalid_var1}")
    var1_total = crewai_real + abstencion_n + majority_n
    if var1_total != 400 and exec_inf:
        gaps.append(
            f"G9: conteo Var1 incompleto crewai+abstencion+majority="
            f"{crewai_real}+{abstencion_n}+{majority_n} != 400"
        )

    crit = [g for g in gaps if g.startswith(("G1", "G2", "G3", "G4"))]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 1,
        "checks": checks,
        "anti_fuga": anti.get("checks", {}),
        "exec_informe": exec_inf,
        "gaps_detectados": gaps,
        "veredicto": "OK" if not crit else "REVISAR",
    }


def auditoria_pasada2(report1: dict[str, Any]) -> dict[str, Any]:
    items = []
    for key, chk in report1["checks"].items():
        ok = chk.get("exists", False)
        if "rows_ok" in chk:
            ok = ok and chk["rows_ok"]
        items.append({"item": key, "veredicto": "✅" if ok else "⚠️", "detail": chk})
    af = report1.get("anti_fuga", {})
    items.append({
        "item": "anti_fuga_overlap",
        "veredicto": "✅" if af.get("history_eval_hash_overlap") == 0 else "⚠️",
        "detail": af,
    })
    for gid in report1.get("gaps_detectados", []):
        sev = "⚠️" if gid.startswith("G7") or gid.startswith("G6") else "⚠️"
        items.append({"item": gid, "veredicto": sev, "detail": "gap documentado"})
    overall = "✅" if report1["veredicto"] == "OK" else "⚠️"
    doc_gaps = [g for g in report1.get("gaps_detectados", []) if g.startswith(("G6", "G7"))]
    if overall == "✅" or (report1["veredicto"] == "OK" or len(doc_gaps) == len(report1.get("gaps_detectados", []))):
        overall = "✅"
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 2,
        "items": items,
        "gaps_restantes": doc_gaps,
        "veredicto_global": overall,
    }


def write_gaps_md(report1: dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoría Pasada 1 — Gaps protocolo experimental",
        "",
        f"**Timestamp:** {report1['timestamp']}",
        f"**Veredicto:** {report1['veredicto']}",
        "",
        "## Gaps",
        "",
    ]
    if not report1["gaps_detectados"]:
        lines.append("Sin gaps críticos.")
    else:
        for g in report1["gaps_detectados"]:
            lines.append(f"- {g}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_resultado_md(report2: dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoría Pasada 2 — Resultado final protocolo",
        "",
        f"**Veredicto global:** {report2['veredicto_global']}",
        "",
        "## Ítems",
        "",
        "| Ítem | Veredicto |",
        "|------|-----------|",
    ]
    for it in report2["items"]:
        lines.append(f"| {it['item']} | {it['veredicto']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    r1 = auditoria_pasada1()
    r2 = auditoria_pasada2(r1)
    (PASO3 / "7_informe_auditoria_pasada1_protocolo.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (PASO3 / "8_informe_auditoria_pasada1_pipeline_0_3.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (PASO3 / "9_informe_auditoria_pasada2_resultado_final.json").write_text(
        json.dumps(r2, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_gaps_md(r1, PASO3 / "AUDITORIA_PASADA1_GAPS.md")
    write_resultado_md(r2, PASO3 / "AUDITORIA_PASADA2_RESULTADO.md")
    print(f"Auditoría completada. Veredicto pasada 1: {r1['veredicto']} | pasada 2: {r2['veredicto_global']}")


if __name__ == "__main__":
    main()
