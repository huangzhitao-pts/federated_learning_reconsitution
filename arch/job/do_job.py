from arch.storage.redis import RedisConnect
from arch.job.job_state import JobState

from rq.decorators import job

from config import DeployMentConfig

redis = RedisConnect(
    host=DeployMentConfig.REDIS_HOST,
    port=DeployMentConfig.REDIS_PORT)


@job(DeployMentConfig.RQ_QUEUE, connection=redis, timeout=DeployMentConfig.RQ_TIMEOUT)
def align(job_id):
    print("align start !!!")
    print(job_id)
    print("align end !!!")

    # update redis state
    redis.hset(job_id, "status", JobState.FINISHED)
    return job_id


# if __name__ == '__main__':
#     import zlib
#
#     print(zlib.decompress(redis.redis.hget("rq:job:b8b57a8c-c8ca-48db-b6ac-4e561b2bb1c3", "exc_info")))