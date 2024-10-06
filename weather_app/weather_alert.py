!pip install requests twilio schedule

from twilio.rest import Client
import requests
import schedule
import time
import json

def get_gridpoint_forecast(lat, lon):
    """
    Fetch the gridpoint forecast for the given latitude and longitude.
    """
    base_url = 'https://api.weather.gov/points'
    point_url = f"{base_url}/{lat},{lon}"
    headers = {
        'User-Agent': '(rainy_season_alerts_app, little.ge@yahoo.com)'
    }

    # Fetch grid data using the /points endpoint
    try:
        point_response = requests.get(point_url, headers=headers)
        point_response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Error occurred: {err}")
        return None

    point_data = point_response.json()

    # Retrieve forecast URL from the grid data
    forecast_url = point_data['properties']['forecast']

    # Fetch the forecast data
    try:
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()
        return forecast_response.json()['properties']['periods']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Error occurred: {err}")

    return None
latitude = 30.4383
longitude = -84.2807

forecast_data = get_gridpoint_forecast(latitude, longitude)

if forecast_data:
    for period in forecast_data:
        print(f"{period['name']}: {period['detailedForecast']}")
def check_rain_conditions(forecast_data):
    for period in forecast_data:
        if 'showers' in period['detailedForecast'].lower():
            chance_of_rain = period.get('probabilityOfPrecipitation', {}).get('value', 0)
            rainfall_amount = period.get('quantitativePrecipitation', {}).get('value', 0)
            
            if chance_of_rain >= 50 or rainfall_amount >= 0.10:
                return True, period['name'], chance_of_rain, rainfall_amount
    return False, None, 0, 0
  
def send_alert(to_phone_number, message_body):
    # Twilio credentials
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    twilio_phone_number = 'your_twilio_phone_number'
    
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=to_phone_number
    )
    
    print(f"Message sent: {message.sid}")

def run_daily_check(zip_code, phone_number):
    forecast_data = get_weather_forecast(zip_code)
    
    if forecast_data:
        condition_met, period_name, chance_of_rain, rainfall_amount = check_rain_conditions(forecast_data)
        
        if condition_met:
            message = f"Reminder: {period_name} has a {chance_of_rain}% chance of rain with {rainfall_amount} inches of expected rainfall."
            send_alert(phone_number, message)
        else:
            print("No rain conditions met for today.")
    else:
        print("Unable to fetch forecast data.")

# Schedule the task to run every day at a specific time (e.g., 7 AM)
schedule.every().day.at("07:00").do(run_daily_check, zip_code='90210', phone_number='+1234567890')

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute if the task is due

{
    "zip_code": "90210",
    "phone_number": "+1234567890"
}
