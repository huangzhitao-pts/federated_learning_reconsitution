# -*- coding: utf-8 -*-

from flask import Blueprint


register = Blueprint('register', __name__)


from . import workspace
from . import dataset
from . import auth
