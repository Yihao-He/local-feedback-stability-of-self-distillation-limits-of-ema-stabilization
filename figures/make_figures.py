from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
COLORS = {0.0: "#0072B2", 0.9: "#D55E00", 0.99: "#009E73"}
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
                     "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
                     "legend.fontsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})


def read_csv(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def fig_spectrum(rows):
    fig, ax = plt.subplots(figsize=(3.35, 2.5))
    for mu in (0.0, 0.9, 0.99):
        subset = sorted([r for r in rows if float(r["ema_mu"]) == mu],
                        key=lambda r: float(r["target_c_over_f"]))
        ax.plot([float(r["target_c_over_f"]) for r in subset],
                [float(r["spectral_radius"]) for r in subset],
                color=COLORS[mu], marker="o", markersize=2.7, linewidth=1.05,
                label=rf"EMA $\mu={mu:g}$")
    ax.axhline(1., color="#333333", linestyle="--", linewidth=.8)
    ax.axvline(1., color="#555555", linestyle=":", linewidth=.9)
    ax.set_xlabel("Feedback ratio c/f")
    ax.set_ylabel("Local spectral radius")
    ax.set_xlim(.65, 1.35); ax.set_ylim(.92, 1.09)
    ax.grid(alpha=.2, linewidth=.5)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(pad=.6)
    fig.savefig(FIGURES / "fig1_feedback_stability.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_fd(rows):
    target = np.asarray([float(r["target_c_over_f"]) for r in rows])
    measured = np.asarray([float(r["measured_c_over_f"]) for r in rows])
    error = np.asarray([float(r["relative_error"]) for r in rows])
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.5))
    lo, hi = min(target.min(), measured.min()), max(target.max(), measured.max())
    axes[0].plot([lo, hi], [lo, hi], color="#666666", linestyle="--", linewidth=.8)
    axes[0].scatter(target, measured, color="#0072B2", s=18, zorder=3)
    axes[0].set_xlabel("Prescribed c/f")
    axes[0].set_ylabel("Finite-difference estimate c/f")
    axes[0].set_title("Cross-Jacobian values")
    axes[0].grid(alpha=.2, linewidth=.5)
    axes[1].bar(np.arange(len(error)), error, width=.62, color="#D55E00", alpha=.8)
    axes[1].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    axes[1].set_xticks(np.arange(len(error)))
    axes[1].set_xticklabels([f"{x:.1f}" for x in target])
    axes[1].set_xlabel("Prescribed c/f")
    axes[1].set_ylabel("Relative finite-difference error")
    axes[1].set_title("Derivative check")
    axes[1].grid(axis="y", alpha=.2, linewidth=.5)
    fig.tight_layout(pad=.7, w_pad=1.1)
    fig.savefig(FIGURES / "fig2_jacobian_check.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIGURES.mkdir(exist_ok=True)
    fig_spectrum(read_csv("feedback_stability_grid.csv"))
    fig_fd(read_csv("finite_difference_checks.csv"))
    print("Wrote fig1_feedback_stability.pdf and fig2_jacobian_check.pdf")


if __name__ == "__main__":
    main()
