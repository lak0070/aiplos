#!/usr/bin/env python3
"""Train and interactively use the Life OS Random Forest regressor.

Usage:
  python3 model.py --train-only
  python3 model.py

This predicts WORK_LIFE_BALANCE_SCORE from the supplied Kaggle survey schema.
It is a baseline score estimator, not a medical, financial, or mental-health diagnosis.
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'data' / 'wellbeing.csv'
ARTIFACT = ROOT / 'data' / 'random_forest_life_os_model.joblib'
MODEL_NAME = 'Random Forest'
RF_PARAMS = dict(n_estimators=150, max_depth=16, min_samples_leaf=3, random_state=42, n_jobs=1)
TARGET = 'WORK_LIFE_BALANCE_SCORE'

BOUNDS = {
    'FRUITS_VEGGIES': (0, 5), 'DAILY_STRESS': (0, 10), 'PLACES_VISITED': (0, 10),
    'CORE_CIRCLE': (0, 10), 'SUPPORTING_OTHERS': (0, 10), 'SOCIAL_NETWORK': (0, 10),
    'ACHIEVEMENT': (0, 10), 'DONATION': (0, 5), 'BMI_RANGE': (1, 2),
    'TODO_COMPLETED': (0, 10), 'FLOW': (0, 10), 'DAILY_STEPS': (0, 10),
    'LIVE_VISION': (0, 10), 'SLEEP_HOURS': (0, 10), 'LOST_VACATION': (0, 10),
    'DAILY_SHOUTING': (0, 10), 'SUFFICIENT_INCOME': (1, 2), 'PERSONAL_AWARDS': (0, 10),
    'TIME_FOR_PASSION': (0, 10), 'WEEKLY_MEDITATION': (0, 10),
}
AGE_OPTIONS = ['Less than 20', '21 to 35', '36 to 50', '51 or more']
GENDER_OPTIONS = ['Female', 'Male']


def engineer(df: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
    """Match the feature construction used during EDA/model evaluation."""
    out = df.copy()
    out['DAILY_STRESS'] = pd.to_numeric(out['DAILY_STRESS'], errors='coerce')
    out['Timestamp'] = pd.to_datetime(out['Timestamp'], errors='coerce')
    for col, (low, high) in BOUNDS.items():
        bad = (~out[col].between(low, high)) & out[col].notna()
        out.loc[bad, col] = np.nan

    out['timestamp_year'] = out['Timestamp'].dt.year
    out['timestamp_month'] = out['Timestamp'].dt.month
    out['timestamp_dayofweek'] = out['Timestamp'].dt.dayofweek
    out['age_midpoint'] = out['AGE'].map({'Less than 20': 16, '21 to 35': 28, '36 to 50': 43, '51 or more': 60})
    out['gender_male'] = out['GENDER'].map({'Male': 1, 'Female': 0})

    def avg(cols):
        return out[cols].mean(axis=1, skipna=True)
    out['health_routine_index'] = avg(['FRUITS_VEGGIES', 'DAILY_STEPS', 'SLEEP_HOURS', 'WEEKLY_MEDITATION'])
    out['social_support_index'] = avg(['CORE_CIRCLE', 'SUPPORTING_OTHERS', 'SOCIAL_NETWORK'])
    out['productivity_flow_index'] = avg(['TODO_COMPLETED', 'FLOW', 'ACHIEVEMENT', 'TIME_FOR_PASSION'])
    out['financial_security_index'] = avg(['SUFFICIENT_INCOME'])
    out['stress_burden_index'] = avg(['DAILY_STRESS', 'LOST_VACATION', 'DAILY_SHOUTING'])
    out['sleep_stress_interaction'] = out['SLEEP_HOURS'] * (10 - out['DAILY_STRESS'])
    out['flow_passion_interaction'] = out['FLOW'] * out['TIME_FOR_PASSION']
    out['social_achievement_interaction'] = out['SOCIAL_NETWORK'] * out['ACHIEVEMENT']
    out = out.drop(columns=['Timestamp'])
    if not include_target and TARGET in out:
        out = out.drop(columns=[TARGET])
    return out


def build_pipeline(X: pd.DataFrame, estimator=None) -> Pipeline:
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical = X.select_dtypes(exclude=[np.number]).columns.tolist()
    preprocess = ColumnTransformer([
        ('numeric', Pipeline([
            ('imputer', SimpleImputer(strategy='median', add_indicator=True)),
            ('scaler', StandardScaler()),
        ]), numeric),
        ('categorical', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]), categorical),
    ], remainder='drop')
    return Pipeline([('preprocess', preprocess), ('regressor', RandomForestRegressor(**RF_PARAMS) if estimator is None else estimator)])


def train_model() -> dict:
    # One training path preserves the held-out partition, including local startup.
    from evaluate_model import run
    run()
    return joblib.load(ARTIFACT)['metadata']


def ask_number(name: str, low: int, high: int) -> int:
    while True:
        raw = input(f'{name} ({low}-{high}): ').strip()
        try:
            value = int(raw)
            if low <= value <= high:
                return value
        except ValueError:
            pass
        print(f'Please enter a whole number from {low} to {high}.')


def ask_choice(name: str, options: list[str]) -> str:
    print(f'Choose {name}:')
    for i, option in enumerate(options, start=1):
        print(f'  {i}. {option}')
    while True:
        raw = input('Enter number: ').strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print('Please choose one of the listed numbers.')


def collect_user_row() -> pd.DataFrame:
    print('\nEnter your details. Numeric questions use the same scale as the dataset.\n')
    row = {'Timestamp': input(f'Timestamp [{date.today().isoformat()}]: ').strip() or date.today().isoformat()}
    row['AGE'] = ask_choice('age range', AGE_OPTIONS)
    row['GENDER'] = ask_choice('gender', GENDER_OPTIONS)
    for col, (low, high) in BOUNDS.items():
        labels = {
            'FRUITS_VEGGIES': 'Fruits and vegetables', 'DAILY_STRESS': 'Daily stress',
            'PLACES_VISITED': 'Places visited', 'CORE_CIRCLE': 'Core circle',
            'SUPPORTING_OTHERS': 'Supporting others', 'SOCIAL_NETWORK': 'Social network',
            'ACHIEVEMENT': 'Achievement', 'DONATION': 'Donation', 'BMI_RANGE': 'BMI range code (1 or 2)',
            'TODO_COMPLETED': 'To-do items completed', 'FLOW': 'Flow', 'DAILY_STEPS': 'Daily steps level',
            'LIVE_VISION': 'Life vision clarity', 'SLEEP_HOURS': 'Sleep hours level',
            'LOST_VACATION': 'Lost vacation days level', 'DAILY_SHOUTING': 'Daily shouting/stress expression',
            'SUFFICIENT_INCOME': 'Sufficient income code (1 or 2)', 'PERSONAL_AWARDS': 'Personal awards',
            'TIME_FOR_PASSION': 'Time for passion', 'WEEKLY_MEDITATION': 'Weekly meditation',
        }
        row[col] = ask_number(labels.get(col, col), low, high)
    return pd.DataFrame([row])


def band(score: float) -> str:
    if score < 636:
        return 'lower range in this dataset'
    if score < 698.5:
        return 'middle range in this dataset'
    return 'higher range in this dataset'


def main():
    print("=" * 60)
    print("AI PERSONAL LIFE OS - RANDOM FOREST REGRESSION")
    print("=" * 60)

    # Train the model.
    if ARTIFACT.exists():
        print("\nLoading saved Random Forest model...")
        bundle = joblib.load(ARTIFACT)
        metadata = bundle["metadata"]
        print(f"Model trained on {metadata['training_rows']:,} cleaned rows.")
    else:
        print("\nTraining Random Forest Regression model...")
        metadata = train_model()
        print(f"Model trained on {metadata['training_rows']:,} cleaned rows.")
        print(f"Saved model to: {ARTIFACT}")

    print("\nDo you want to enter your own details and get a prediction?")
    choice = input("Enter yes or no: ").strip().lower()

    if choice != "yes":
        print("\nTraining finished. Model file is saved.")
        return

    bundle = joblib.load(ARTIFACT)

    # Collect one user's information.
    user_data = collect_user_row()

    # Convert user input into the same features used during training.
    user_features = engineer(user_data, include_target=False)

    # Predict work-life balance score.
    prediction = float(
        bundle["pipeline"].predict(user_features)[0]
    )

    print("\n" + "=" * 60)
    print(f"Predicted Work-Life Balance Score: {prediction:.2f}")
    print(f"Interpretation: {band(prediction)}")
    print("=" * 60)

    print("\nNote:")
    print("This is a baseline score estimate from the survey dataset.")
    print("It is not a medical diagnosis or a guaranteed prediction.")
    print("The target appears to be formula-derived from the survey inputs.")


if __name__ == '__main__':
    main()
