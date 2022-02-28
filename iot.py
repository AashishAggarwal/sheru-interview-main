from crypt import methods
import os
from flask import Flask, render_template, session
import pytz
import socketio
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func

# App reference
app = Flask(__name__)
sio = socketio.Client()

# Method execution before API request
# Function call in console only

def getData():
    # Grab url data whole
    """Example of how to send server generated events to clients."""
    url = 'http://3.109.76.78:2222/xenergyData.json'
    records = ((requests.get(url)).json())['records']
    return records
    


def filterData(data):
    # adding a small comment
    # filter data only after last known timestamp
    # get last query from db and then filter data from getdata
    url = 'http://127.0.0.1:5000/timestamp/'
    lastTime = ((requests.get(url)).json())['timestamp']
    # print(lastTime)

    if lastTime:
        utcTimezone = pytz.UTC
        lastTime = datetime.strptime(lastTime, '%a, %d %b %Y %H:%M:%S GMT')
        lastTime = utcTimezone.localize(lastTime)
        # print("last time:", lastTime)
        lst = []
        for item in data:
            timezone = pytz.timezone('Asia/Kolkata')
            newTime = datetime.strptime(item['created'], '%Y-%m-%d %H:%M:%S')
            newTime = newTime.astimezone(timezone)

            if newTime > lastTime:
                # print('new time:', newTime)
                lst.append(item)
        return lst
    else:
        return data


def sendData(data):
    # send single json object for the last query after filter 
    print('Sending data via socket connection...')
    # print('before API request')
    sio.connect('http://127.0.0.1:5000')
    sio.emit('records', data)
    sio.disconnect()

def background():
    data = getData()
    records = filterData(data)
    if records:
        sendData(records)

scheduler = BackgroundScheduler()

@app.route('/')
def control():
    return render_template('control.html')


@app.route('/start/', methods=['POST', 'GET'])
def start():
    scheduler.add_job(func=background, trigger="interval", seconds=10)
    scheduler.start()
    return "Succesfully started"


@app.route('/stop/', methods=['POST', 'GET'])
def stop():
    scheduler.remove_job(func = background)
    # scheduler.shutdown()
    return "Succesfully stopped"


# Receive the test request from client and send back a test response
@sio.on('alerts')
def handle_message(data):
    print(data)
    # emit('test_response', {'data': 'Test response sent'})

# App run interface
app.debug = True
host = os.environ.get('IP', '127.0.0.1')
port = int(os.environ.get('PORT', 8091))
app.run(host=host, port=port, use_reloader = True)


