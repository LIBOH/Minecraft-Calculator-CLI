import os
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
from minecraft_calculator.exceptions import JsonParseError, JsonSaveError

try:
    import orjson

    _HAS_ORJSON = True
except ImportError:
    _HAS_ORJSON = False

try:
    import ujson

    _HAS_UJSON = True
except ImportError:
    _HAS_UJSON = False

import json as _std_json


class BackupManager:
    @staticmethod
    def backup(
        file_path: str,
        max_backups: int = 3,
        enabled: bool = True,
        backup_dir: Optional[str] = None,
    ) -> None:
        if not enabled or not os.path.exists(file_path):
            return

        if backup_dir:
            if not os.path.isabs(backup_dir):
                file_dir = os.path.dirname(file_path)
                backup_dir = os.path.join(file_dir, backup_dir)
        else:
            backup_dir = f"{file_path}.backups"

        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"{timestamp}.json")

        shutil.copy2(file_path, backup_file)

        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".json")],
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
        )

        while len(backups) > max_backups:
            oldest = backups.pop(0)
            os.remove(os.path.join(backup_dir, oldest))


class JsonLoader:
    @staticmethod
    def _validate_path(file_path: str) -> str:
        abs_path = os.path.abspath(os.path.normpath(file_path))
        if ".." in abs_path.split(os.sep):
            raise JsonParseError(file_path, "路径不安全")
        return abs_path

    @staticmethod
    def load(
        file_path: str,
        max_file_size: int = 10 * 1024 * 1024,
        prefer_orjson: bool = True,
        fallback_to_ujson: bool = True,
        fallback_to_stdjson: bool = True,
    ) -> Dict[str, Any]:
        file_path = JsonLoader._validate_path(file_path)

        if not os.path.exists(file_path):
            return {}

        if os.path.getsize(file_path) > max_file_size:
            raise JsonParseError(file_path, "文件过大")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if prefer_orjson and _HAS_ORJSON:
                return orjson.loads(content)
            elif fallback_to_ujson and _HAS_UJSON:
                return ujson.loads(content)
            elif fallback_to_stdjson:
                return _std_json.loads(content)
            else:
                raise JsonParseError(file_path, "没有可用的JSON解析库")
        except (ValueError, TypeError) as e:
            raise JsonParseError(file_path, str(e))
        except Exception as e:
            raise JsonParseError(file_path, str(e))

    @staticmethod
    def save(
        file_path: str,
        data: Dict[str, Any],
        compact: bool = False,
        prefer_orjson: bool = True,
        fallback_to_ujson: bool = True,
        fallback_to_stdjson: bool = True,
        backup_enabled: bool = True,
        max_backups: int = 3,
        backup_dir: Optional[str] = None,
    ):
        file_path = JsonLoader._validate_path(file_path)

        BackupManager.backup(file_path, max_backups, backup_enabled, backup_dir)

        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            if prefer_orjson and _HAS_ORJSON:
                if compact:
                    content = orjson.dumps(
                        data, option=orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS
                    )
                else:
                    content = orjson.dumps(
                        data,
                        option=orjson.OPT_INDENT_2
                        | orjson.OPT_SORT_KEYS
                        | orjson.OPT_NON_STR_KEYS,
                    )
                with open(file_path, "wb") as f:
                    f.write(content)
            elif fallback_to_ujson and _HAS_UJSON:
                indent_ujson: int = 0 if compact else 2
                content = ujson.dumps(data, indent=indent_ujson)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            elif fallback_to_stdjson:
                indent_stdjson: int | None = None if compact else 2
                with open(file_path, "w", encoding="utf-8") as f:
                    _std_json.dump(
                        data,
                        f,
                        indent=indent_stdjson,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
            else:
                raise JsonSaveError(file_path, "没有可用的JSON序列化库")
        except (ValueError, TypeError) as e:
            raise JsonSaveError(file_path, str(e))
        except PermissionError:
            raise JsonSaveError(file_path, "权限不足")
        except Exception as e:
            raise JsonSaveError(file_path, str(e))
