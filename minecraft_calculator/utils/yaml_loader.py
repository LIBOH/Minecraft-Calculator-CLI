import os
import yaml
from typing import Dict, Any
from minecraft_calculator.exceptions import YamlParseError, YamlSaveError

class YamlLoader:
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @staticmethod
    def _validate_path(file_path: str) -> str:
        abs_path = os.path.abspath(os.path.normpath(file_path))
        if ".." in abs_path.split(os.sep):
            raise YamlParseError(file_path, "路径不安全")
        return abs_path

    @staticmethod
    def load(file_path: str) -> Dict[str, Any]:
        file_path = YamlLoader._validate_path(file_path)
        
        if not os.path.exists(file_path):
            return {}
        
        if os.path.getsize(file_path) > YamlLoader.MAX_FILE_SIZE:
            raise YamlParseError(file_path, "文件过大")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise YamlParseError(file_path, str(e))
        except Exception as e:
            raise YamlParseError(file_path, str(e))

    @staticmethod
    def save(file_path: str, data: Dict[str, Any]):
        file_path = YamlLoader._validate_path(file_path)
        
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except PermissionError:
            raise YamlSaveError(file_path, "权限不足")
        except Exception as e:
            raise YamlSaveError(file_path, str(e))
