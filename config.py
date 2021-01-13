# -*- coding: utf-8 -*-
import os


class DeployMentConfig(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:111@192.168.89.155:3310/federated_learning?charset=utf8"

    BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


config = {
    "deployment": DeployMentConfig
}
