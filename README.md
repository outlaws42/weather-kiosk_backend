# weather-kiosk

I previously wrote the weather kiosk using a raspberry pi with a display to display weather information.
This has a bit of a different purpose. This will take information from a weather API (Currently OWM) and gleen what information I want.
It will then present this information through a Flask API for the local network to consume. 
For me the main display is going to be simalur display  with a 5" or 6" screen that will set a desk. 
This time I am thinking this display will be a retired phone mounted in a frame running a flutter frontend.

Seperating the frontend from the backend allows for any frontend that can read the created API and display it differently depending on the device it is runnning on.

Right now I am really working on this and it is changing all the time. Currently it just runs a flask development server for coding. It is really not ready for being used for production but if you want to use the code and or expand on it go for it.

## Prerequisites

requires: python 3.3, Open Weather Map api key, mongoDB database

## config.py
You will need to create a dir in weatherkiosk called instance and your config.py.  So it will be like this weatherkiosk/instance/.config.py 
You can get a api key from https://openweathermap.org/ 

```python

OWM_API_KEY = 'your_OWM_api_key'

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
**run.py** serves up the flask API for your front end. The best way is to make these a system service that starts at boot time. besides these 2 you will need a system service for the mongoDB database. Ubuntu Linux this is `sudo systemctl enable mongod.service` to enable the installed
mongoDB database to start at boot time.   
```bash
get_weather.py
run.py

```

## Example API Calls

### /current
```json
[
    {
        "_id": {
            "$oid": "5fe1d0e7130d9ade63c80713"
        },
        "current_feels_like": 27,
        "current_humidity": "79%",
        "current_icon": 803,
        "current_status": "Clouds",
        "current_temp": 37,
        "current_wind_dir": "WNW",
        "current_wind_speed": 11,
        "updated": {
            "$date": 1608634599015
        }
    }
]
```

### /forecast

```json
[
    {
        "_id": {
            "$oid": "5fddccf961cbccf18afd4b08"
        },
        "date": {
            "$date": 1608640035018
        },
        "day0_dow": "Tue",
        "day0_icon": 803,
        "day0_pop": "48%",
        "day0_temp": "40\u00b0/34\u00b0",
        "day1_dow": "Wed",
        "day1_icon": 501,
        "day1_pop": "100%",
        "day1_temp": "49\u00b0/34\u00b0",
        "day2_dow": "Thu",
        "day2_icon": 601,
        "day2_pop": "100%",
        "day2_temp": "35\u00b0/16\u00b0",
        "replace": 1
    }
]
```
### /HighLow/day or /HighLow/year
Current is past day and past year for these to work you have have this data in 
database or it will return no data.

```json
[
    {
        "_id": {
            "$oid": "5fe17885130d9ade63c806fa"
        },
        "date": {
            "$date": 1608508800000
        },
        "high": 43,
        "icon": 804,
        "low": 32
    }
]
```

## Author

Troy Franks

## License

GPL
 
