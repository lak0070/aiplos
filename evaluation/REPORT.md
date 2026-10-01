# Model evaluation evidence

This report evaluates the existing Ridge alpha=10 estimator without choosing parameters on the test set.

Original rows: 15972; duplicates removed: 482; training rows: 12392; holdout rows: 3098.

Identical questionnaire answers are grouped before the 80/20 split (seed 42), ignoring timestamp and target when identifying groups. Five-fold grouped cross-validation uses only the training partition. All imputation, scaling, and encoding are fitted within the respective training partitions. Engineered features are row-local and exclude the target.

| Model | Train MAE | CV MAE (mean ± SD) | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|---:|
| Mean baseline | 36.1661944 | 36.1674697 ± 0.347548978 | 36.2685328 | 44.9091938 | -0.000683240592689 |
| Linear regression | 2.72198876e-14 | 0.000713436722 ± 0.00142687344 | 2.73024555e-14 | 5.57877561e-14 | 1 |
| Ridge (alpha=10) | 0.0171660215 | 0.0220062755 ± 0.00164524673 | 0.0172506786 | 0.0237323213 | 0.999999720548 |

MAE and RMSE are in original score points, not the dashboard 0–100 display scale. R² is not a classification accuracy percentage.

Linear regression reproduces this holdout target to floating-point precision. This is strong empirical evidence of a questionnaire-derived score, not near-perfect prediction of real-world wellbeing. No authoritative scoring formula was verified in this evaluation. These results do not establish future wellbeing prediction, causality, or performance on a new population. Timestamp features remain in the original pipeline; no future-time holdout was performed. Respondent IDs are unavailable, so repeated respondents cannot be ruled out.

## Reproduce

Run `python evaluate_model.py` from the repository root. The script generates summary.json, holdout_predictions.csv, split_manifest.csv under evaluation/, and saves a Ridge pipeline fitted on training rows only. Render runs the same evaluation during each build. The website displays the metrics produced by that deployed build; minor numerical differences across library versions are possible.

The versioned CSV files provide per-row evidence from this run without exposing the full questionnaire responses. Clean row indices refer to the deduplicated, valid-target data in source order. The dataset hash and dependency versions are recorded in summary.json.

No external-population, future-time, subgroup-fairness or clinical validation was performed. No respondent identifiers exist to exclude multiple responses by one person. The bootstrap interval is conditional on the fixed split and fitted model, not a population guarantee.
