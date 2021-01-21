
from tensorflow_federated.simulation.vertical_sample_align import FederatedLearningJob
from arch.job.job_state import JobState


class SampleAlign(FederatedLearningJob):
    def __init__(self, align_job_id, dataset_ids, dataset_from_another_org, org_id, **kwargs):
        self._dataset_ids = dataset_ids
        super().__init__(align_job_id, {}, dataset_ids, 1, **kwargs)
        self._dataset_from_another_org = dataset_from_another_org
        self._org_id = org_id
        self._controller = AlignJobInfoController.restore(align_job_id)
        self._ALIGNED_ID_TEMPLATE = '/aligned_data/{}/'.format(align_job_id) + 'aligned_id_{}.txt'
        self._ALIGNED_DATASET_TEMPLATE = '/aligned_data/{}/'.format(align_job_id) + 'aligned_data_{}.csv'

    def _get_uid_list(self):
        session = sessionmaker(bind=_SQLALCHEMY_ENGINE)()
        try:
            uid_row = session.query(SchemaOrganization.uid).join(Dataset, SchemaOrganization.schema_id == Dataset.schema_id).filter(Dataset.dataset_id.in_(self._dataset_ids)).all()
            uids = [uid[0] for uid in uid_row]
        except Exception:
            raise
        finally:
            session.close()
        return uids

    def _get_client_id_url_tuples(self):
        session = sessionmaker(bind=_SQLALCHEMY_ENGINE)()
        try:
            clients_row = session.query(Client).join(Dataset, Client.client_id == Dataset.client_id).filter(Dataset.dataset_id.in_(self._dataset_ids)).all()
            clients_tuple = [(client.client_id, client.client_address) for client in clients_row]
        except Exception:
            raise
        finally:
            session.close()
        return clients_tuple

    def _get_dataset_url_list(self):
        session = sessionmaker(bind=_SQLALCHEMY_ENGINE)()
        try:
            datasets_row = session.query(Dataset).filter(Dataset.dataset_id.in_(self._dataset_ids)).all()
            datasets_url_list = [dataset.dataset_url for dataset in datasets_row]
        except Exception:
            raise
        finally:
            session.close()
        print(datasets_url_list)
        return datasets_url_list

