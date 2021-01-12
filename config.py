# -*- coding: utf-8 -*-


class DeployMentConfig(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:111@192.168.89.155:3310/federated_learning?charset=utf8"


config = {
    "deployment": DeployMentConfig
}
