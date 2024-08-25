import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # db配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'resource.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    return app