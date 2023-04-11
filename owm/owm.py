"""
This is where we retrieve weather forecast from OpenWeatherMap. Before doing so, make sure you have both the
signed up for an OWM account and also obtained a valid API key that is specified in the config.json file.
"""

import logging
import requests
import json
import string
import datetime


class OWMModule:
    def __init__(self):
        self.logger = logging.getLogger('maginkdash')

    def get_owm_weather(self, lat, lon, api_key):
        url = "https://api.openweathermap.org/data/3.0/onecall?lat=%s&lon=%s&appid=%s&exclude=minutely,alerts&units=metric" % (
        lat, lon, api_key)
        response = requests.get(url)
        data = json.loads(response.text)
        curr_weather = data["current"]
        hourly_forecast = data["hourly"]
        # print(json.dumps(curr_weather, indent=2))
        daily_forecast = data["daily"]
        # print(json.dumps(forecast, indent=2))
        results = {"current_weather": curr_weather, "hourly_forecast": hourly_forecast, "daily_forecast": daily_forecast}
        return results

    def get_weather(self, lat, lon, owm_api_key):
        current_weather, daily_forecast = {}, {}

        weather_results = self.get_owm_weather(lat, lon, owm_api_key)
        current_weather = weather_results["current_weather"]
        hourly_forecast = weather_results["hourly_forecast"]
        daily_forecast = weather_results["daily_forecast"]

        """        
        print("Current weather is %s, and the temperature is %s." % (
            string.capwords(current_weather["weather"][0]["description"]), current_weather["temp"]))

        print("")
        dt = datetime.datetime.fromtimestamp(hourly_forecast[1]["dt"])
        print("Next Hour: " + dt.strftime("%m/%d/%Y, %H:%M:%S"))
        print("Type: " + string.capwords(hourly_forecast[1]["weather"][0]["description"]))
        print("Temp: " + str(round(hourly_forecast[1]["temp"])))
        print("Chance of Rain: " + str(hourly_forecast[1]["pop"] * 100) + "%")
        
        for i in range(3):
            print("")
            dt = datetime.datetime.fromtimestamp(daily_forecast[i]["dt"])
            print("Date: " + dt.strftime("%m/%d/%Y, %H:%M:%S"))
            print("Type: " + string.capwords(daily_forecast[i]["weather"][0]["description"]))
            print("Min: " + str(round(daily_forecast[i]["temp"]["min"])))
            print("Max: " + str(round(daily_forecast[i]["temp"]["max"])))
            print("Chance of Rain: " + str(daily_forecast[i]["pop"] * 100) + "%")
        """

        return current_weather, hourly_forecast, daily_forecast
