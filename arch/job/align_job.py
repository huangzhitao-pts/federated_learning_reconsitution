from arch.storage.redis import RedisConnect
from rq.decorators import job

from config import DeployMentConfig


redis = RedisConnect(
    host=DeployMentConfig.REDIS_HOST,
    port=DeployMentConfig.REDIS_PORT)


@job(DeployMentConfig.RQ_QUEUE, connection=redis, timeout=DeployMentConfig.RQ_TIMEOUT)
def align(x, y):
    print("align start !!!")
    print(x + y)
    print("align end !!!")
    return x + y


