from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

class PredictionTests(TestCase):
    @patch('yourapp.apps.InventoryConfig.get_forecast_model')
    def test_predict_view(self, mock_get_model):
        mock_model = mock_get_model.return_value
        mock_model.predict.return_value = [42]  # Assuming your model returns a list

        response = self.client.get(reverse('predict-url-name'), {'feature1': 10, 'feature2': 20})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'prediction': [42]})
