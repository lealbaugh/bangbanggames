from flask import *
from flask.ext.socketio import SocketIO, emit

import datetime
import random
import re
import string

debug = False
app = Flask(__name__)

socketio = SocketIO(app)


# ----------- Web --------------
@app.route('/', methods=['GET'])
def greet():
	thisTime = datetime.datetime.now()
	return render_template("index.html", time = thisTime)

@socketio.on('message')
def send_message(message):
	emit("message",str(datetime.datetime.now()))


#----------Jinja filter-------------------------------------------
@app.template_filter('printtime')
def timeToString(timestamp):
    return str(timestamp)


#-----------Run it!----------------------------------------------

if __name__ == "__main__":
	socketio.run(app)
