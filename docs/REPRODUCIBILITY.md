# Setup, execution and reproducibility

## Validation status

This repository contains historical research results and maintained experiment code. The September 2026 maintenance update checks notebook structure, Python syntax and stage configuration logic without private data, GPU training or model downloads. It does **not** rerun the experiments or verify their numerical reproduction.

The follow-up notebook's saved outputs were cleared after editing settings, so old logs cannot be mistaken for outputs from the new configuration. The public report, result summary and SVG figures retain the original results. The historical notebook retains its previous outputs.

## Environment

Use Python 3.10 or newer and a virtual environment. From the repository root:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m jupyterlab
```

`requirements.txt` lists direct dependencies, not a tested training lockfile. The original exact package/CUDA environment was not recorded in the provided public artifacts. Select an appropriate PyTorch build for your hardware, test the real-data smoke run, and save `python -m pip freeze` alongside the outputs of a successful run. GPU memory and runtime depend strongly on sequence lengths and backbone size. The 150M run is optional.

In Colab, install the dependencies needed by the notebook in your runtime, enable a suitable GPU and run the guarded Drive-mount cell. On a local machine the mount cell skips Drive. Hugging Face model downloads require network access on first use.

## Data and paths

Supply the CSVs described in [DATA.md](DATA.md), then set:

```python
PROJECT_ROOT_OVERRIDE = '/absolute/path/to/project'
OUTPUT_DIR_OVERRIDE = '/absolute/path/to/new/output-folder'  # follow-up only
```

The project folder must contain `processed_data/training.csv` and both held-out CSVs. Explicit paths are preferable to the legacy automatic search through working directories and Google Drive. Keep different experiment versions in separate output folders: run fingerprints include the Git commit, dataset hashes and settings, so old outputs may correctly be rejected for reuse.

## Follow-up stages

Start with `notebooks/sequential_binary_followup_experiments.ipynb`. Restart the kernel and run cells in order whenever you change settings; some function defaults capture configuration values at definition time.

| Purpose | Settings | Behaviour |
| --- | --- | --- |
| Default smoke run | `SMOKE_TEST=True`, `RUN_STAGE='validation_check'` | Reduced real-data subset, one epoch, split seed 42, three split strategies |
| Frozen capacity | `SMOKE_TEST=False`, `RUN_STAGE='model_capacity'` | Frozen 8M and 35M, twenty epochs |
| Fine-tuning rates | `SMOKE_TEST=False`, `RUN_STAGE='lr_tuning'` | Unfrozen 8M, rates `1e-7`, `1e-6`, `1e-5`, twenty epochs |
| Split sensitivity | `SMOKE_TEST=False`, `RUN_STAGE='validation_check'` | Frozen 8M, three strategies and seeds 42/43/44 |
| Optional larger model | `SMOKE_TEST=False`, `RUN_STAGE='esm2_150m_check'` | Frozen 150M, `1e-5`, nine epochs |
| Main follow-up suite | `SMOKE_TEST=False`, `RUN_STAGE='all'` | Capacity, learning rates and split sensitivity; excludes optional 150M |

`LR_FROZEN=1e-4` restores the missing frozen-rate setting using the value explicitly recorded for validation sensitivity. The historical capacity table does not separately state its learning rate, so confirm against the original run configuration before claiming an exact capacity-run reproduction.

The former public notebook had an exploratory `1e-7` setting for the optional 150M check. The maintained default now matches the **documented** `1e-5`, nine-epoch result. It does not reinterpret the old exploratory outputs as that result.

All smoke runs still need real data and download/use the selected encoder; they are not instantaneous unit tests. Smoke results must not be reported as full-data results.

## Final held-out evaluation

1. Complete development experiments with the setup flag `RUN_HELDOUT_EVALUATION=False`.
2. Select the final **full-data** configuration and threshold using validation evidence alone.
3. In the final notebook cell only, set `SELECTED_RUN_SUMMARY_PATH` to that run's `run_summary.json` and change its local `RUN_HELDOUT_EVALUATION` assignment to `True`.
4. Run that final cell. Do not rerun training cells with held-out evaluation enabled.

The summary must point to an existing compatible checkpoint. Neither summaries nor weights are bundled. The old hard-coded run identifier was removed because newly generated identifiers and paths may differ. Evaluation keeps the saved validation threshold; it does not tune a new threshold on the held-out sets.

## Checks without private data

```bash
python -m unittest discover -s tests -v
python -c "import pathlib, nbformat; [nbformat.validate(nbformat.read(p, as_version=4)) for p in pathlib.Path('notebooks').glob('*.ipynb')]"
```

The tests compile all code cells, exercise the actual stage factories using configuration extracted from the notebook, check rates and smoke/full epoch counts, and verify that the Drive cell can run without Colab. They intentionally do not load datasets, models or execute training.

Full execution remains a separate validation step after supplying the environment and approved data. Open the follow-up notebook in Jupyter, run the default smoke configuration top-to-bottom, inspect its tables and diagnostics, then restart with the chosen full experiment settings. No browser-rendered notebook inspection or full training execution was performed during maintenance.

## Maintenance changes

- Defined the missing frozen learning rate and restored the documented three-value fine-tuning sweep.
- Made Drive mounting conditional in both notebooks.
- Set a smoke configuration as the follow-up default and made optional 150M smoke runs one epoch.
- Matched the optional 150M full configuration to the recorded result and made epoch labels dynamic.
- Made the selected held-out summary path explicit and removed the old run-specific path.
- Added dependency/data guidance and project-specific ignore rules.
- Preserved the original report, recorded results, figures, model architecture and sampling logic.

The original staged notebook remains a historical workflow, including its older first-character family grouping. Use the follow-up notebook for the corrected family parsing and evaluation safeguards.
