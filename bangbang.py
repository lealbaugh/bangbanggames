

import datetime
import random
import re
import string

from flask import *
from flask.ext.socketio import SocketIO, emit
app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)

from pymongo import *
import envvariables
# MongoHQ account info, temporarily from envvariables.py
mongoclientURL = envvariables.MONGOHQ_URL
databasename = mongoclientURL.split("/")[-1] #gets the last bit of the URL, which is the database name
mongoclient = MongoClient(mongoclientURL)
database = mongoclient[databasename]	#loads the assigned database
geocodes = database["geocodes"]	#loads or makes the collection, whichever should happen


# ----------Logic---------------
def gameLogic(content):
	socketio.emit('location', content)


# ----------- Web --------------
@app.route('/', methods=['GET'])
def greet():
	thisTime = datetime.datetime.now()
	return render_template("index.html", time = thisTime)

@app.route('/twilio', methods=['POST'])
def incomingSMS():
	phoneNumber = request.form.get('From', None)
	content = request.form.get('Body', None)
	if content:
		gameLogic(content)
		return "Success!"
	else: 
		return "Eh?"

@app.route('/map', methods=['GET'])
def mapview():
	return render_template("map.html")

@socketio.on('message')
def send_message(message):
	if message == "hello":
		for geocode in geocodes.find():
			placename = geocode["placename"]
			longitude = geocode["location"]["A"]
			latitude = geocode["location"]["k"]
			socketio.emit("cachedgeocode", {"placename":placename, "latitude":latitude, "longitude": longitude})
	return

# put received placename/location in DB
@socketio.on('newgeocode')
def cacheGeocode(data):
	print data
	geocodes.insert(data)
	return True
	

#----------Jinja filter-------------------------------------------
@app.template_filter('printtime')
def timeToString(timestamp):
    return str(timestamp)


#-----------Run it!----------------------------------------------

if __name__ == "__main__":
	socketio.run(app)


# curl --post "From=adfsd&Body=Pittsburgh" http://localhost:5000/twilio
