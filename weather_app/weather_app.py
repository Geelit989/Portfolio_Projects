from twilio.rest import Client
import requests
import schedule
import time
import json
import os
import logging
import smtplib 
from datetime import datetime, timedelta
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
        # self.twilio_client = self.initiate_twilio_client()
        self.yahoo_user = os.getenv('YMAIL_USER')
        self.yahoo_password = os.getenv('YMAIL_KEY')


    def load_config(self):
        """
        Load configuration from the specified JSON file.
        """
        try:
            with open(self.config_file) as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
        
        
    def initiate_twilio_client(self):
        """
        Initialize the Twilio client with the account SID and auth token.
        """
        try:
            account_sid = os.environ["TWILIO_ACCOUNT_SID"]
            auth_token = os.environ["TWILIO_AUTH_TOKEN"]
            return Client(account_sid, auth_token)
        except Exception as e:
            print(f"Error initializing Twilio client: {e}")
            return None
        

    def get_gridpoint_forecast(self, lat, lon):
        """
        Fetch the gridpoint forecast for the given latitude and longitude.
        """
        base_url = 'https://api.weather.gov/points'
        point_url = f"{base_url}/{lat},{lon}"
        headers = {
            'User-Agent': '(rainy_season_alerts_app, little.ge@yahoo.com)'
        }
        error_messages = {
        404: "Resource not found. Please check if the latitude and longitude are correct.",
        500: "Server error. The weather service may be down. Please try again later.",
        503: "Service unavailable. The weather service is temporarily unavailable."
        }

        # Build functionality that accounts for server timeouts and other errors
        # Retry the request up to 3 times

        try:
            point_response = requests.get(point_url, headers=headers)
            point_response.raise_for_status()
            point_data = point_response.json()
            forecast_url_grid = point_data['properties']['forecastGridData']
            
            forecast_response = requests.get(forecast_url_grid, headers=headers)
            forecast_response.raise_for_status()
            forecast_grid_data = forecast_response.json()['properties']
            logging.info(f"Successfully retrieved data from {point_url}!")
            return forecast_grid_data
        except requests.exceptions.Timeout:
            logging.warning(f'Request to {point_url} timed out! Retrying...')
            # retry logic here...
        except requests.exceptions.HTTPError as http_err:
            status_code = point_response.status_code
            if status_code in error_messages:
                logging.error(error_messages[status_code])
            else:
                logging.error(f"HTTP error {status_code}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Network-related error occurred: {req_err}")
        except Exception as err:
            print(f"Error occurred: {err}")

        return None
    

    def parse_forecast_data(self, forecast_grid_data):
        """
        Parse forecast grid data to extract date, precipitation probability, and quantitative precipitation.
        """
        parsed_data = {
            "date_time": [],
            "probability_of_precipitation": [],
            "quantitative_precipitation": []
        }

        precip_probability_data = forecast_grid_data.get('probabilityOfPrecipitation', {}).get('values', [])
        rainfall_data = forecast_grid_data.get('quantitativePrecipitation', {}).get('values', [])

        for precip, rain in zip(precip_probability_data, rainfall_data):
            parsed_data["date_time"].append(precip.get('validTime'))
            parsed_data["probability_of_precipitation"].append(precip.get('value'))
            parsed_data["quantitative_precipitation"].append(rain.get('value'))

        return parsed_data
    

    def summarize_precipitation_to_6hr_intervals(self, data):
        """
        Summarize precipitation data into 6-hour intervals and structure by day.
        """
        day_summary = defaultdict(list)

        for dt, precip_prob, precip in zip(data["date_time"], 
                                           data["probability_of_precipitation"], 
                                           data["quantitative_precipitation"]):
            datetime_obj = datetime.fromisoformat(dt.split('/')[0])
            day = datetime_obj.strftime('%A')  # Get day of the week
            interval_summary = {
                "avg_precip_prob": precip_prob,
                "total_rainfall": precip
            }
            day_summary[day].append(interval_summary)


        return day_summary
    

    def check_rain_conditions(self, day_summary):
        """
        Check if any day meets the rain conditions for an alert.
        """
        alert_days = []
        for day, intervals in day_summary.items():
            for interval in intervals:
                # Check if any interval within the day meets the alert criteria
                if interval["avg_precip_prob"] >= 50 and interval["total_rainfall"] >= 0.1:
                    alert_days.append(day)
                    break  # No need to check further intervals for this day
        return alert_days
    

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


    def send_sms_via_yahoo(self, to_number, message_body, yahoo_user, yahoo_password):
        """
        Send an SMS via Yahoo Mail's email-to-SMS gateway.

        :param to_number: The recipient's phone number as a string (e.g., '1234567890').
        :param message_body: The message text to send.
        :param yahoo_user: The Yahoo email address for the SMTP server login.
        :param yahoo_password: The password for the Yahoo email login.
        """

        # Email-to-SMS gateway
        to_email = f"{to_number}@vtext.com"  # Verizon example; replace for other carriers as needed

        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = yahoo_user
        msg['To'] = to_email
        msg['Subject'] = "Weather Alert"
        msg.attach(MIMEText(message_body, 'plain'))

        # Yahoo Mail SMTP server details
        smtp_server = 'smtp.mail.yahoo.com'
        smtp_port = 587

        # Connect to the SMTP server and send the message
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(yahoo_user, yahoo_password)
                server.sendmail(yahoo_user, to_email, msg.as_string())
                print("Alert sent successfully!")
        except Exception as e:
            print(f"Failed to send alert: {e}")



    def run_daily_check(self):
        """
        Run the weather check for all configured job sites for the next 7 days.
        """
        for i, site in enumerate(self.config['job site']):
            lat = self.config['lat'][i]
            lon = self.config['lon'][i]
            phone_number = self.config['to phone number']

            forecast_grid_data = self.get_gridpoint_forecast(lat, lon)
            if forecast_grid_data:
                parsed_data = self.parse_forecast_data(forecast_grid_data)
                day_summary = self.summarize_precipitation_to_6hr_intervals(parsed_data)

                alert_days = self.check_rain_conditions(day_summary)

                if alert_days:
                    message = (
                        f"Rain Alert: The following days at {site} have a forecasted rain chance:\n" +
                        "\n".join([f"{day} - 50%+ chance of rain with 0.10+ inches expected" for day in alert_days]) +
                        "\nRemember to create the rain event report!"
                    )
                    print(message)
                    # Uncomment the line below to send the SMS
                    self.send_sms_via_yahoo(phone_number, message, self.yahoo_user, self.yahoo_password)
                else:
                    print(f"No rain conditions met for {site} over the next 7 days.")
            else:
                print(f"Unable to fetch forecast data for {site}.")
                

    def schedule_daily(self):
        """
        Schedule the program to run twice daily at 7:00 AM and 7:00 PM.
        """
        schedule.every().day.at("07:00").do(self.run_daily_check)
        schedule.every().day.at("19:00").do(self.run_daily_check)

        print("Weather alerts scheduled for 7:00 AM and 7:00 PM.")

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    # Set up logging configuration once, ideally at the top of your program
    logging.basicConfig(
        filename="weather_app.log", 
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s"
        )
    
    prog = WeatherApp("weather_app_config.json")
    prog.run_daily_check()
