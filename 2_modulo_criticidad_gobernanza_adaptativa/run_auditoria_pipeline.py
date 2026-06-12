"""Auditoría pasada 1/2 del pipeline entregable 0→1→2."""

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
        "paso0_lab_n400": check_file(PASO0 / "4_muestra_laboratorio_n400.csv", 400),
        "paso1_rag_2000": check_file(PASO1 / "7_tabla_recuperacion_hibrida_rrf_top5.csv", 2000),
        "paso1_anti_fuga": check_file(PASO1 / "4_informe_auditoria_anti_fuga.json"),
        "paso2_senales_400": check_file(PASO2 / "2_tabla_senales_por_ticket_n400.csv", 400),
        "paso2_gate_a_400": check_file(PASO2 / "3_tabla_decisiones_politica_play_pausa_stop_n400.csv", 400),
        "paso2_gate_b_400": check_file(PASO2 / "4_tabla_decisiones_gate_b_post_agente_simulado_n400.csv", 400),
        "paso2_metricas": check_file(PASO2 / "6_tabla_metricas_modulo_criticidad_capa_a.csv"),
    }
    anti = json.loads((PASO1 / "4_informe_auditoria_anti_fuga.json").read_text(encoding="utf-8"))
    metricas = pd.read_csv(PASO2 / "6_tabla_metricas_modulo_criticidad_capa_a.csv")
    c_ids_all = set(metricas["metrica_id"].astype(str))
    c_ids_gate_a = set(metricas[metricas["gate"] == "A"]["metrica_id"].astype(str))
    gaps = []
    if anti.get("checks", {}).get("history_eval_hash_overlap") != 0:
        gaps.append("G1: overlap historial-eval distinto de 0")
    if checks["paso1_rag_2000"].get("rows") != 2000:
        gaps.append("G2: filas RAG != 2000")
    if checks["paso2_senales_400"].get("rows") != 400:
        gaps.append("G3: señales != 400")
    required_gate_a = {"C-01", "C-02", "C-03", "C-04", "C-05"}
    if not required_gate_a.issubset(c_ids_gate_a):
        gaps.append(f"G4: métricas Gate A incompletas: {required_gate_a - c_ids_gate_a}")
    if "C-06" not in c_ids_all:
        gaps.append("G4b: falta C-06 override rate en artefacto métricas")
    # override_rate=0 es válido si Gate A no es más conservador que agente RAG (caso batch actual)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 1,
        "checks": checks,
        "anti_fuga": anti.get("checks", {}),
        "metricas_capa_a_gate_a": metricas[metricas["gate"] == "A"].to_dict(orient="records"),
        "gaps_detectados": gaps,
        "veredicto": "OK" if not any(g.startswith("G1") or g.startswith("G2") or g.startswith("G3") or g.startswith("G4") for g in gaps) else "REVISAR",
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
        sev = "⚠️" if gid.startswith("G5") else "⚠️"
        items.append({"item": gid, "veredicto": sev, "detail": "gap documentado"})
    overall = "✅" if report1["veredicto"] == "OK" else "⚠️"
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 2,
        "items": items,
        "gaps_restantes": [g for g in report1.get("gaps_detectados", []) if g.startswith("G5")],
        "veredicto_global": overall,
    }


def write_gaps_md(report1: dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoría Pasada 1 — Gaps detectados",
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
    lines.extend([
        "",
        "## Conteos verificados",
        "",
        "| Artefacto | Filas | OK |",
        "|-----------|-------|-----|",
    ])
    for k, v in report1["checks"].items():
        rows = v.get("rows", "—")
        ok = "✅" if v.get("rows_ok", v.get("exists")) else ("✅" if v.get("exists") and "rows" not in v else "⚠️")
        lines.append(f"| {k} | {rows} | {ok} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_resultado_md(report2: dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoría Pasada 2 — Resultado final",
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
    if report2.get("gaps_restantes"):
        lines.extend(["", "## Gaps aceptados (documentales)", ""])
        for g in report2["gaps_restantes"]:
            lines.append(f"- {g}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    r1 = auditoria_pasada1()
    r2 = auditoria_pasada2(r1)
    (PASO2 / "8_informe_auditoria_pasada1_pipeline_completo.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (PASO2 / "9_informe_auditoria_pasada2_resultado_final.json").write_text(
        json.dumps(r2, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_gaps_md(r1, PASO2 / "AUDITORIA_PASADA1_GAPS.md")
    write_resultado_md(r2, PASO2 / "AUDITORIA_PASADA2_RESULTADO.md")
    print(json.dumps({"pasada1": r1["veredicto"], "pasada2": r2["veredicto_global"]}, indent=2))


if __name__ == "__main__":
    main()
