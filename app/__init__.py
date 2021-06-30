import os

from flask import Flask
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

from .config import env_config

db = SQLAlchemy()
migrate = Migrate()
mysql = MySQL()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(env_config[config_name])
    mysql.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    from . import view
    app.register_blueprint(view.bp)
    return app



