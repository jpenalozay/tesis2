"""Auditoría doble pasada PASO 4 (pipeline 0→4)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ENTREGABLE = Path(__file__).resolve().parents[1]
PASO4 = ENTREGABLE / "4_calibracion_diagnosticos_y_explicabilidad"

REQUIRED_PASO4 = [
    ("0_informe_configuracion_paso4.json", None),
    ("1_tabla_calibracion_ece_brier_antes_despues.csv", None),
    ("2_figura_curvas_calibracion_tres_variantes.png", None),
    ("3_tabla_ablacion_componentes_middleware.csv", None),
    ("4_figura_ablacion_delta_f1_stop_ec.png", None),
    ("5_tabla_importancia_senales_overrides.csv", None),
    ("6_figura_importancia_senales_gate_b.png", None),
    ("7_tabla_metricas_piloto_crewai_n40.csv", None),
    ("8_informe_resumen_paso4.json", None),
]


def check_file(path: Path, min_rows: int | None = None) -> dict[str, Any]:
    ok = path.exists()
    info: dict[str, Any] = {"path": str(path.relative_to(ENTREGABLE)), "exists": ok}
    if ok and path.suffix == ".csv":
        n = len(pd.read_csv(path))
        info["rows"] = n
        if min_rows is not None:
            info["rows_ok"] = n >= min_rows
    return info


def auditoria_pasada1() -> dict[str, Any]:
    checks = {}
    for name, min_r in REQUIRED_PASO4:
        checks[f"paso4_{name}"] = check_file(PASO4 / name, min_r)

    gaps = []
    for name, min_r in REQUIRED_PASO4:
        chk = checks.get(f"paso4_{name}", {})
        if not chk.get("exists"):
            gaps.append(f"G1: falta {name}")
        elif min_r and not chk.get("rows_ok", True):
            gaps.append(f"G2: {name} filas insuficientes")

    cal_path = PASO4 / "1_tabla_calibracion_ece_brier_antes_despues.csv"
    if cal_path.exists():
        cal = pd.read_csv(cal_path)
        for var in ("Baseline", "Var1", "Var2"):
            sub = cal[(cal["variante"] == var) & (cal["metodo_calibracion"] == "isotonic")]
            if sub.empty:
                gaps.append(f"G3: calibración isotónica ausente para {var}")

    abl_path = PASO4 / "3_tabla_ablacion_componentes_middleware.csv"
    if abl_path.exists():
        abl = pd.read_csv(abl_path)
        if len(abl) < 4:
            gaps.append("G4: ablación debe incluir Var2 completo + ≥3 componentes")

    pilot_path = PASO4 / "7_tabla_metricas_piloto_crewai_n40.csv"
    if pilot_path.exists():
        pilot = pd.read_csv(pilot_path)
        if "n_piloto" in pilot.columns and int(pilot.iloc[0]["n_piloto"]) != 40:
            gaps.append(f"G5: piloto CrewAI n={pilot.iloc[0]['n_piloto']} (esperado 40)")

    resumen_path = PASO4 / "8_informe_resumen_paso4.json"
    if resumen_path.exists():
        res = json.loads(resumen_path.read_text(encoding="utf-8"))
        if not res.get("honesty_notes"):
            gaps.append("G6: honesty_notes vacías en resumen PASO 4")

    crit = [g for g in gaps if g.startswith(("G1", "G2", "G3"))]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 1,
        "checks": checks,
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
    for gid in report1.get("gaps_detectados", []):
        items.append({"item": gid, "veredicto": "⚠️", "detail": "gap documentado"})
    overall = "✅" if report1["veredicto"] == "OK" else "⚠️"
    doc_only = all(g.startswith(("G5", "G6")) for g in report1.get("gaps_detectados", []))
    if report1["veredicto"] == "OK" or doc_only:
        overall = "✅"
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 2,
        "items": items,
        "gaps_restantes": report1.get("gaps_detectados", []),
        "veredicto_global": overall,
    }


def write_gaps_md(report1: dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoría Pasada 1 — Gaps PASO 4",
        "",
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
        "# Auditoría Pasada 2 — Resultado final PASO 4",
        "",
        f"**Veredicto global:** {report2['veredicto_global']}",
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
    (PASO4 / "9_informe_auditoria_pasada1_paso4.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    (PASO4 / "10_informe_auditoria_pasada2_resultado_final.json").write_text(
        json.dumps(r2, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    write_gaps_md(r1, PASO4 / "AUDITORIA_PASADA1_GAPS.md")
    write_resultado_md(r2, PASO4 / "AUDITORIA_PASADA2_RESULTADO.md")
    print(f"Auditoría PASO 4: pasada1={r1['veredicto']} pasada2={r2['veredicto_global']}")


if __name__ == "__main__":
    main()
