"""Ejecuta PASO 4 — calibración, ablación middleware, explicabilidad (IA06)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent
PASO3 = ROOT.parent / "3_protocolo_experimental_variantes"
PLUGINS = (ROOT.parent / "2_modulo_criticidad_gobernanza_adaptativa/plugins").resolve()

for p in (ROOT, PASO3, PLUGINS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from calibracion_diagnosticos_entregable import (  # noqa: E402
    build_resumen_informe,
    load_config,
    load_predictions,
    plot_ablation_delta,
    plot_calibration_curves_three_variants,
    plot_signal_importance,
    resolve_path,
    run_middleware_ablation,
    run_pilot_crewai_subanalysis,
    run_posthoc_calibration,
    run_signal_importance,
)


def main() -> None:
    cfg = load_config()
    seed = int(cfg["seed"])
    n_bins = int(cfg["calibracion"]["n_bins_ece"])
    cost_kw = {
        "pause_cost": float(cfg["cost_matrix"]["pause_hitl"]),
        "stop_cost": float(cfg["cost_matrix"]["stop_hitl"]),
        "fn_stop_cost": float(cfg["cost_matrix"]["false_negative_stop"]),
        "ece_bins": n_bins,
    }

    df_train = pd.read_csv(resolve_path(cfg["paths"]["train"]))
    df_holdout = pd.read_csv(resolve_path(cfg["paths"]["holdout"]))
    df_eval = pd.read_csv(resolve_path(cfg["paths"]["eval"]))
    df_var1_raw = pd.read_csv(resolve_path(cfg["paths"]["pred_var1"]))
    df_var2_raw = pd.read_csv(resolve_path(cfg["paths"]["pred_var2"]))
    df_gate_a = pd.read_csv(resolve_path(cfg["paths"]["gate_a"]))
    df_senales = pd.read_csv(resolve_path(cfg["paths"]["senales"]))

    train_hashes = set(df_train["text_hash"].astype(str))
    holdout_hashes = set(df_holdout["text_hash"].astype(str))

    preds = load_predictions(cfg)

    cal_df, calibrated = run_posthoc_calibration(preds, train_hashes, holdout_hashes, n_bins)
    cal_df.to_csv(ROOT / "1_tabla_calibracion_ece_brier_antes_despues.csv", index=False)
    plot_calibration_curves_three_variants(
        preds, calibrated, ROOT / "2_figura_curvas_calibracion_tres_variantes.png", n_bins,
    )

    rag_mod = import_module("1_plugin_rag_recuperacion")
    policy_mod = import_module("3_motor_politica_play_pausa_stop")
    df_rag = rag_mod.load_neighbors_table(resolve_path(cfg["paths"]["rag_hibrido"]), None)
    neighbors_map = rag_mod.neighbors_by_hash(df_rag)
    rag_plugin = rag_mod.RagPlugin(neighbors_map)
    build_features = policy_mod.build_features

    with resolve_path(cfg["paths"]["paso3_config"]).open(encoding="utf-8") as f:
        paso3_cfg = yaml.safe_load(f)
    policy_params = dict(paso3_cfg["policy"])
    win_path = resolve_path(cfg["paths"]["winning_config"])
    if win_path.exists():
        win = json.loads(win_path.read_text(encoding="utf-8"))
        p = win.get("params", {})
        policy_params = {
            "mode": p.get("mode", policy_params["mode"]),
            "weights": dict(p.get("weights", policy_params["weights"])),
            "threshold_stop": p.get("threshold_stop", policy_params["threshold_stop"]),
            "threshold_pausa": p.get("threshold_pausa", policy_params["threshold_pausa"]),
            "risk_stop_floor": p.get("risk_stop_floor", policy_params["risk_stop_floor"]),
            "p_stop_floor": p.get("p_stop_floor", policy_params["p_stop_floor"]),
            "stop_cost_threshold": p.get("stop_cost_threshold", policy_params["stop_cost_threshold"]),
            "pause_uncertainty": p.get("pause_uncertainty", policy_params["pause_uncertainty"]),
        }
    policy_engine = policy_mod.PolicyEngine(policy_params, rag_obligatorio=True)

    abl_df = run_middleware_ablation(
        df_eval,
        df_var1_raw,
        df_var2_raw,
        df_gate_a,
        neighbors_map,
        rag_plugin,
        policy_engine,
        build_features,
        list(cfg["ablacion"]["componentes"]),
        cost_kw,
    )
    abl_df.to_csv(ROOT / "3_tabla_ablacion_componentes_middleware.csv", index=False)
    plot_ablation_delta(abl_df, ROOT / "4_figura_ablacion_delta_f1_stop_ec.png")

    winning = json.loads(win_path.read_text(encoding="utf-8")) if win_path.exists() else {}
    imp_df = run_signal_importance(
        df_var2_raw,
        df_senales,
        winning,
        n_repeats=int(cfg["explicabilidad"]["n_repeats"]),
    )
    imp_df.to_csv(ROOT / "5_tabla_importancia_senales_overrides.csv", index=False)
    plot_signal_importance(imp_df, ROOT / "6_figura_importancia_senales_gate_b.png")

    pilot_df = run_pilot_crewai_subanalysis(df_var1_raw, cost_kw)
    pilot_df.to_csv(ROOT / "7_tabla_metricas_piloto_crewai_n40.csv", index=False)

    config_informe = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "n_eval": cfg["n_eval"],
        "n_piloto_crewai": cfg["n_piloto_crewai"],
        "calibracion": cfg["calibracion"],
        "ablacion_componentes": cfg["ablacion"]["componentes"],
        "upstream_refs": {k: str(resolve_path(v)) for k, v in cfg["paths"].items()},
        "honesty_notes": cfg["honesty_notes"],
    }
    (ROOT / "0_informe_configuracion_paso4.json").write_text(
        json.dumps(config_informe, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    resumen = build_resumen_informe(cal_df, abl_df, imp_df, pilot_df, cfg)
    resumen["timestamp"] = datetime.now(timezone.utc).isoformat()
    (ROOT / "8_informe_resumen_paso4.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    print("PASO 4 completado.")
    print("Calibración (ECE isotónica n=400):")
    for var, stats in resumen.get("calibracion_resumen", {}).items():
        print(f"  {var}: {stats['ECE_antes']:.4f} → {stats['ECE_despues_isotonic']:.4f}")
    print(f"Ablación peor F1-stop: {resumen.get('ablacion_peor_F1_stop')}")
    print(f"Piloto CrewAI n={resumen.get('piloto_n')}")


if __name__ == "__main__":
    main()
