import json
import os
from typing import Any, Dict


class FileManager:
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {file_path}: {e}")

    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any]):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
