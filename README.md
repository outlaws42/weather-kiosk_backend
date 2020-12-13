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

### config.py
You will need to create a dir in weatherkiosk called instance and your config.py.  So it will be like this weatherkiosk/instance/.config.py 
You can get a api key from https://openweathermap.org/ 

```python

OWM_API_KEY = 'your_OWM_api_key'

```

### Installing 

Installing python 3, pip on the raspberry pi or any debian based linux computer
```
sudo apt-get install python3 python3-pip 

```
Run this from a terminal in the dir you want. to clone the repo to your local computer

```
git clone https://github.com/outlaws42/weather-kiosk_backend.git


```
Then run this command to install the modules needed

```
pip3 install -r requirements.txt

```

You will have to make the python files executedable.

```
chmod u+x *.py

```

To run

```
get_weather.py
run.py

```


## Author

Troy Franks

## License

GPL
 
