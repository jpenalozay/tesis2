"""Ejecuta PASO 5 — tablero, checklist, gap, guía demo, auditoría global."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cierre_examen_entregable import (  # noqa: E402
    auditoria_global_0_4,
    build_checklist_examen,
    build_gap_overfitting_informe,
    build_guia_demo,
    build_resumen_paso5,
    build_tablero_experimentos,
    load_config,
    write_veredicto_md,
)


def main() -> None:
    cfg = load_config()
    tablero = build_tablero_experimentos(cfg)
    tablero.to_csv(ROOT / "1_tablero_experimentos_consolidado.csv", index=False)

    gap = build_gap_overfitting_informe(cfg)
    (ROOT / "3_informe_gap_overfitting_calibracion.json").write_text(
        json.dumps(gap, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    (ROOT / "4_guia_demo_presentacion_10min.md").write_text(
        build_guia_demo(cfg), encoding="utf-8",
    )

    audit = auditoria_global_0_4(cfg)
    (ROOT / "5_informe_auditoria_global_entregable_0_4.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    checklist = build_checklist_examen(cfg)
    checklist.to_csv(ROOT / "2_checklist_examen_final_ia08.csv", index=False)

    resumen = build_resumen_paso5(tablero, checklist, gap, audit)
    (ROOT / "8_informe_resumen_paso5.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    informe_cfg = {
        "paso": 5,
        "ia08": True,
        "seed": cfg["seed"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "paths_outputs": [
            "1_tablero_experimentos_consolidado.csv",
            "2_checklist_examen_final_ia08.csv",
            "3_informe_gap_overfitting_calibracion.json",
            "4_guia_demo_presentacion_10min.md",
            "5_informe_auditoria_global_entregable_0_4.json",
            "6_veredicto_final_entregable.md",
            "8_informe_resumen_paso5.json",
        ],
        "checklist_pct": resumen["checklist_cumplimiento_pct"],
        "veredicto_auditoria": audit["veredicto"],
    }
    (ROOT / "0_informe_configuracion_paso5.json").write_text(
        json.dumps(informe_cfg, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    write_veredicto_md(resumen, checklist, audit, ROOT / "6_veredicto_final_entregable.md")

    print(f"PASO 5: tablero={len(tablero)} filas checklist={resumen['checklist_cumplimiento_pct']}% auditoria={audit['veredicto']}")


if __name__ == "__main__":
    main()
