#! /usr/bin/env python3

# -*- coding: utf-8 -*-
import datetime
import pytz
import geopy.geocoders
from geopy.geocoders import Nominatim
import logging
import requests
import weatherkiosk.tmod as tmod
from collections import ChainMap
from weatherkiosk.instance.config import OWM_API_KEY as key
from weatherkiosk.settings import USE_API, ZIP_CODE, UNITS
logging.basicConfig(
    filename='wu.log', 
    level=logging.INFO, 
    format='%(asctime)s %(message)s', 
    datefmt='%m/%d/%Y %I:%M:%S %p')


class Weather():
    degree_sign = '\N{DEGREE SIGN}'

    def __init__(self):
        pass

    def get_forecast(self):
        forecast_l = []
        tmod.add_to_list(self.forecast_days(),forecast_l)
        tmod.add_to_list(self.forecast_temp(),forecast_l)
        tmod.add_to_list(self.forecast_precip_day(),forecast_l)
        tmod.add_to_list(self.forecast_code(),forecast_l)
        tmod.add_to_list(self.forecast_datetime(),forecast_l)
        return forecast_l
    
    # def combine_dict(self, dict_list):
    #     """
    #     Takes a list of dictionarys and combines into one dictionary
    #     requires from collections import ChainMap and python 3.3 or later
    #     """
    #     current = dict(ChainMap(*dict_list))
    #     return current

    def geolocation(self, address):
        try:
            geolocator = Nominatim(user_agent = "weather kiosk")
            location = geolocator.geocode(address)
            addressout = location.address
            addresslist = addressout.split(',')
            if len(address) <= 5:
                city = addresslist[0]
            else:
                city = addresslist[2]
            return location.latitude, location.longitude, city
        except Exception as e:
            print("This is the location from Error {} ".format(e))
            return 41.232921, -85.649106, "columbia city"

    def get_weather_info(self):
        location = self.geolocation(ZIP_CODE)
        lat, long, self.city = location
        # print(f" This is the location {location}")
        try:
            if USE_API == True:
                c = requests.get(f'https://api.openweathermap.org/data/2.5/weather?zip=46725,us&units={UNITS}&appid={key}')
                f = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&units={UNITS}&exclude=current,alert,minutely,hourly&appid={key}')
                weather = c.json()
                forecast = f.json()
                tmod.save_json('weather.json', weather, 'relative')
                tmod.save_json('forecast.json', forecast, 'relative')
                self.weather = tmod.open_json('weather.json','relative')
                self.forecast_in = tmod.open_json('forecast.json','relative')
            else:
                self.weather = tmod.open_json('weather.json', 'relative')
                self.forecast_in = tmod.open_json('forecast.json','relative')
        except Exception as e:
           self.weather = tmod.open_json('weather.json', 'relative')
           logging.info('Collect weather error:  ' + str(e))
           pass
        
    def gleen_info(self):
        # weather service
        # left weather info
        # brief description of the weather
        status = {'current_status': self.weather['weather'][0]['main']}
        refresh = {'updated' : datetime.datetime.utcnow()}

        # outside temp .
        outdoor_temp = {'current_temp': round(self.weather['main']['temp'])}
        
        # wind
        import_wind_dir = self.weather['wind']['deg']
        wind_dir = {'current_wind_dir' : self.degtocompass(import_wind_dir)}
        wind_speed = {'current_wind_speed': round(self.weather['wind']['speed'])}

        # Humidity
        humidity = {'current_humidity' : f"{round(self.weather['main']['humidity'])}%"}
        
        # Feels Like
        feels_like = {'current_feels_like': round(float(self.weather['main']['feels_like']))}

        # Current Icon 
        current_icon =  {'current_icon' : self.weather['weather'][0]['icon']}    
        return [status, outdoor_temp, refresh, wind_dir, wind_speed, humidity, feels_like, current_icon]

    def degtocompass(self, degrees):
        direction = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
                     "N"]
        val = int((degrees / 22.5) + .5)
        return direction[(val % 16)]

    def forecast_days(self, days =3):
        # forecast day for 3 days
        forecast_day = []
        for i in range(days):
            tstamp = self.forecast_in['daily'][i]['dt']
            day = {f'day{i}_dow' : datetime.datetime.fromtimestamp(tstamp).strftime('%a')}
            forecast_day.append(day)
        return forecast_day
        
    def forecast_temp(self, days = 3):
        # forecast high / low temp for 3 days    
        forecast = []
        for i in range(days):
            temp = {f'day{i}_temp' : f"{round(self.forecast_in['daily'][i]['temp']['max'])}{self.degree_sign}/{round(self.forecast_in['daily'][i]['temp']['min'])}{self.degree_sign}"}
            forecast.append(temp)
        return forecast
    
    def forecast_code(self, days = 3):
        # forecast code is day / night key word starting at index 0 for 3 days
        forecast_day_code = []
        for i in range(days):
            temp = {f'day{i}_icon' : self.forecast_in['daily'][i]['weather'][0]['icon']}
            forecast_day_code.append(temp)
        return forecast_day_code
        
    def forecast_precip_day(self, days=3):
        # pop is day night chance of precip starting at index 0 for 3 days
        forecast_pr = []
        for i in range(days):
            temp = self.forecast_in['daily'][i]['pop']
            temp_calc = (float(temp)*100)
            forecast_pr.append({f'day{i}_pop' : f'{int(temp_calc)}%'})
        return forecast_pr
        
    def forecast_datetime(self):
        # pop is day night chance of precip starting at index 0 for 3 days
        forecast_dt = [{"date" : datetime.datetime.utcnow()}]
        return forecast_dt

if __name__ == "__main__":
    app = Weather()