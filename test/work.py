# import time
# from task import add
#
# job = add.delay(3, 4)
# time.sleep(2)
# print(job.result)
#
# from rq import Queue
# from redis import Redis
# redis_conn = Redis(host='192.168.89.155', port=6380)
#
# q = Queue(connection=redis_conn)
# print(len(q.failed_job_registry))


class A:
    a = 1


a = A()
a.b = 2
# print(getattr(A, "a"))
print(A.__dict__)
print(vars(A))
print(a.__dict__)
print(vars(a))
