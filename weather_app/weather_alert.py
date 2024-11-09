from twilio.rest import Client
import requests
import schedule
import time
import json
import os


class WeatherApp:
    """
    A class to run the weather alert program.
    """

    def __init__(self, config_file):
        """
        Initialize the weather app with a config JSON file.
        """
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """
        Load configuration from the specified JSON file.
        """
        with open(self.config_file) as config_file:
            return json.load(config_file)

    def get_gridpoint_forecast(self, lat, lon):
        """
        Fetch the gridpoint forecast for the given latitude and longitude.
        """
        base_url = 'https://api.weather.gov/points'
        point_url = f"{base_url}/{lat},{lon}"
        headers = {
            'User-Agent': '(rainy_season_alerts_app, little.ge@yahoo.com)'
        }

        try:
            point_response = requests.get(point_url, headers=headers)
            point_response.raise_for_status()
            point_data = point_response.json()
            forecast_url = point_data['properties']['forecast']
            forecast_response = requests.get(forecast_url, headers=headers)
            forecast_response.raise_for_status()
            return forecast_response.json()['properties']['periods']
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Error occurred: {err}")
        return None

    def check_rain_conditions(self, forecast_data):
        """
        Check if rain conditions meet the criteria for sending an alert.
        """
        for period in forecast_data:
            if 'precipitation' in period['detailedForecast'].lower():
                chance_of_rain = period.get('probabilityOfPrecipitation', {}).get('value', 0)
                rainfall_amount = period.get('quantitativePrecipitation', {}).get('value', 0)

                if chance_of_rain >= 20 or rainfall_amount >= 0.10:
                    return True, period['name'], chance_of_rain, rainfall_amount
        return False, None, 0, 0

    def send_alert(self, to_phone_number, message_body):
        """
        Send an SMS alert using Twilio.
        """
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        twilio_phone_number = self.config['send_phone_number']

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=to_phone_number
        )
        print(f"Message sent: {message.sid}")

    def run_daily_check(self):
        """
        Run the weather check for all configured job sites.
        """
        for i, site in enumerate(self.config['job site']):
            lat = self.config['lat'][i]
            lon = self.config['lon'][i]
            phone_number = self.config['to phone number']

            forecast_data = self.get_gridpoint_forecast(lat, lon)
            if forecast_data:
                condition_met, period_name, chance_of_rain, rainfall_amount = \
                    self.check_rain_conditions(forecast_data)

                if condition_met:
                    message = (
                        f"Reminder: {period_name} has a {chance_of_rain}% chance of rain "
                        f"with {rainfall_amount} inches of expected rainfall.\n"
                        f"Remember to create the rain event report for {site}."
                    )
                    print(message)
                    # self.send_alert(phone_number, message)
                else:
                    print(f"No rain conditions met for {site} today.")
            else:
                print(f"Unable to fetch forecast data for {site}.")

    def schedule_daily(self):
        """
        Schedule the program to run daily using the 'schedule' library.
        """
        schedule.every().day.at("07:00").do(self.run_daily_check)
        print("Weather alerts scheduled. Running daily at 07:00.")

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    prog = WeatherApp("weather_app_config.json")
    prog.run_daily_check()
