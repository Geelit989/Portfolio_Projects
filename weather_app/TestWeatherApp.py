# test_weather_app.py
import unittest
from weather_app import WeatherApp
from unittest.mock import patch

class TestWeatherApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the WeatherApp with a test configuration file
        cls.app = WeatherApp("test_config.json")

    def test_load_config(self):
        """
        Test that the configuration loads correctly.
        """
        config = self.app.config
        self.assertIsNotNone(config, "Config should not be None")
        self.assertIn("job site", config, "Config should contain 'job site' key")
    
    @patch('requests.get')
    def test_get_gridpoint_forecast(self, mock_get):
        """
        Test fetching gridpoint forecast from the API.
        """
        mock_response_data = {
            "properties": {
                "forecastGridData": "https://api.weather.gov/gridpoints/MOCK"
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        lat, lon = 33.49463, -117.1474
        result = self.app.get_gridpoint_forecast(lat, lon)
        self.assertIsNotNone(result, "Forecast data should not be None")

    def test_parse_forecast_data(self):
        """
        Test parsing of forecast data for precipitation and quantitative precipitation.
        """
        sample_forecast_data = {
            'probabilityOfPrecipitation': {'values': [{'validTime': '2023-11-04T06:00:00+00:00', 'value': 60}]},
            'quantitativePrecipitation': {'values': [{'validTime': '2023-11-04T06:00:00+00:00', 'value': 0.1}]}
        }
        parsed_data = self.app.parse_forecast_data(sample_forecast_data)
        self.assertEqual(parsed_data['probability_of_precipitation'][0], 60, "Precipitation probability should be 60")
        self.assertEqual(parsed_data['quantitative_precipitation'][0], 0.1, "Quantitative precipitation should be 0.1")

    def test_summarize_precipitation_to_6hr_intervals(self):
        """
        Test summarization of precipitation data into 6-hour intervals.
        """
        sample_data = {
            "date_time": ["2023-11-04T06:00:00+00:00/PT6H"],
            "probability_of_precipitation": [60],
            "quantitative_precipitation": [0.1]
        }
        day_summary = self.app.summarize_precipitation_to_6hr_intervals(sample_data)
        self.assertIn('Saturday', day_summary, "Saturday should be in day summary")
        self.assertEqual(day_summary['Saturday'][0]['avg_precip_prob'], 60, "Average precip probability should be 60")

    def test_check_rain_conditions(self):
        """
        Test if rain conditions meet the threshold for sending an alert.
        """
        day_summary = {
            'Monday': [{'avg_precip_prob': 60, 'total_rainfall': 0.2}],
            'Tuesday': [{'avg_precip_prob': 20, 'total_rainfall': 0.05}]
        }
        alert_days = self.app.check_rain_conditions(day_summary)
        self.assertIn('Monday', alert_days, "Monday should be an alert day")
        self.assertNotIn('Tuesday', alert_days, "Tuesday should not be an alert day")

    @patch('smtplib.SMTP')
    def test_send_sms_via_yahoo(self, mock_smtp):
        """
        Test sending SMS alert via Yahoo email-to-SMS gateway.
        """
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.return_value = {}

        to_number = "1234567890"
        message_body = "Test Alert"
        result = self.app.send_sms_via_yahoo(to_number, message_body)
        mock_smtp_instance.sendmail.assert_called_once()
        print("SMS via Yahoo test passed.")

    @classmethod
    def tearDownClass(cls):
        # Perform cleanup if necessary
        print("Cleanup after tests")

if __name__ == "__main__":
    unittest.main()
