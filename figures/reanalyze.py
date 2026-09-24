"""Rebuild compact CPU analyses from the records supplied with this paper."""
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]

def read_json(name):
    kind = "gpu" if "_gpu" in name else "cpu"
    return json.loads((ROOT / "results" / ("source_" + kind + "_summary.json")).read_text(encoding="utf-8"))

def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def run_idea05():
    out = ROOT / "results"
    gpu = read_json("idea05_gpu.json")
    stability = []
    for row in gpu["ratio_ema_grid"]:
        stability.append({
            "target_c_over_f": row["target_c_over_f"],
            "measured_c_over_f": row["measured_c_over_f"],
            "ema_mu": row["ema_mu"], "eta_f": row["eta_f"],
            "spectral_radius": row["local_spectral_radius"],
            "predicted_stable": int(row["predicted_stable"]),
        })
    write_csv(out / "feedback_stability_grid.csv", stability)
    trajectory_rows = []
    for row in gpu["ratio_ema_grid"]:
        radius = row["local_spectral_radius"]
        trajectory_rows.append({
            "target_c_over_f": row["target_c_over_f"],
            "ema_mu": row["ema_mu"],
            "initial_student": 1e-5, "initial_teacher": 1e-5,
            "step": row["student_teacher_trajectory"][-1]["step"],
            "normalized_state_norm": row["student_teacher_trajectory"][-1]["student_teacher_norm"] / (math.sqrt(2) * 1e-5),
            "dominant_mode_doubling_steps": math.log(2) / math.log(radius) if radius > 1 else "",
        })
    write_csv(out / "normalized_trajectory.csv", trajectory_rows)
    fd_rows = []
    f = float(gpu["f_empirical"])
    for item in gpu["cross_jacobian_finite_difference_checks"]:
        fd_rows.append({"target_c_over_f": item["target_c"]/f,
                        "measured_c_over_f": item["finite_difference_c"]/f,
                        "relative_error": item["relative_error"]})
    write_csv(out / "finite_difference_checks.csv", fd_rows)
    # Matched frozen-teacher student-only CPU control; teacher output is fixed at zero.
    x0 = 1e-5
    rho_student = 1.0 - .2
    frozen = [{"step": t, "student_abs_error": x0*rho_student**t,
               "squared_error": (x0*rho_student**t)**2, "student_spectral_radius": rho_student}
              for t in (0, 1, 5, 10, 20, 50)]
    write_csv(out / "frozen_teacher_control.csv", frozen)
    (out / "reanalysis_config.json").write_text(json.dumps({
        "model": "x+ = (1-eta*f)x + eta*c*y; y+ = mu*y+(1-mu)x+",
        "gpu_feature_rows": gpu["feature_rows"], "ordinary_rows": gpu["ordinary_rows"],
        "arithmetic_rows": gpu["arithmetic_rows"], "f_empirical": f,
        "natural_unscaled_c_over_f": gpu["raw_privileged_cross_over_f"],
        "finite_difference_max_relative_error": gpu["max_cross_jacobian_relative_error"],
        "fixed_point": "(x,y)=(0,0) is exact by construction; JSON's 1.0 is not an independently measured match rate",
        "frozen_teacher_control": "y fixed at zero, eta*f=.2, x0=1e-5, 50 deterministic CPU steps",
        "gpu_parameters": "gamma-scaled feedback ratios are controlled interventions, not natural self-distillation measurements",
    }, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_idea05()
