# Sequential Binary Follow-up Results

Date: 2026-07-21

Updated: 2026-07-30 to include the later optional frozen ESM2 150M follow-up check.

This document summarises the completed v2 follow-up experiments from:

```text
sequential_binary_followup_v2/sequential_binary_followup_v2/
```

It is a results-summary artifact, not a full report draft. The held-out sets were evaluated only after selecting a final configuration from validation evidence.

## Executive Summary

The strongest validation-selected follow-up configuration was:

```text
model: facebook/esm2_t6_8M_UR50D
architecture: unfrozen_esm
clustering: no_clustering
negative sampling: cross_family
learning rate: 1e-5
validation split: code_group_random
split seed: 42
training seed: 42
pair generation seed: 4242
validation MCC: 0.4681
validation threshold: 0.10
```

This supports fine-tuning as the strongest validation direction among the completed follow-up runs. However, the final held-out evaluation remained much weaker than validation performance, especially for singleton proteases.


## Model Capacity

Fixed settings:

```text
clustering: no_clustering
negative sampling: cross_family
architecture: frozen_esm
validation split: code_group_random
split seed: 42
epochs: 20
effective batch size: 4
```

| Model | Architecture | Validation MCC | Threshold | Validation codes | Validation positives | Validation negatives |
|---|---|---:|---:|---:|---:|---:|
| `facebook/esm2_t6_8M_UR50D` | frozen ESM | 0.1914 | 0.40 | 54 | 6441 | 5831 |
| `facebook/esm2_t12_35M_UR50D` | frozen ESM | 0.1961 | 0.55 | 54 | 6441 | 5831 |

The frozen 35M model only slightly improved over the corrected frozen 8M baseline. This does not provide strong evidence that frozen backbone scaling alone solves the task.

### Optional Frozen ESM2 150M Check

A later optional frozen ESM2 150M follow-up was completed after the main v2 loop. This was added as a practical model-capacity check following the supervisor discussion about testing a larger backbone while avoiding the long runtime of unfrozen 150M fine-tuning.

Fixed settings matched the v2 capacity setup where possible:

```text
model: facebook/esm2_t30_150M_UR50D
architecture: frozen_esm
clustering: no_clustering
negative sampling: cross_family
validation split: code_group_random
split seed: 42
training seed: 42
pair generation seed: 4242
epochs: 9
physical batch size: 1
gradient accumulation steps: 4
effective batch size: 4
```

| Model | Architecture | Epochs | Learning rate | Validation MCC | Threshold | ROC AUC | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| `facebook/esm2_t30_150M_UR50D` | frozen ESM | 9 | `1e-5` | 0.0834 | 0.40 | 0.5486 | 0.6264 |

This result did not improve over the frozen 8M or frozen 35M checks. Because it used 9 epochs rather than the 20-epoch model-capacity runs, it should be reported as additional follow-up evidence rather than a direct replacement for the original v2 capacity comparison. The 150M model was not selected for held-out evaluation.

## Learning-rate Tuning

Fixed settings:

```text
model: facebook/esm2_t6_8M_UR50D
architecture: unfrozen_esm
clustering: no_clustering
negative sampling: cross_family
validation split: code_group_random
split seed: 42
epochs: 20
effective batch size: 4
```

| Learning rate | Validation MCC | Threshold |
|---:|---:|---:|
| `1e-7` | 0.1230 | 0.35 |
| `1e-6` | 0.3354 | 0.10 |
| `1e-5` | 0.4681 | 0.10 |

The best completed fine-tuning run was the unfrozen 8M model at `1e-5`. Lower learning rates reduced validation MCC in this setup.

## Validation Split Sensitivity

Fixed settings:

```text
model: facebook/esm2_t6_8M_UR50D
architecture: frozen_esm
clustering: no_clustering
negative sampling: cross_family
learning rate: 1e-4
split seeds: 42, 43, 44
epochs per run: 20
```

| Validation split strategy | Mean MCC | Std MCC | Min MCC | Max MCC | Mean validation codes | Fallback frequency |
|---|---:|---:|---:|---:|---:|---:|
| `code_group_random` | 0.2272 | 0.0729 | 0.1791 | 0.3111 | 54 | 0.0 |
| `family_stratified_code` | 0.2296 | 0.0329 | 0.1983 | 0.2640 | 58 | 0.0 |
| `family_abundance_stratified_code` | 0.3915 | 0.1350 | 0.2406 | 0.5006 | 62 | 0.0 |

The validation split design materially affected validation MCC. The abundance-stratified split gave the highest mean MCC, but also the highest variability. These runs should be treated as validation sensitivity analysis rather than a competition to choose the split with the highest MCC. Family-aware splitting tests unseen protease codes within represented MEROPS families; it does not test generalisation to entirely unseen MEROPS families.

## Final Held-out Evaluation

Held-out evaluation was run manually for the validation-selected configuration:

```text
run: lr_tuning_esm2_8m_unfrozen_aaea37e3
model: facebook/esm2_t6_8M_UR50D
architecture: unfrozen_esm
learning rate: 1e-5
validation threshold: 0.10
used_for_selection: false
selected_by_validation_only: true
```

| Held-out set | Rows | MCC | Precision | Recall | F1 | Accuracy | ROC AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| `test_1_sample` | 254 | 0.0241 | 0.5098 | 0.6142 | 0.5571 | 0.5118 | 0.5435 |
| `test_2_to_10_samples` | 3655 | 0.2549 | 0.5912 | 0.7171 | 0.6481 | 0.6227 | 0.6719 |

The singleton held-out set remained close to random by MCC. The 2-to-10-sample held-out set retained a clearer non-random signal, but it was still substantially lower than validation performance.

