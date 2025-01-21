from prefect import task, flow
from minio import Minio
from meilisearch import Client
from data_pipeline.services.prefect_tasks.img_internaler import ImgInternaller
import time

class MeilisearchIndexer:
    def __init__(self, meilisearch_client: Client, index_name: str):
        """
        Initialize the MeilisearchIndexer service.

        :param meilisearch_client: A Meilisearch client object.
        :param index_name: The name of the Meilisearch index.
        """
        self.meilisearch_client = meilisearch_client
        self.index_name = index_name

    @task
    def index_data(self, data: list) -> str:
        """
        Index data into Meilisearch.

        :param data: Data to index.
        :return: Task ID from Meilisearch.
        """
        index = self.meilisearch_client.index(self.index_name)
        task = index.add_documents(documents=data, primary_key='id')
        return task.task_uid

    @task
    def check_task_status(self, task_uid: str) -> bool:
        """
        Check the status of a Meilisearch task.

        :param task_uid: Task ID to check.
        :return: True if the task is successful, False otherwise.
        """
        while True:
            task = self.meilisearch_client.get_task(task_uid)
            if task.status == 'succeeded':
                return True
            elif task.status == 'enqueued' or task.status == 'processing':
                time.sleep(2)
            else:
                return False
