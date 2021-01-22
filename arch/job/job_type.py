from arch.job import align


class JobType(object):
    ALIGN = 0
    FEATURE_ENGINEERING = 1
    HORIZONTAL = 2
    VERTICAL = 3

    @classmethod
    def get(cls, item):
        item = item.upper()
        if hasattr(cls, item):
            return getattr(cls, item)

    @staticmethod
    def align_job(job_id):
        align.delay(job_id)