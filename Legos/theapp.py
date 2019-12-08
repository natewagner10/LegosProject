import psycopg2
from flask import Flask, render_template
import os


app = Flask(__name__)

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

from views import *

if __name__ == '__main__':
    #app.debug = True
    app.run()
