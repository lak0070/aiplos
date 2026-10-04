# Random Forest evaluation evidence

Random Forest selected at owner request after viewing the previous Ridge results. Fixed parameters chosen for free-hosting resource limits, without tuning on this test set. This reused holdout is a comparison set, not a fresh post-selection test.

Random Forest, fitted only on the training partition; test rows are not used for deployment training.

Training rows: 12392; test rows: 3098. 80/20 questionnaire-group holdout; GroupShuffleSplit random_state=42. 5-fold GroupKFold on the training partition only.

| Model | Train MAE | CV MAE | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|---:|
| Mean baseline | 36.166194 | 36.16747 | 36.268533 | 44.909194 | -0.000683240592689 |
| Linear regression | 2.7219888e-14 | 0.00071343672 | 2.7302456e-14 | 5.5787756e-14 | 1 |
| Ridge (alpha=10) | 0.017166022 | 0.022006276 | 0.017250679 | 0.023732321 | 0.999999720548 |
| Random Forest | 3.257348 | 7.1595457 | 6.8115111 | 8.8590767 | 0.961059364318 |

Linear regression reproduces this holdout target to floating-point precision. This is strong empirical evidence of a questionnaire-derived score, not near-perfect prediction of real-world wellbeing. No authoritative scoring formula was verified in this evaluation. These results do not establish future wellbeing prediction, causality, or performance on a new population. Timestamp features remain in the original pipeline; no future-time holdout was performed. Respondent IDs are unavailable, so repeated respondents cannot be ruled out.

Random Forest is less accurate on this score than Ridge. Switching estimators does not fix the formula-derived target issue. R² is not classification accuracy.

Parameters: {'n_estimators': 150, 'max_depth': 16, 'min_samples_leaf': 3, 'random_state': 42, 'n_jobs': 1}

Random Forest test MAE 95% bootstrap interval: [6.603373169760913, 7.010757485459988]. Conditional on this fitted model and split; 1,000 row resamples.

Run `python evaluate_model.py` to regenerate the summary, prediction evidence, split manifest and production artifact. Preprocessing is fitted within each training fold. The target is excluded; identical questionnaire groups do not cross partitions. Deployment retains only training-partition fitting.

Dataset SHA-256: 80f6176284139a960c1c402f4b1d43bc9826f70a49e61a977a4606057bd6a104

Versions: {'python': '3.12.14', 'numpy': '2.3.5', 'pandas': '2.2.3', 'scikit_learn': '1.8.0'}

The live evaluation endpoint contains metrics generated during its deployment build; small numerical differences across dependency versions are possible.
