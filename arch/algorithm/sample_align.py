import json
from tensorflow_federated.simulation.vertical_sample_align import FederatedLearningJob
from arch.job.job_state import JobState

from arch.storage.mysql.session import Session
from arch.storage.mysql.model.register_table import Job, User, DataSet
from arch.job.job_type import JobType
from config import DeployMentConfig


class SampleAlign(FederatedLearningJob):
    def __init__(self, job_id, **kwargs):
        super().__init__(job_id, **kwargs)
        # self._controller = AlignJobInfoController.restore(align_job_id)
        self._ALIGNED_ID_TEMPLATE = '/aligned_data/{}/'.format(job_id) + 'aligned_id_{}.txt'
        self._ALIGNED_DATASET_TEMPLATE = '/aligned_data/{}/'.format(job_id) + 'aligned_data_{}.csv'
        self.session = Session(DeployMentConfig.SQLALCHEMY_DATABASE_URI)

    def _get_uid_list(self):
        job = self.session.query(Job).filter_by(
            uid=self._job_id,
            job_type=JobType.ALIGN
        ).first()
        with open(job.conf_path, "rb") as f:
            conf = json.load(f)
            return [i["field"] for i in conf["conf"]["dataSet"]]

    def _get_client_id_url_tuples(self):
        job = self.session.query(Job).filter_by(
            uid=self._job_id,
            job_type=JobType.ALIGN
        ).first()
        with open(job.conf_path, "rb") as f:
            conf = json.load(f)
            dataSet = conf["conf"]["dataSet"]
            patty_ip_address_list = list()
            for i in dataSet:
                party = self.session.query(User.id, User.ip_address).join(
                    DataSet, DataSet.user_uid == User.uid
                ).filter(DataSet.uid == i["uid"]).first()
                patty_ip_address_list.append(party)
        return patty_ip_address_list

    def _get_dataset_url_list(self):
        job = self.session.query(Job).filter_by(
            uid=self._job_id,
            job_type=JobType.ALIGN
        ).first()
        with open(job.conf_path, "rb") as f:
            conf = json.load(f)
            dataSet = conf["conf"]["dataSet"]
            file_path_list = list()
            for i in dataSet:
                file_path = self.session.query(DataSet).filter_by(
                    uid=i["uid"]
                ).first()
                file_path_list.append(file_path[0])
        return file_path_list

