from pathlib import Path
import model
model.SOURCE=Path(__file__).parent/'data'/'wellbeing.csv'
model.ARTIFACT=Path(__file__).parent/'data'/'ridge_life_os_model.joblib'
model.train_model()
print('Ridge pipeline trained for deployment.')
