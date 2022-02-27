from tarfile import RECORDSIZE
from threading import Lock
from flask import Flask, jsonify, redirect, render_template, session
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
import requests

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
# app.config['MONGODB_SETTINGS'] = {
#     'db': 'IOTdb',
#     'host': 'localhost',
#     'port' : 8091
# }
# database = PyMongo(app)
# db = database.db
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()



lst = []
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode, lst=lst)

@app.route('/timestamp/')
def timestamp():
    return {'Hello': 'WOrld'}

def saveData():
    #  save only data 
    pass


# Receive the test request from client and send back a test response
@socketio.on('record')
def handle_message(data):
    #  Parse and save
    # Check for alerts
    # print(data)
    # saveData(data)
    lst.append(data)
    print(lst)
    emit('alerts', {'data': 'Test response sent'})
    return render_template('index.html')



# Add alert to handle message through redis
@socketio.event
def connect():
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task()
    print('Hello')
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=False, use_reloader = True)