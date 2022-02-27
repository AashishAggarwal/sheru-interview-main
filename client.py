from codecs import backslashreplace_errors
import os
from threading import Lock
from flask import Flask, render_template, session
# from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
import socketio
import requests

# App reference
app = Flask(__name__)
sio = socketio.Client()

# Method execution before API request
# Function call in console only


def getData():
    # Grab url data whole
    """Example of how to send server generated events to clients."""
    count = 0

    url = 'http://3.109.76.78:2222/xenergyData.json'
    records = ((requests.get(url)).json())['records']
    
        # print(tdata)
        # print(created)
    


def filterData():
    # filter data only after last known timestamp
    # get last query from db and then filter data from getdata
    url = 'http://127.0.0.1:5000/timestamp/'
    records = ((requests.get(url)).json())['Hello']
    # for record in records:
    #     socketio.sleep(1)
    #     count += 1
    #     vid = record['vid']
    #     tdata = record['tdata']
    #     created = record['created']
    #     datavia = record['datavia']
    #     tdata = tdata.split(',')
    # pass
    print(records)

def sendData():
    # send single json object for the last query after filter 
    print('')
    print('before API request')
    sio.connect('http://127.0.0.1:5000')
    sio.emit('record', {
      "id": 'null',
      "vid": "XNG1037",
      "datavia": "GPRS",
      "tdata": "XNG1037,32.649029,89.980239,4.40,4.65,4.60,4.46,4.40,4.72,4.58,4.46,4.59,4.68,4.26,4.42,4.76,4.41,4.24,59.99,0.62,86,-1.0,0,A1,122723,4094,v2.1.4",
      "created": "2022-02-27 08:13:21"
    })
    # sio.disconnect()

def background():
    # data = getData()
    filterData()
    # if filterData():
    #     saveData(filterData)
    # sendData()


# background()

# Receive the test request from client and send back a test response
@sio.on('test_response')
def handle_message(data):
    print('received message: ' + str(data))
    # emit('test_response', {'data': 'Test response sent'})

background()
# def sendData():

app.debug = True
host = os.environ.get('IP', '127.0.0.1')
port = int(os.environ.get('PORT', 8091))
app.run(host=host, port=port, use_reloader = True)


