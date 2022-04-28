from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
import datetime

'''
This scriipt follows the models model used in flask/django development. This script holds
all of the DB items that will be initialized and used throughout the project. 

All classes correspond to their table in the DB. 
'''

db = SQLAlchemy()

class Home(db.Model):
    __tablename__ = 'home'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Home: {self.name}"

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    home_id = db.Column(db.Integer(), db.ForeignKey('home.id'))

    def __init__(self, name, home_id = None):
        self.name = name
        self.home_id = home_id

class Sensor(db.Model):
    __tablename__ = 'sensors'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    value = db.Column(db.Float())
    home_id = db.Column(db.Integer(), db.ForeignKey('home.id'))

    def __init__(self, name, value = 0, home_id = None):
        self.name = name
        self.value = value
        self.home_id = home_id
    
    def __repr__(self):
        return f"<Sensor: {self.name} Value: {self.value}>"

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    status = db.Column(db.Boolean())
    home_id = db.Column(db.Integer(), db.ForeignKey('home.id'))
    room_id = db.Column(db.Integer(), db.ForeignKey('rooms.id'))
    x_pos = db.Column(db.Integer())
    y_pos = db.Column(db.Integer())
    type = db.Column(db.String())

    def __init__(self, name, type, status = False, home_id = None, room_id = None, x_pos = 0, y_pos = 0):
        self.name = name
        self.status = status
        self.home_id = home_id
        self.room_id = room_id
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.type = type

    def __repr__(self):
        return f"<Item: {self.name} Status: {self.status}>"

class Weather(db.Model):
    __tablename__ = 'weather'
    
    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.String())
    data = db.Column(JSONB())
    
    def __init__(self, datetime, data):
        self.datetime = datetime
        self.data = data

class Usage(db.Model):
    __tablename__ = 'usage'

    id = db.Column(db.Integer(), primary_key=True)
    start_time = db.Column(db.String())
    usage = db.Column(db.Integer())
    item_id = db.Column(db.Integer())

    def __init__(self, start_time, item_id, usage = 0):
        self.start_time = start_time
        self.usage = usage
        self.item_id = item_id

    def __repr__(self):
        return f"<Start Time: {self.start_time} Usage(sec): {self.usage} Item ID: {self.item_id}>"

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String())
    date = db.Column(db.String())
    powervalues = db.Column(JSONB())
    watervalues = db.Column(JSONB())
    costvalues = db.Column(JSONB())

    def __init__(self, type, date, powervalues, watervalues, costvalues):
        self.type = type
        self.date = date
        self.powervalues = powervalues
        self.watervalues = watervalues
        self.costvalues = costvalues

    #return history object as tuple of (powerValues, waterValues, costValues)
    def graphValues(self):
        pow = list(self.powervalues[1:-1].split(', '))
        pow = [float(i) for i in pow]
        wat = list(self.watervalues[1:-1].split(', '))
        wat = [float(i) for i in wat]
        cos = list(self.costvalues[1:-1].split(', '))
        cos = [float(i) for i in cos]
        return pow, wat, cos

    def __repr__(self):
        return f"<Month: {self.month} Power Values: {self.powerValues} Water Values: {self.waterValues} Cost Values: {self.costValues}>"

class HVAC (db.Model):
    __tablename__ = 'hvac'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    setpoint = db.Column(db.Integer())
    mode = db.Column(db.String())
    home_id = db.Column(db.Integer(), db.ForeignKey('home.id'))

    openDoor = 0
    openWindow = 0

    def __init__(self, name, home_id, setpoint = 60, mode = "off"):
        self.name = name
        self.setpoint = setpoint
        self.mode = mode
        self.home_id = home_id

        self.openDoor = 0
        self.openWindow = 0