# weather-kiosk

I previously wrote the weather kiosk using a raspberry pi with a display to display weather information.
This has a bit of a different purpose. This will take information from a weather API (Currently OWM) and gleen what information I want.
It will then present this information through a Flask API for the local network to consume. 
For me the main display is going to be simalur display  with a 5" or 6" screen that will set 
on a desk. 
This time I am thinking this display will be a retired phone mounted in a frame running a flutter frontend.

Seperating the frontend from the backend allows for any frontend that can read the created API and display it differently depending on the device it is runnning on.

Right now I am really working on this and it is changing all the time. Currently it just runs a flask development server for coding. It is really not ready for being used for production but if you want to use the code and or expand on it go for it.

## Prerequisites

requires: python 3.3, Open Weather Map api key, mongoDB database

## config.py
You will need to create a dir in weatherkiosk called instance and put in your config.py.  So it will be like this weatherkiosk/instance/config.py 
You can get a api key from https://openweathermap.org/  Alternativally you can use the weather bit API https://www.weatherbit.io/. To use weather bit you would need to change the `API` setting in the `settings.py` to 1 as well as get a weather bit API key and put it in the `config.py` file as follows. 

```python

OWM_API_KEY = 'your_OWM_api_key'
WEATHER_BIT_API_KEY = 'your_weatherbit_api_key'

```

## Installing 

Installing python 3, pip on the raspberry pi or any debian based linux computer
```bash
sudo apt-get install python3 python3-pip 

```
Run this from a terminal in the dir you want. to clone the repo to your local computer

```bash
git clone https://github.com/outlaws42/weather-kiosk_backend.git


```
Change into the project main dir

```bash
cd weatherkiosk

```

Then run this command to install the modules needed

```bash
pip3 install -r requirements.txt

```

You will have to make the python files executedable.

```bash
chmod u+x *.py

```

## To run
**get_weather.py** will check the weather API every 15 min. This is the main file that
collects the information for the weather kiosk API.

**indoor.py** Will check the indoor weather sensor every 30 seconds. I seperated this off
so it could be updated more often then getting the weather info.

**run.py** serves up the flask API for your front end. 

The best way to run these is to make these a system service that starts at boot time. 

Besides these 3 you will need a system service for the mongoDB database. In Linux that uses systemd this is `sudo systemctl enable mongod.service` to enable the installed
mongoDB database to start at boot time.  To install MongoDB server community Edition on Ubuntu you can follow these instructions. [Install MongoDB in Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)   

```bash
./get_weather.py
./indoor.py
./run.py

```

**Note:** You should be able to run this code on Windows and MacOS as well as long as you have the 
prerequesites installed. Runing the python files and starting everything at boot time will be different for those platforms but it should be possible.

## Example API Calls

### /current
```json
{
  "current": {
    "current_sunset": 1612220301,
    "current_sunrise": 1612183956,
    "current_icon": 804,
    "current_feels_like": 20,
    "current_humidity": "88%",
    "current_wind_speed": 1,
    "current_wind_dir": "N",
    "updated": 1612171610,
    "current_temp": 25,
    "current_status": "Clouds"
  }
}

```

### /forecast

```json
{
    "forecast": {
        "date": 1609411531,
        "replace": 1,
        "day2_icon": 500,
        "day1_icon": 502,
        "day0_icon": 803,
        "day2_pop": "100%",
        "day1_pop": "100%",
        "day0_pop": "0%",
        "day2_temp": "34\u00b0/30\u00b0",
        "day1_temp": "35\u00b0/27\u00b0",
        "day0_temp": "32\u00b0/25\u00b0",
        "day2_dow": "Sat",
        "day1_dow": "Fri",
        "day0_dow": "Thu"
    }
}

```
### /past/day or /past/year
Current is past day and past year for these to work you have have this data in 
database or it will return no data.

```json
{
    "forecast_day": {
        "icon": 500,
        "high": 42,
        "low": 27,
        "date": 1609304400
    }
}

// forecast year
{
    "forecast_year": {
        "icon": 804,
        "high": 31,
        "low": 25,
        "date": 1577768400
    }
}


```

## Author

Troy Franks

## License

GPL
 
