import requests
import datetime as dt
import json
import models
from dateutil.parser import parse

# call the meteostat API and get data. 
def getWeather(x = 30):
    
    url = "https://meteostat.p.rapidapi.com/stations/hourly"

    querystring = {"station":"72228","start":dt.date.today() - dt.timedelta(days=x),"end":dt.date.today(),"tz":"America/Chicago","model":"true","units":"imperial"}

    headers = {
        'x-rapidapi-host': "meteostat.p.rapidapi.com",
        'x-rapidapi-key': "e4a12345e7mshb7a976fe3ea03b6p1b9a1bjsnccde9d8ebafb"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    #write data to a local file to limit api calls. 
    with open('meteostat_API.json', 'w+') as data:
        json.dump(response.json(), data, indent=4)

# store the historical weather data in the DB. 
def storeWeather(app):

    with open ('meteostat_API.json') as data:
        weather_data = json.load(data)

    with app.app_context():
        weather_data = weather_data['data']
        for i in range(len(weather_data)):
            if (weather_data[i]['time'],) not in models.db.session.query(models.Weather.datetime).all():
                w_dt = weather_data[i]['time']
                w_data = weather_data[i]
                models.db.session.add(models.Weather(w_dt, w_data))
                models.db.session.commit()
            else:
                pass

# get the current conditions. This is used to pass information to the dashboard to display the current outdoor temp and humidity. could expand to add outdoor conditions/precip.
def getCurrentConditions():
    with open ('meteostat_API.json') as data:
        weather_data = json.load(data)
        meta = weather_data['meta'] 
        if parse(meta['generated']).strftime('%Y-%m-%d') != dt.date.today().strftime('%Y-%m-%d'):
            getWeather(1)
            data = weather_data['data']     
            hour = dt.datetime.today().strftime('%Y-%m-%d %H:00:00')
            for i in range(len(data)):
                if data[i]['time'] == hour:
                    return {'temp': data[i]['temp'], 'humidity': data[i]['rhum']}
                else:
                    pass
        else:
            data = weather_data['data']     
            hour = dt.datetime.today().strftime('%Y-%m-%d %H:00:00')
            for i in range(len(data)):
                if data[i]['time'] == hour:
                    return {'temp': data[i]['temp'], 'humidity': data[i]['rhum']}
                else:
                    pass