import os
import requests
import tempfile
from minio import Minio
from minio.error import S3Error
from prefect import task

class ImgInternaller:
    def __init__(self, minio_client: Minio, minio_bucket: str):
        """
        Initialize the ImgInternaller service.

        :param minio_client: A Minio client object to interact with MinIO.
        :param minio_bucket: The name of the MinIO bucket where images will be uploaded.
        """
        self.minio_client = minio_client
        self.minio_bucket = minio_bucket

    @task
    def downloader(self, image_urls: list) -> dict[str, str]:
        """
        Download images from a list of URLs and save them temporarily.

        :param image_urls: A list of image URLs to download.
        :return: A dictionary with image URLs as keys and temporary file paths as values.
        """
        downloaded_images = {}
        for url in image_urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    downloaded_images[url] = tmp_file.name

            except requests.exceptions.RequestException as e:
                print(f"Failed to download image from {url}: {e}")
                continue

        return downloaded_images

    @task
    def uploader(self, downloaded_images: dict[str, str]) -> tuple[bool, dict[str, str]]:
        """
        Upload images to MinIO.

        :param downloaded_images: A dictionary with image URLs as keys and temporary file paths as values.
        :return: A tuple containing a boolean (True if all uploads succeeded, False otherwise)
                 and a dictionary with MinIO paths for the uploaded images.
        """
        uploaded_images = {}
        success = True

        for url, tmp_file_path in downloaded_images.items():
            try:
                object_name = os.path.basename(url)

                self.minio_client.fput_object(
                    bucket_name=self.minio_bucket,
                    object_name=object_name,
                    file_path=tmp_file_path,
                )

                uploaded_images[url] = f"{self.minio_bucket}/{object_name}"

                os.remove(tmp_file_path)

            except S3Error as e:
                print(f"Failed to upload image {url} to MinIO: {e}")
                success = False
                uploaded_images = {}
                break

        return success, uploaded_images
