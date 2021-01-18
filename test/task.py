import time
from redis import Redis
from rq.decorators import job

from flask import current_app as app


@job('high', connection=app.redis, timeout=5)
def add(x, y):
    print("--------------")
    return x + y


