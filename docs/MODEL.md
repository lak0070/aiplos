# Model and validation guide

[Back to README](../README.md)

## Prediction task

Predict numeric `WORK_LIFE_BALANCE_SCORE` from survey responses. This is regression, not classification. The deployed estimator is `RandomForestRegressor` with 150 trees, maximum depth 16, minimum 3 samples per leaf, random seed 42 and one training job.

## Feature processing

`model.engineer` is stateless: it converts stress/date values, marks out-of-range numeric values missing, extracts year/month/weekday, maps age and gender into numeric features, creates five composite indices and three interactions, and drops the raw timestamp. Prediction/evaluation calls exclude the target.

The fitted pipeline uses median numeric imputation with missing indicators, standardisation, most-frequent categorical imputation and one-hot encoding with unknown categories ignored. Scaling is retained for a shared comparison pipeline; trees generally do not need it. Original age/gender categories remain alongside their engineered numeric representations.

## Split and leakage controls

1. Remove exact duplicates before splitting: 15,972 raw rows, 482 duplicates, 15,490 cleaned rows in the recorded run.
2. Coerce targets to numeric and remove missing targets.
3. Hash the 20 numeric questionnaire columns plus age and gender to group identical responses, excluding timestamp and target from group identity.
4. Use `GroupShuffleSplit(test_size=0.2, random_state=42)` and assert no group overlap.
5. Exclude the target from predictors. Feature engineering uses row-local operations and no learned statistics.
6. Fit imputation, encoding and scaling inside each training fold using a pipeline and five-fold `GroupKFold`.
7. Fit each estimator on the training partition and evaluate the shared holdout. Save only the fitted training-partition Random Forest.

The 80/20 proportion is a group split, so row counts can differ with another dataset. Parameters were fixed, not optimized through a hyperparameter search.

## Evidence files

Read [the report](../evaluation/REPORT.md) for recorded values. `summary.json` includes training/test/CV metrics, five fold values, package versions, dataset SHA-256 and a 1,000-resample bootstrap interval for Random Forest test MAE. That interval is conditional on the fitted model and split; it is not a population-wide guarantee.

`holdout_predictions.csv` connects cleaned row IDs to actual and predicted values. `split_manifest.csv` records each cleaned row's assignment. Re-run `python evaluate_model.py` to regenerate these and the deployed model artifact.

## Limitations

- Near-exact Linear Regression predictions suggest a questionnaire-derived target; the authoritative formula has not been verified.
- Random Forest performs worse than Ridge on this score. A lower R² is not itself evidence that leakage has been fixed.
- The holdout was reused after earlier results informed the request to change models. A fresh final test is needed for an independent post-selection assessment.
- No respondent IDs are available, so repeated respondents with different responses cannot be excluded.
- Timestamp features remain; no future-time holdout or external population validation was performed.
- Categories and ranges reflect the supplied dataset and may not represent all users.
- Correlation, recommendations and feature coefficients do not establish causal effects. SHAP is not implemented.

Report MAE and RMSE in score points and R² as a regression metric, never as a classification accuracy percentage.
