from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from config import config
from .api.v1.auth import auth_api
from .api.v1.admin import admin_api
from .api.v1.teacher import teacher_api
from .api.v1.student import student_api

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    app.register_blueprint(auth_api, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_api, url_prefix='/api/v1/admin')
    app.register_blueprint(teacher_api, url_prefix='/api/v1/teacher')
    app.register_blueprint(student_api, url_prefix='/api/v1/student')

    return app