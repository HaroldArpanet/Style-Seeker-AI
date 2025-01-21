from prefect import task
import json

class JsonReader:
    def __init__(self, file_path: str):
        """
        Initialize the JsonReader.
        """
        self.file_path = file_path

    @task
    def read_json_file(self):
        """
        Read and load JSON data from a file.

        :param file_path: Path to the JSON file.
        :return: Loaded JSON data.
        """
        with open(self.file_path, 'r') as file:
            return json.load(file)