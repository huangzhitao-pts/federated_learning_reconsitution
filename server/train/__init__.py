# -*- coding: utf-8 -*-

from flask import Blueprint


train = Blueprint('train', __name__)


from . import align
