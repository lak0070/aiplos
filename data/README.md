# Dataset notes

[Back to README](../README.md)

`wellbeing.csv` is the supplied Wellbeing and Lifestyle dataset used for training. The source filename supplied with the project was `Wellbeing_and_lifestyle_data_Kaggle(1).csv`. The original publisher, collection methodology, source URL and redistribution licence have not been independently verified in this repository. Do not invent attribution or treat public GitHub access as permission to reuse the dataset.

The recorded evaluation contains 15,972 input records and 15,490 after removing 482 duplicates. The target is `WORK_LIFE_BALANCE_SCORE`.

## Input schema

`Timestamp` is used for date features; `AGE` accepts `Less than 20`, `21 to 35`, `36 to 50`, `51 or more`; `GENDER` accepts the dataset categories `Female` and `Male`.

Numeric questionnaire values are whole numbers. The application's accepted ranges are:

| Range | Fields |
|---|---|
| 0–5 | `FRUITS_VEGGIES`, `DONATION` |
| 1–2 | `BMI_RANGE`, `SUFFICIENT_INCOME` |
| 0–10 | `DAILY_STRESS`, `PLACES_VISITED`, `CORE_CIRCLE`, `SUPPORTING_OTHERS`, `SOCIAL_NETWORK`, `ACHIEVEMENT`, `TODO_COMPLETED`, `FLOW`, `DAILY_STEPS`, `LIVE_VISION`, `SLEEP_HOURS`, `LOST_VACATION`, `DAILY_SHOUTING`, `PERSONAL_AWARDS`, `TIME_FOR_PASSION`, `WEEKLY_MEDITATION` |

These are the implemented survey scales, not independently validated health recommendations. See `model.BOUNDS` for the executable schema and `static/app.js` for displayed field labels.

`name` is a display-only API field and is not used by the model. At prediction time the backend supplies today's date; a client-provided timestamp does not override it.

The generated `random_forest_life_os_model.joblib` is ignored by Git and recreated during the build. Load joblib artifacts only from trusted sources; deserialization can execute code.
