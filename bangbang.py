from flask import *

import datetime
import random
import re
import string

debug = False
app = Flask(__name__)


# ----------- Web --------------

@app.route('/', methods=['GET'])
def greet():
	thisTime = datetime.datetime.now()
	return render_template("index.html", time = thisTime)

#----------Jinja filter-------------------------------------------
@app.template_filter('printtime')
def timeToString(timestamp):
    return str(timestamp)


#-----------Run it!----------------------------------------------

if __name__ == "__main__":
	app.run(debug=debug)
