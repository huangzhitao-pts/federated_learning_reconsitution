# -*- coding: utf-8 -*-

from flask import Blueprint


jobs = Blueprint('jobs', __name__)


# from . import align
# from . import feature_engineering
# from . import horizontal
# from . import vertical
from . import job

