# Data requirements and boundaries

The original MEROPS-derived datasets are not distributed in this public repository. Obtain the approved processed inputs through the original project arrangements; do not substitute fabricated data and label it as a reproduction.

## Required directory

Set `PROJECT_ROOT_OVERRIDE` in the notebook to the folder containing `processed_data/`.

| Path beneath that folder | Purpose |
| --- | --- |
| `processed_data/training.csv` | Development positives |
| `processed_data/test_1_sample.csv` | Held-out positives for singleton proteases |
| `processed_data/test_2_to_10_samples.csv` | Held-out positives for 2–10-sample proteases |
| `processed_data/training_8mer_clustering.csv` | Required only for the 8-mer condition in the historical workflow |
| `processed_data/training_p1_clustering.csv` | Optional precomputed P1 selection; the notebooks can construct a P1 selection internally |

Both held-out files are loaded during setup for code exclusion and positive-pair blocking, even while held-out **model evaluation** is disabled. The model metrics on these sets are reserved for final evaluation.

## Required columns

| Column | Meaning |
| --- | --- |
| `code` | MEROPS protease identifier; treated as a string |
| `site` | Cleavage-site sequence, intended as an eight-residue window |
| `protease` | Protease amino-acid sequence |
| `cleavage_type` | Cleavage annotation; the P1 selection uses `physiological`, `pathological` and `non-physiological` values |

An optional `cleavageID` supports the historical P1 deduplication logic. The follow-up derives full protease codes, MEROPS classes and family prefixes. These identifiers are not interchangeable: for example, `S01.151` is a code, `S` a class and `S01` a family.

The loaders normalise code/site strings and drop missing codes, sites and protease sequences. These cleaning steps are not a complete biological input validation. Check sequence alphabet, cleavage-window definition, duplicate annotations and provenance before introducing new inputs.

## Sampling and interpretation

Positive examples are observed pairs. Negative strategies scramble the cleavage site, draw a site from the partition's candidate pool, draw across MEROPS families, or mix these strategies. Candidate negatives are checked against known positive code–site pairs. A lack of an observed interaction does not prove absence of cleavage.

The desired ratio is one negative per positive, but failed sampling and deduplication can change the final balance. The recorded held-out evaluation sizes (254 and 3,655 rows) are final binary pair counts, not simply counts of original positive annotations. Run diagnostics record the actual balance.

The follow-up blocks exact code–site overlap and splits on protease code. This does not establish that homologous sequences or individual cleavage-site sequences are disjoint. Original extraction/preprocessing scripts and an independently redistributable dataset are not supplied, so downloading generic MEROPS data alone does not establish an exact reproduction.

## Public artifacts

Raw/processed datasets, pair-level predictions, generated manifests containing sequences and model weights remain excluded. Aggregate results and existing figures are available under `reports/`. Project-specific ignore rules cover the normal data, output and checkpoint paths; review files before committing anything stored elsewhere.
