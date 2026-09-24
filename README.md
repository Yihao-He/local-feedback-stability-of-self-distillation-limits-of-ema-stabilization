# Reproducibility files: Idea 5

This package regenerates the CPU local-stability and finite-difference tables and both statistical plots from the compact recorded feature-experiment results. The CPU control uses the exact local model in the paper.

## Run

Python 3.10+, NumPy, and Matplotlib are required. From this directory:

```bash
python figures/reanalyze.py
python figures/make_figures.py
```

The analysis writes compact CSV tables and a protocol record under `results/`.

## Contents

- `figures/`: compact-result and plotting scripts.
- `results/source_gpu_summary.json`: only the derivatives, feedback grid, and recorded trajectories needed by the reanalysis script.

No prompts, raw features, model weights, credentials, or machine paths are included. These files regenerate the reported local analyses and plots; they do not rerun frozen-model feature extraction.

No reuse license has been assigned in this package. Add the authors' chosen license before public release.
