from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import app_configs

# SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)
app.config.from_object(app_configs['development'])
app.url_map.strict_slashes = False
db = SQLAlchemy(app)

from app import views, models # package from which  we import the views
from app.views import mod
from app.auth import auth_blueprint
from app import views

app.register_blueprint(views.mod, url_prefix='/api/v1/')
app.register_blueprint(auth_blueprint)
