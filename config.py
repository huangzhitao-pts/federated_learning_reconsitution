# -*- coding: utf-8 -*-
import os


class DeployMentConfig(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:111@192.168.89.155:3310/federated_learning?charset=utf8"

    REDIS_HOST = "192.168.89.155"
    REDIS_PORT = "6380"
    REDIS_CONNECT_DB = "0"
    RQ_TIMEOUT = "6h"
    RQ_QUEUE = "high"

    BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


config = {
    "deployment": DeployMentConfig
}
