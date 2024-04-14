from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib

# Load and prepare data
data = pd.read_csv('historical_data.csv')
X = data.drop('target', axis=1)
y = data['target']

# Train the RandomForest model
model = RandomForestRegressor()
model.fit(X, y)

# Save the trained model to a file
joblib.dump(model, 'path/to/django/app/media/demand_forecast_model.joblib')

