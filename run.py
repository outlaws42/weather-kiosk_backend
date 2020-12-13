#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, Response

from datetime import datetime, timedelta, date, time
from flask_restful import Api, Resource, abort, fields, marshal_with 
from flask_pymongo import MongoClient
from bson.codec_options import CodecOptions
from weatherkiosk.settings import DB_URI, DATABASE
import pytz

# Init app
app = Flask(__name__)
api = Api(app)

# Database
mongo = MongoClient(DB_URI)
db = mongo[DATABASE]


# Forecast Class
class Forecast(Resource):
  def get(self):
    collection = db['forecast']
    last = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in last]
    print(result)
    return jsonify({'forecast' : f"{result}"})
api.add_resource(Forecast, "/forecast")

# Current Class
class Current(Resource):
  def get(self):
    collection = db['current']
    response = collection.find().sort("_id", -1).limit(1)
    result = [doc for doc in response]
    print(result)
    return jsonify({'current' : f"{result}"})
api.add_resource(Current, "/current")

# History Class
class History(Resource):
  def get(self):
    today = datetime.combine(date.today(), time())
    tomorrow = today + timedelta(1)
    collection = db['HighLow']
    response = collection.find({'date' :{'$lt' : tomorrow, '$gte' : today}})
    results = [doc for doc in response]
    return jsonify({'History' : f"{results}"})

api.add_resource(History, "/history")

# History Year ago Class
class HistoryYear(Resource):
  def get(self):
    year_ago = datetime.combine(date.today(), time()) - timedelta(366)
    year_ago_plus =  year_ago + timedelta(1)
    collection = db['HighLow']
    response = collection.find({
        'date' :{'$lt' : year_ago_plus, 
        '$gte' : year_ago}}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    return jsonify({'HistoryYear' : f"{year_ago_plus}"})

api.add_resource(HistoryYear, "/history/year")

# History Day ago Class
class HistoryDay(Resource):
  def get(self):
    day_ago = datetime.combine(date.today(), time()) - timedelta(1)
    day_ago_plus =  day_ago + timedelta(1)
    collection = db['HighLow']
    response = collection.find({
        'date' :{'$lt' : day_ago_plus, 
        '$gte' : day_ago}}).sort('_id', -1).limit(1)
    result = [doc for doc in response]
    return jsonify({'Historyday' : f"{result}"})

api.add_resource(HistoryDay, "/history/day")


# Run Server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
