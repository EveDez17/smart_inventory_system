from django.core.management.base import BaseCommand
import joblib
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class Command(BaseCommand):
    help = 'Trains a model and saves it to a file'

    def handle(self, *args, **options):
        data = pd.read_csv('path/to/historical_data.csv')
        X = data.drop('target', axis=1)
        y = data['target']
        
        model = RandomForestRegressor()
        model.fit(X, y)
        
        model_path = 'path/to/model.joblib'
        joblib.dump(model, model_path)
        self.stdout.write(self.style.SUCCESS('Successfully trained model.'))
