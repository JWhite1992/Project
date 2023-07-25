from flask import Flask

app = Flask(__name__)
app.secret_key = 'its about time'

from flask_app.controllers import controllers_users
from flask_app.controllers import controllers_tables
from flask_app.controllers import controllers_messages
from flask_app.models import model_message
from flask_app.models import model_user
from flask_app.models import model_seatingtable
