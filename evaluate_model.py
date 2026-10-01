"""Reproducible grouped holdout evaluation; no test-set model selection."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import model

ROOT = Path(__file__).resolve().parent

def metrics(y, pred):
    return dict(mae=float(mean_absolute_error(y, pred)), rmse=float(np.sqrt(mean_squared_error(y, pred))), r2=float(r2_score(y, pred)))

def run():
    source = ROOT/'data/wellbeing.csv'
    raw = pd.read_csv(source)
    clean = raw.drop_duplicates().copy()
    clean[model.TARGET] = pd.to_numeric(clean[model.TARGET], errors='coerce')
    invalid_targets = int(clean[model.TARGET].isna().sum())
    clean = clean.dropna(subset=[model.TARGET]).reset_index(drop=True)
    # Group identical questionnaire responses, regardless of timestamp/target.
    group_cols = list(model.BOUNDS) + ['AGE', 'GENDER']
    groups = pd.util.hash_pandas_object(clean[group_cols], index=False).to_numpy()
    train, test = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(clean, groups=groups))
    assert not set(groups[train]) & set(groups[test])
    X = model.engineer(clean, include_target=False)
    assert model.TARGET not in X.columns
    y = clean[model.TARGET]
    ridge = model.build_pipeline(X)
    linear = clone(ridge).set_params(ridge=LinearRegression())
    candidates = [('Mean baseline', DummyRegressor(strategy='mean')), ('Linear regression', linear), ('Ridge (alpha=10)', ridge)]
    rows = []
    prediction_columns = {'source_row_after_cleaning': test, 'actual': y.iloc[test].to_numpy()}
    fitted_ridge = None
    for name, estimator in candidates:
        cv = cross_validate(estimator, X.iloc[train], y.iloc[train], groups=groups[train], cv=GroupKFold(5), scoring={'mae':'neg_mean_absolute_error','rmse':'neg_root_mean_squared_error','r2':'r2'}, n_jobs=1)
        estimator.fit(X.iloc[train], y.iloc[train])
        pred = estimator.predict(X.iloc[test])
        row = {'model':name, 'train':metrics(y.iloc[train],estimator.predict(X.iloc[train])), 'test':metrics(y.iloc[test],pred), 'cv':{k:{'mean':float(np.mean(cv['test_'+k])*(-1 if k!='r2' else 1)), 'std':float(np.std(cv['test_'+k])), 'fold_values':(cv['test_'+k]*(-1 if k!='r2' else 1)).tolist()} for k in ['mae','rmse','r2']}}
        rows.append(row)
        prediction_columns[name] = pred
        if name.startswith('Ridge'):
            fitted_ridge = estimator
            rng = np.random.default_rng(42)
            errors = np.abs(y.iloc[test].to_numpy()-pred)
            boots = [np.mean(errors[rng.integers(0,len(errors),len(errors))]) for _ in range(1000)]
            row['mae_bootstrap_95_ci'] = [float(v) for v in np.quantile(boots,[.025,.975])]
    audit = {
        'target_excluded_from_features': True,
        'identical_questionnaire_group_overlap': 0,
        'preprocessing_fitted_inside_each_training_fold': True,
        'invalid_daily_stress_values': int(pd.to_numeric(clean.DAILY_STRESS,errors='coerce').isna().sum()),
        'caution': 'Linear regression reproduces this holdout target to floating-point precision. This is strong empirical evidence of a questionnaire-derived score, not near-perfect prediction of real-world wellbeing. No authoritative scoring formula was verified in this evaluation. These results do not establish future wellbeing prediction, causality, or performance on a new population. Timestamp features remain in the original pipeline; no future-time holdout was performed. Respondent IDs are unavailable, so repeated respondents cannot be ruled out.'
    }
    report = {'generated_utc':datetime.now(timezone.utc).isoformat(), 'dataset_sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'raw_rows':len(raw), 'duplicates_removed':int(raw.duplicated().sum()), 'invalid_targets_removed':invalid_targets, 'clean_rows':len(clean), 'train_rows':len(train), 'test_rows':len(test), 'unique_questionnaire_groups':len(np.unique(groups)), 'split':'80/20 questionnaire-group holdout; GroupShuffleSplit random_state=42', 'cv_method':'5-fold GroupKFold on the training partition only', 'selection':'Existing Ridge alpha=10 retained; no tuning or selection using holdout results. Linear regression is a comparator.', 'deployed_model':'Ridge (alpha=10), fitted only on the training partition; test rows are not used for deployment training.', 'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scikit_learn':sklearn.__version__}, 'metrics':rows,'audit':audit}
    out=ROOT/'evaluation';out.mkdir(exist_ok=True)
    (out/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    pd.DataFrame(prediction_columns).to_csv(out/'holdout_predictions.csv',index=False)
    pd.DataFrame({'clean_row':np.arange(len(clean)), 'partition':np.where(np.isin(np.arange(len(clean)),test),'test','train')}).to_csv(out/'split_manifest.csv',index=False)
    model.joblib.dump({'pipeline':fitted_ridge,'metadata':{'model':'Ridge(alpha=10.0)','target':model.TARGET,'training_rows':len(train),'test_rows':len(test),'evaluation':'evaluation/summary.json','feature_columns':list(X.columns)}},ROOT/'data/ridge_life_os_model.joblib')
    print(json.dumps({'train_rows':len(train),'test_rows':len(test),'metrics':rows},indent=2))
    return report

if __name__=='__main__':run()
