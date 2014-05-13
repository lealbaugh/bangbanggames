

import datetime
import random
import re
import string
import os

from flask import *
from flask.ext.socketio import SocketIO, emit
app = Flask(__name__)
app.debug = False
socketio = SocketIO(app)

from pymongo import *

# MongoHQ account info, temporarily from envvariables.py
# import envvariables
# mongoclientURL = envvariables.MONGOHQ_URL
mongoclientURL = os.environ['MONGOHQ_URL']
databasename = mongoclientURL.split("/")[-1] #gets the last bit of the URL, which is the database name
mongoclient = MongoClient(mongoclientURL)
database = mongoclient[databasename]	#loads the assigned database
geocodes = database["geocodes"]	#loads or makes the collection, whichever should happen

import urllib2
import json

def formatAddressForGeocoding(rawaddress):
	return "+".join(rawaddress.strip().split())

def requestGeocode(rawaddress):
	address = formatAddressForGeocoding(rawaddress)
	url="http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % address
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geocode = json.loads(jsongeocode)

	if geocode["status"] == "OK":
		location = geocode["results"][0]["geometry"]["location"]
		latitude = location["lat"]
		longitude = location["lng"]
		data = {"placename":rawaddress, "status":"OK", "latitude":latitude, "longitude":longitude}
		socketio.emit("geocode", data)
		geocodes.insert(data)

	else:
		status = geocode["status"]
		data = {"placename":rawaddress, "error":status}
		geocodes.insert(data)


# ----------Logic---------------
def gameLogic(content):
	requestGeocode(content)
	pass
	# socketio.emit('location', content)


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
			if geocode["status"]=="OK":
				placename = geocode["placename"]
				latitude = geocode["latitude"]
				longitude = geocode["longitude"]
				socketio.emit("geocode", {"placename":placename, "latitude":latitude, "longitude": longitude})
	return

# put received placename/location in DB
@socketio.on('test')
def testingSocket(data):
	print "HELLO"
	

#----------Jinja filter-------------------------------------------
@app.template_filter('printtime')
def timeToString(timestamp):
    return str(timestamp)


#-----------Run it!----------------------------------------------

if __name__ == "__main__":
	socketio.run(app)


# curl --post "From=adfsd&Body=Pittsburgh" http://localhost:5000/twilio
