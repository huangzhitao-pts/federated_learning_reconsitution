import sys, os

sys.path.append("/home/huangzhitao/project/federated_learning_reconsitution/tensorflow_federated")

from datetime import datetime
from rq.decorators import job

from arch.storage.redis import RedisConnect
from arch.storage.mysql.session import Session
from arch.job.job_state import JobState
from arch.storage.mysql.model.register_table import Job

from arch.algorithm.sample_align import SampleAlign

from config import DeployMentConfig

redis = RedisConnect(
    host=DeployMentConfig.REDIS_HOST,
    port=DeployMentConfig.REDIS_PORT)

db = Session(DeployMentConfig.SQLALCHEMY_DATABASE_URI)


@job(DeployMentConfig.RQ_QUEUE, connection=redis, timeout=DeployMentConfig.RQ_TIMEOUT)
def align(job_id):
    print("align start !!!")
    print(job_id)
    SampleAlign(job_id).run()
    print("align end !!!")

    update_data = {"state": JobState.FINISHED, "completion_timestamp": datetime.utcnow()}
    # update mysql state
    db.query(Job).filter_by(uid=job_id).update(update_data)
    db.commit()

    # update redis state
    update_data["completion_timestamp"] = update_data["completion_timestamp"].timestamp()
    redis.hmset(job_id, update_data)

    return job_id


# if __name__ == '__main__':
#     import zlib
#
#     print(zlib.decompress(redis.redis.hget("rq:job:b8b57a8c-c8ca-48db-b6ac-4e561b2bb1c3", "exc_info")))
