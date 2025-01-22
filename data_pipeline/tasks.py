from prefect import task, flow
import json
from decouple import config
from minio import Minio
from meilisearch import Client
from data_pipeline.services.prefect_tasks.json_reader import JsonReader
from data_pipeline.services.prefect_tasks.index_data import MeilisearchIndexer
from data_pipeline.services.prefect_tasks.img_internaler import ImgInternaller

@flow
def img_internaller_flow(image_urls: list, minio_client: Minio, minio_bucket: str):
    """
    Prefect flow to orchestrate the download and upload of images.

    :param image_urls: A list of image URLs to process.
    :param minio_client: A Minio client object.
    :param minio_bucket: The name of the MinIO bucket.
    """
    img_internaller = ImgInternaller(minio_client, minio_bucket)

    downloaded_images = img_internaller.downloader(image_urls)

    success, uploaded_images = img_internaller.uploader(downloaded_images)

    if success:
        print("All images uploaded successfully!")
        return uploaded_images
    else:
        print("Failed to upload some images.")

@flow
def index_data_flow(json_file_path: str, index_name: str):
    """
    Prefect flow to index data from a JSON file into Meilisearch after processing images.

    :param json_file_path: Path to the JSON file.
    :param minio_client: Minio client object.
    :param minio_bucket: Name of the MinIO bucket.
    :param meilisearch_client: Meilisearch client object.
    :param index_name: Name of the Meilisearch index.
    """
    json_reader = JsonReader(json_file_path)
    data = json_reader.read_json_file()

    minio_client = Minio(
        config('MINIO_HOST'),
        access_key=config('MINIO_ACCESS_KEY'),
        secret_key=config('MINIO_SECRET_KEY'),
        secure=False
    )
    meilisearch_client = Client(config('MEILISEARCH_HOST'), config('MEILISEARCH_API_KEY'))
    minio_bucket = config('MINIO_BUCKET')

    # for item in data:
    #     image_urls = item.get('images', [])
    #     if image_urls:
    #         local_paths = list(img_internaller_flow(image_urls, minio_client, minio_bucket).values())
    #         item['images'] = local_paths

    meilisearch_indexer = MeilisearchIndexer(meilisearch_client, index_name)
    task_uid = meilisearch_indexer.index_data(data)

    task_status =meilisearch_indexer.check_task_status(task_uid)

    if task_status:
        print("Data indexed successfully!")
        return True
    else:
        raise Exception("Failed to index data into Meilisearch.")
