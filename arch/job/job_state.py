from arch.storage.redis import RedisConnect
from config import DeployMentConfig


class JobState(object):
    UNKNOWN = 0
    DISABLED = 1
    STARTED = 2
    FINISHED = 3
    FAILED = 4
    PAUSED = 5
    PENDING = 6

    def __init__(self, job_id):
        self.job_id = job_id
        self.redis = RedisConnect(
            host=DeployMentConfig.REDIS_HOST,
            port=DeployMentConfig.REDIS_PORT)

    def sample_align(self):
        pass

    def feature_engineering(self):
        pass