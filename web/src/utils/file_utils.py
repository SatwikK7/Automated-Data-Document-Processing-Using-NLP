import os
from typing import List, Dict, Union

class FileUtils:
    @staticmethod
    def read_file(filepath: str) -> Dict[str, Union[bytes, str]]:
        """Read file and return content with type"""
        with open(filepath, "rb") as f:
            content = f.read()
            file_type = filepath.split(".")[-1]
            return {
                "content": content,
                "type": f"application/{file_type}"
            }