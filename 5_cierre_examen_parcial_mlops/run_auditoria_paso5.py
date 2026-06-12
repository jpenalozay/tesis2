"""Auditoría doble pasada PASO 5 (cierre IA08 + pipeline 0→4)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
ENTREGABLE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cierre_examen_entregable import auditoria_global_0_4, load_config  # noqa: E402

REQUIRED_PASO5 = [
    "0_configuracion_cierre_examen.yaml",
    "0_informe_configuracion_paso5.json",
    "1_tablero_experimentos_consolidado.csv",
    "2_checklist_examen_final_ia08.csv",
    "3_informe_gap_overfitting_calibracion.json",
    "4_guia_demo_presentacion_10min.md",
    "5_informe_auditoria_global_entregable_0_4.json",
    "6_veredicto_final_entregable.md",
    "8_informe_resumen_paso5.json",
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
    checks = {f"paso5_{name}": check_file(ROOT / name) for name in REQUIRED_PASO5}
    tab_path = ROOT / "1_tablero_experimentos_consolidado.csv"
    chk_path = ROOT / "2_checklist_examen_final_ia08.csv"

    gaps: list[str] = []
    for name in REQUIRED_PASO5:
        if not (ROOT / name).exists():
            gaps.append(f"G1: falta {name}")

    if tab_path.exists():
        tab = pd.read_csv(tab_path)
        if len(tab) < 10:
            gaps.append(f"G2: tablero {len(tab)} filas (esperado ≥10)")
        if not set(tab["paso"].astype(str)).issuperset({"0", "3", "4", "HPO"}):
            gaps.append("G3: tablero incompleto (faltan pasos clave)")

    if chk_path.exists():
        chk = pd.read_csv(chk_path)
        pct = (chk["estado"] == "CUMPLIDO").mean() * 100
        if pct < 80:
            gaps.append(f"G4: checklist {pct:.0f}% (esperado ≥80%)")

    global_audit = auditoria_global_0_4(load_config())
    if global_audit["veredicto"] != "OK":
        gaps.extend(global_audit.get("gaps_detectados", []))

    crit = [g for g in gaps if g.startswith(("G1", "G2", "G3"))]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pasada": 1,
        "checks": checks,
        "global_audit_veredicto": global_audit["veredicto"],
        "gaps_detectados": gaps,
        "veredicto": "OK" if not crit else "REVISAR",
    }


def auditoria_pasada2(report1: dict[str, Any]) -> dict[str, Any]:
    items = []
    for key, chk in report1["checks"].items():
        items.append({"item": key, "veredicto": "✅" if chk.get("exists") else "⚠️", "detail": chk})
    items.append({
        "item": "auditoria_global_0_4",
        "veredicto": "✅" if report1.get("global_audit_veredicto") == "OK" else "⚠️",
        "detail": report1.get("global_audit_veredicto"),
    })
    for gid in report1.get("gaps_detectados", []):
        if gid.startswith("G_"):
            items.append({"item": gid, "veredicto": "⚠️", "detail": "gap documentado"})
    overall = "✅" if report1["veredicto"] == "OK" and report1.get("global_audit_veredicto") == "OK" else "⚠️"
    doc_only = all(
        g.startswith(("G4", "G_DOC", "G_MET")) or "G_P4" in g
        for g in report1.get("gaps_detectados", [])
    )
    if report1["veredicto"] == "OK" and report1.get("global_audit_veredicto") == "OK":
        overall = "✅"
    elif doc_only and report1["veredicto"] == "OK":
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
        "# Auditoría Pasada 1 — Gaps PASO 5",
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
        "# Auditoría Pasada 2 — Resultado final PASO 5",
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
    (ROOT / "7_informe_auditoria_pasada1_paso5.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    (ROOT / "9_informe_auditoria_pasada2_resultado_final.json").write_text(
        json.dumps(r2, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    write_gaps_md(r1, ROOT / "AUDITORIA_PASADA1_GAPS.md")
    write_resultado_md(r2, ROOT / "AUDITORIA_PASADA2_RESULTADO.md")
    print(f"Auditoría PASO 5: pasada1={r1['veredicto']} pasada2={r2['veredicto_global']}")


if __name__ == "__main__":
    main()
