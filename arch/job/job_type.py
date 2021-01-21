from arch.job import align


class JobType(object):
    ALIGN = 0
    FEATURE_ENGINEERING = 1
    HORIZONTAL = 2
    VERTICAL = 3

    def get(self, item):
        item = item.upper()
        if hasattr(self, item):
            return getattr(self, item)

    def align_job(self, *args, **kwargs):
        align.delay(*args, **kwargs)