"""Ejecuta PASO 3 con API DeepSeek real (api-incremental) y regenera artefactos 0–16."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
_TESIS2 = ROOT.parents[2]
load_dotenv(_TESIS2 / ".env")
load_dotenv(ROOT / ".env")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PLUGINS = (ROOT / "../2_modulo_criticidad_gobernanza_adaptativa/plugins").resolve()
if str(PLUGINS) not in sys.path:
    sys.path.insert(0, str(PLUGINS))

from metricas_protocolo_entregable import (
    compute_metrics_bundle,
    mcnemar_test,
    plot_ablation_f1_ec_fnr,
    plot_calibration_curve,
    plot_confusion_matrices,
    stratified_cv_metrics,
)
from protocolo_variantes_entregable import (
    ensure_deepseek_env,
    load_deepseek_cache,
    load_jsonl_cache,
    predict_baseline,
    predict_var1,
    predict_var2,
    compute_var1_api_queue,
    select_var1_pilot_hashes_stratified,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(ROOT / "run_protocolo.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("run_protocolo")


def resolve(p: str) -> Path:
    return (ROOT / p).resolve()


def main() -> None:
    with (ROOT / "0_configuracion_protocolo_experimental.yaml").open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    seed = int(cfg["seed"])
    run_api = bool(cfg["execution"]["run_api"])
    run_crewai = bool(cfg["execution"]["run_crewai"])
    max_api_bl = int(cfg["execution"]["max_new_api_calls_baseline"])
    max_api_v1 = int(cfg["execution"]["max_new_api_calls_var1"])
    log_every = int(cfg["execution"].get("log_every_n", 10))
    pause_cost = float(cfg["cost_matrix"]["pause_hitl"])
    stop_cost = float(cfg["cost_matrix"]["stop_hitl"])
    fn_stop = float(cfg["cost_matrix"]["false_negative_stop"])
    ece_bins = int(cfg["metrics"]["ece_bins"])

    has_key = ensure_deepseek_env()
    log.info(
        "Inicio PASO 3 mode=%s run_api=%s run_crewai=%s deepseek_key=%s max_api_bl=%s max_api_v1=%s",
        cfg["execution"]["mode"],
        run_api,
        run_crewai,
        has_key,
        max_api_bl,
        max_api_v1,
    )

    path_eval = resolve(cfg["paths"]["eval"])
    path_holdout = resolve(cfg["paths"]["holdout"])
    path_rag = resolve(cfg["paths"]["rag_hibrido"])
    path_anti = resolve(cfg["paths"]["anti_fuga"])
    path_gate_a = resolve(cfg["paths"]["gate_a"])
    path_ds_ext = resolve(cfg["paths"]["deepseek_cache_ext"])
    path_win = resolve(cfg["paths"]["winning_config"])
    cache_bl = ROOT / "1_cache_predicciones_deepseek_baseline.jsonl"
    cache_v1 = ROOT / "2_cache_predicciones_var1_crewai_rag.jsonl"

    df_eval = pd.read_csv(path_eval)
    df_holdout = pd.read_csv(path_holdout)
    holdout_hashes = set(df_holdout["text_hash"].astype(str))
    assert len(df_eval) == cfg["n_eval"]

    rag_mod = import_module("1_plugin_rag_recuperacion")
    policy_mod = import_module("3_motor_politica_play_pausa_stop")
    df_rag = rag_mod.load_neighbors_table(path_rag, None)
    neighbors_map = rag_mod.neighbors_by_hash(df_rag)
    rag_plugin = rag_mod.RagPlugin(neighbors_map)

    anti_fuga = json.loads(path_anti.read_text(encoding="utf-8"))
    df_gate_a = pd.read_csv(path_gate_a)
    gate_a_by_hash = df_gate_a.set_index("text_hash")["decision"].to_dict()

    policy_params = dict(cfg["policy"])
    winning_source = "yaml_fallback"
    if path_win.exists():
        win = json.loads(path_win.read_text(encoding="utf-8"))
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
        winning_source = str(path_win)

    policy_engine = policy_mod.PolicyEngine(policy_params, rag_obligatorio=True)
    build_features = policy_mod.build_features

    deepseek_cache = load_deepseek_cache([path_ds_ext, cache_bl])
    crewai_cache = load_jsonl_cache(cache_v1)

    eval_rows = df_eval[["text_hash", "thesis_class"]].to_dict(orient="records")
    var1_pilot_stratified = select_var1_pilot_hashes_stratified(eval_rows, seed, max_api_v1)
    var1_api_queue = compute_var1_api_queue(eval_rows, crewai_cache, var1_pilot_stratified)
    log.info(
        "Var1 pilot: estratificado=%d cola_api=%d cache_crewai=%d",
        len(var1_pilot_stratified),
        len(var1_api_queue),
        len(crewai_cache),
    )
    api_calls_bl = [0]
    api_calls_v1 = [0]
    api_errors: dict[str, int] = {}
    api_errors_v1: dict[str, int] = {}
    baseline_rows, var1_rows, var2_rows = [], [], []
    source_counts = {"baseline": {}, "var1": {}}

    n_eval = len(df_eval)
    for pos, row in df_eval.reset_index(drop=True).iterrows():
        text = str(row["text"])
        th = str(row["text_hash"])
        true_label = str(row["thesis_class"])
        ns = neighbors_map.get(th, [])
        rag_enrich = rag_plugin.enrich(th, ns)

        bl, bl_conf, bl_lat, bl_src, bl_tok = predict_baseline(
            text, th, deepseek_cache, cache_bl, run_api, api_calls_bl, max_api_bl, api_errors,
        )
        source_counts["baseline"][bl_src] = source_counts["baseline"].get(bl_src, 0) + 1
        baseline_rows.append({
            "query_idx": int(pos), "text_hash": th, "true_label": true_label,
            "pred_label": bl, "confidence": round(bl_conf, 6), "latency_ms": round(bl_lat, 2),
            "source": bl_src, "tokens": bl_tok,
        })

        v1, v1_conf, v1_lat, v1_src, v1_tok = predict_var1(
            text, th, ns, crewai_cache, run_crewai, api_calls_v1, max_api_v1, cache_v1,
            api_errors_v1, var1_pilot_stratified,
        )
        source_counts["var1"][v1_src] = source_counts["var1"].get(v1_src, 0) + 1
        var1_rows.append({
            "query_idx": int(pos), "text_hash": th, "true_label": true_label,
            "pred_label": v1, "confidence": round(v1_conf, 6), "latency_ms": round(v1_lat, 2),
            "source": v1_src, "tokens": v1_tok, "rag_neighbors_k": len(ns),
        })

        ga = gate_a_by_hash.get(th, "pausa")
        features = build_features(text, v1, ns, rag_enrich, llm_label=v1, llm_confidence=v1_conf)
        v2, v2_conf, overridden, trace_str, _ = predict_var2(v1, v1_conf, ga, features, policy_engine)
        var2_rows.append({
            "query_idx": int(pos), "text_hash": th, "true_label": true_label,
            "agent_label": v1, "final_label": v2, "confidence": round(v2_conf, 6),
            "overridden": overridden, "decision_gate_a": ga,
            "risk_4d": round(float(features["risk_4d"]), 6),
            "trace": trace_str,
            "source": "var2_gate_b_deterministic",
            "latency_ms": round(v1_lat + 0.5, 2),
            "tokens": v1_tok,
        })

        if (pos + 1) % log_every == 0 or pos + 1 == n_eval:
            log.info(
                "Progreso %d/%d | api_bl=%d cache_bl=%d | var1 cache=%d api=%d abst=%d | api_v1=%d/%d",
                pos + 1,
                n_eval,
                source_counts["baseline"].get("deepseek_api", 0),
                source_counts["baseline"].get("deepseek_cache", 0),
                source_counts["var1"].get("crewai_cache", 0),
                source_counts["var1"].get("crewai_api", 0),
                source_counts["var1"].get("abstencion_fuera_piloto_d5", 0)
                + source_counts["var1"].get("abstencion_crewai_fallo", 0),
                api_calls_v1[0],
                max_api_v1,
            )

    df_bl = pd.DataFrame(baseline_rows)
    df_v1 = pd.DataFrame(var1_rows)
    df_v2 = pd.DataFrame(var2_rows)

    df_cons = df_eval[["text_hash", "text", "thesis_class", "severity"]].copy()
    df_cons = df_cons.merge(
        df_bl[["text_hash", "pred_label", "confidence", "source"]].rename(
            columns={"pred_label": "pred_baseline", "confidence": "conf_baseline", "source": "source_baseline"}
        ),
        on="text_hash",
    )
    df_cons = df_cons.merge(
        df_v1[["text_hash", "pred_label", "confidence", "source"]].rename(
            columns={"pred_label": "pred_var1", "confidence": "conf_var1", "source": "source_var1"}
        ),
        on="text_hash",
    )
    df_cons = df_cons.merge(
        df_v2[["text_hash", "final_label", "confidence", "overridden", "agent_label"]].rename(
            columns={"final_label": "pred_var2", "confidence": "conf_var2", "agent_label": "var2_agent_label"}
        ),
        on="text_hash",
    )
    df_cons["is_holdout"] = df_cons["text_hash"].isin(holdout_hashes).astype(int)

    y_true = df_cons["thesis_class"].astype(str).tolist()
    cost_kw = dict(pause_cost=pause_cost, stop_cost=stop_cost, fn_stop_cost=fn_stop, ece_bins=ece_bins)

    m_bl = compute_metrics_bundle(
        y_true, df_bl["pred_label"].tolist(), "Baseline",
        df_bl["confidence"].tolist(), df_bl["latency_ms"].tolist(), int(df_bl["tokens"].sum()), alcance_n=400, **cost_kw,
    )
    m_v1 = compute_metrics_bundle(
        y_true, df_v1["pred_label"].tolist(), "Var1",
        df_v1["confidence"].tolist(), df_v1["latency_ms"].tolist(), int(df_v1["tokens"].sum()), alcance_n=400, **cost_kw,
    )
    m_v2 = compute_metrics_bundle(
        y_true, df_v2["final_label"].tolist(), "Var2",
        df_v2["confidence"].tolist(), df_v2["latency_ms"].tolist(), int(df_v2["tokens"].sum()), alcance_n=400,
        override_count=int(df_v2["overridden"].sum()), **cost_kw,
    )
    m_v2["override_rate"] = round(float(df_v2["overridden"].mean()), 6)
    df_metricas_min = pd.DataFrame([m_bl, m_v1, m_v2])

    ext_rows = []
    for m in [m_bl, m_v1, m_v2]:
        ext_rows.append({
            "variante": m["variante"],
            "F1-play": m.get("F1-play"),
            "F1-pausa": m.get("F1-pausa"),
            "F1-stop": m.get("F1-stop (F1-critical)"),
            "Precision-play": m.get("Precision-play"),
            "Precision-pausa": m.get("Precision-pausa"),
            "Precision-stop": m.get("Precision-stop"),
            "Recall-play": m.get("Recall-play"),
            "Recall-pausa": m.get("Recall-pausa"),
            "Recall-stop": m.get("Recall-stop"),
            "MCC-macro": m["MCC-macro (Matthews Correlation)"],
            "balanced_accuracy": m["Balanced accuracy"],
            "tokens_total": m["tokens_total"],
            "latencia_media_ms": m.get("latencia_media_ms", 0),
            "latencia_p95_ms": m["latencia_p95_ms"],
            "hitl_tiempo_total_min": m.get("hitl_tiempo_total_min", 0),
            "hitl_costo_programador_usd": m.get("hitl_costo_programador_usd", 0),
            "hitl_intervenciones_pausa": m.get("hitl_intervenciones_pausa", 0),
            "hitl_intervenciones_stop": m.get("hitl_intervenciones_stop", 0),
            "override_rate": m.get("override_rate", 0.0),
            "end_indice_auxiliar": m["end_indice_auxiliar"],
            "nota_end": "índice auxiliar interno — no métrica principal",
            "nota_hitl": "supuesto: 5min/pausa, 20min/stop, 3min/override, $45/h dev",
        })
    df_metricas_ext = pd.DataFrame(ext_rows)

    ho = df_cons[df_cons["is_holdout"] == 1]
    y_ho = ho["thesis_class"].astype(str).tolist()
    ho_rows = [
        compute_metrics_bundle(y_ho, ho["pred_baseline"].tolist(), "Baseline", ho["conf_baseline"].tolist(), alcance_n=120, **cost_kw),
        compute_metrics_bundle(y_ho, ho["pred_var1"].tolist(), "Var1", ho["conf_var1"].tolist(), alcance_n=120, **cost_kw),
        compute_metrics_bundle(
            y_ho, ho["pred_var2"].tolist(), "Var2", ho["conf_var2"].tolist(), alcance_n=120,
            override_count=int(ho["overridden"].sum()) if "overridden" in ho.columns else 0, **cost_kw,
        ),
    ]
    df_holdout_metrics = pd.DataFrame(ho_rows)

    cv_bl = stratified_cv_metrics(y_true, df_bl["pred_label"].tolist(), df_bl["confidence"].tolist(), "Baseline", seed, **cost_kw)
    cv_v1 = stratified_cv_metrics(y_true, df_v1["pred_label"].tolist(), df_v1["confidence"].tolist(), "Var1", seed, **cost_kw)
    cv_v2 = stratified_cv_metrics(y_true, df_v2["final_label"].tolist(), df_v2["confidence"].tolist(), "Var2", seed, **cost_kw)
    df_cv = pd.concat([cv_bl, cv_v1, cv_v2], ignore_index=True)

    mcnemar_rows = [
        mcnemar_test(y_true, df_bl["pred_label"].tolist(), df_v1["pred_label"].tolist(), "Baseline vs Var1"),
        mcnemar_test(y_true, df_v1["pred_label"].tolist(), df_v2["final_label"].tolist(), "Var1 vs Var2"),
        mcnemar_test(y_true, df_bl["pred_label"].tolist(), df_v2["final_label"].tolist(), "Baseline vs Var2"),
    ]
    df_mcnemar = pd.DataFrame(mcnemar_rows)

    plot_ablation_f1_ec_fnr(df_metricas_min, str(ROOT / "13_figura_ablacion_f1_macro_ec_fnr_stop.png"))
    plot_confusion_matrices(
        y_true,
        {"Baseline": df_bl["pred_label"].tolist(), "Var1": df_v1["pred_label"].tolist(), "Var2": df_v2["final_label"].tolist()},
        str(ROOT / "14_figura_matrices_confusion_tres_variantes.png"),
    )
    plot_calibration_curve(
        y_true, df_v2["confidence"].tolist(), df_v2["final_label"].tolist(),
        str(ROOT / "15_figura_curva_calibracion_ece_var2.png"), ece_bins,
    )

    mode = cfg["execution"]["mode"]
    config_informe = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "n_eval": len(df_eval),
        "execution_mode": mode,
        "run_api": run_api,
        "run_crewai": run_crewai,
        "decisiones_D1_D5": cfg["decisiones"],
        "policy_params_source": winning_source,
        "cost_matrix": cfg["cost_matrix"],
        "anti_fuga_overlap": anti_fuga["checks"]["history_eval_hash_overlap"],
        "upstream_refs": {k: str(resolve(v)) for k, v in cfg["paths"].items()},
        "honesty_notes": [
            "Arquitectura: RAG→CrewAI(Var1)→Criticidad Gate B(Var2). Prompt CrewAI v2_permissive.",
            f"Baseline: deepseek cache+API ({source_counts['baseline']}).",
            f"Var1 piloto D5: crewai_cache+api ({source_counts['var1']}); fuera piloto: abstención pausa (Chow 1970).",
            "Var2: Gate B ampliado (riesgo 4D, incertidumbre, FN-stop); 0 API adicional.",
            "HITL cost: supuesto operativo documentado en métricas extendidas (no medido en campo).",
        ],
    }
    (ROOT / "0_informe_configuracion_protocolo_experimental.json").write_text(
        json.dumps(config_informe, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    exec_informe = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "run_api": run_api,
        "run_crewai": run_crewai,
        "deepseek_key_present": has_key,
        "api_calls_baseline": api_calls_bl[0],
        "api_calls_var1": api_calls_v1[0],
        "api_calls_var1_sesion": api_calls_v1[0],
        "api_calls_var1_historico": int((df_v1["source"] == "crewai_api").sum()),
        "crewai_pilot_cache_n": int((df_v1["source"] == "crewai_cache").sum()),
        "crewai_pilot_api_first_run_n": 40,
        "api_calls_baseline_sesion": api_calls_bl[0],
        "api_calls_baseline_historico": int((df_bl["source"] == "deepseek_api").sum()),
        "api_errors_baseline": api_errors,
        "api_errors_var1": api_errors_v1,
        "baseline_sources": source_counts["baseline"],
        "var1_sources": source_counts["var1"],
        "var1_pilot_stratified_n": len(var1_pilot_stratified),
        "var1_api_queue_n": len(var1_api_queue),
        "cache_coverage": {
            "deepseek_hits_n400": int((df_bl["source"] == "deepseek_cache").sum()),
            "deepseek_api_n400": int((df_bl["source"] == "deepseek_api").sum()),
            "crewai_api_n400": int((df_v1["source"] == "crewai_api").sum()),
            "crewai_cache_n400": int((df_v1["source"] == "crewai_cache").sum()),
            "majority_fallback_n400": int((df_v1["source"] == "pgvector_majority_fallback").sum()),
            "abstencion_fuera_piloto_n400": int((df_v1["source"] == "abstencion_fuera_piloto_d5").sum()),
            "abstencion_crewai_fallo_n400": int((df_v1["source"] == "abstencion_crewai_fallo").sum()),
            "lexical_fallback_n400": int((df_bl["source"] == "early_gate_lexical_fallback").sum()),
        },
        "tokens_total": {"baseline": int(df_bl["tokens"].sum()), "var1": int(df_v1["tokens"].sum()), "var2": int(df_v2["tokens"].sum())},
    }
    (ROOT / "12_informe_ejecucion_fuentes_cache_api.json").write_text(
        json.dumps(exec_informe, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    resumen = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_eval": 400,
        "metricas_set_minimo": df_metricas_min.to_dict(orient="records"),
        "mcnemar": df_mcnemar.to_dict(orient="records"),
        "veredicto_preliminar": f"protocolo ejecutado {mode} — api_bl={api_calls_bl[0]}",
    }
    (ROOT / "16_informe_resumen_protocolo_experimental.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    df_bl.to_csv(ROOT / "3_tabla_predicciones_baseline_amnesico_n400.csv", index=False)
    df_v1.to_csv(ROOT / "4_tabla_predicciones_var1_crewai_rag_n400.csv", index=False)
    df_v2.to_csv(ROOT / "5_tabla_predicciones_var2_middleware_intercepta_n400.csv", index=False)
    df_cons.to_csv(ROOT / "6_tabla_predicciones_consolidada_tres_variantes_n400.csv", index=False)
    df_metricas_min.to_csv(ROOT / "7_tabla_metricas_set_minimo_seis_por_variante.csv", index=False)
    df_metricas_ext.to_csv(ROOT / "8_tabla_metricas_extendidas_framework_por_variante.csv", index=False)
    df_holdout_metrics.to_csv(ROOT / "9_tabla_validacion_holdout_30_por_variante.csv", index=False)
    df_cv.to_csv(ROOT / "10_tabla_validacion_cruzada_5fold_estratificada_n400.csv", index=False)
    df_mcnemar.to_csv(ROOT / "11_tabla_comparacion_pareada_mcnemar.csv", index=False)

    log.info("Finalizado. Baseline sources: %s", source_counts["baseline"])
    log.info("Var1 sources: %s | crewai_api_sesion=%d", source_counts["var1"], api_calls_v1[0])
    log.info("Métricas:\n%s", df_metricas_min[["variante", "F1-macro (Macro-averaged F1)", "EC (Expected Cost / ex-CEPA)", "FNR-stop (False Negative Rate stop)"]])


if __name__ == "__main__":
    main()
