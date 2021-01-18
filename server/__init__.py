# -*- coding: utf-8 -*-
from flask import Flask

from config import config
from arch.storage.mysql.session import Session
from arch.storage.redis.connect import RedisConnect


def create_app(config_name):
    app = Flask(__name__)

    from .register import register
    from .jobs import jobs

    app.register_blueprint(register)
    app.register_blueprint(jobs)

    app.config.from_object(config[config_name])

    setattr(app, "db", Session(app.config["SQLALCHEMY_DATABASE_URI"]))
    setattr(app, "redis", RedisConnect(
        app.config["REDIS_HOST"],
        app.config["REDIS_PORT"]
    ))

    return app
