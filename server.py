from crypt import methods
from threading import local
from flask import Flask, jsonify, redirect, render_template, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import requests

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iotdevices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

'''Model For Iot Device data'''
class Device(db.Model):
    vid = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    avgVolt = db.Column(db.Float)
    packVolt = db.Column(db.Float)
    current = db.Column(db.Float)
    battery = db.Column(db.Integer)
    created = db.Column(db.DateTime, primary_key=True)

db.create_all()
# Device.query.delete()

socketio = SocketIO(app, async_mode=async_mode)


alertsList = []
voltageAlerts = []
currentAlerts = []
batteryAlerts = []

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/timestamp/')
def timestamp():
    Tquery = Device.query.all()
    # print("Empty query",Tquery)
    if Tquery:
        return {'timestamp': Tquery[-1].created}       
    return {'timestamp': False}

@socketio.on('records')
def saveData(data):
    #  save only data
    # # Commit changes in the session

    for item in data:
        lst = item['tdata'].split(',')
        timestamp = datetime.strptime(item['created'], '%Y-%m-%d %H:%M:%S')
        created = timestamp.astimezone(pytz.UTC)
        record = Device(vid = lst[0],latitude = lst[1],longitude = lst[2],avgVolt = lst[17],packVolt = lst[18],current = lst[19],battery = lst[20],created = created)
        db.session.add(record)
        try:
            db.session.commit() 
        except Exception as e:
            print(e)
            print("error")
            db.session.rollback()
        finally:
            db.session.close()
        if float(lst[18]) >= 100:
            print('Package voltage breach..')
            voltageAlerts.append(item)
            emit('alerts',{'data': str(item), 'type': 'Voltage Breach'},broadcast=True)
            print('')
            
        elif float(lst[19]) < 0:
            print('Current  breach..')
            currentAlerts.append(item)
            emit('alerts',{'data': str(item), 'type': 'Current Breach'},broadcast=True)
            print('')
            
        elif int(lst[20]) <= 20:
            print('Battery  breach..')
            batteryAlerts.append(item)
            emit('alerts',{'data': str(item), 'type': 'Battery Breach'},broadcast=True)
            print('')
            
        else:
            pass


if __name__ == '__main__':
    socketio.run(app, port=5000, debug=False, use_reloader = True)