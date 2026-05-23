import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from minecraft_calculator.core.event_system import get_event_bus, EventType
from minecraft_calculator.utils.json_loader import JsonLoader

_config_manager_instance = None


@dataclass
class PathsConfig:
    data_dir: str
    inventory_file: str
    recipes_dir: str
    vanilla_recipes_file: str
    mods_recipes_dir: str
    app_config_file: str


@dataclass
class BackupConfig:
    max_backups: int
    enabled: bool
    recipes_backup_dir: Optional[str] = None
    inventory_backup_dir: Optional[str] = None


@dataclass
class IOConfig:
    max_file_size: int
    compact_json: bool


@dataclass
class JsonLoaderConfig:
    prefer_orjson: bool
    fallback_to_ujson: bool
    fallback_to_stdjson: bool


@dataclass
class AppConfig:
    paths: PathsConfig
    backup: BackupConfig
    io: IOConfig
    json_loader: JsonLoaderConfig


class ConfigManager:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._base_dir = base_dir
        self._config: AppConfig = self._create_default_config()
        self._enabled_mods: list[str] = []
        self._event_bus = get_event_bus()
        self._load_config()

    def _load_config(self):
        config_path = os.path.join(
            self._base_dir, "minecraft_calculator", "data", "app_config.json"
        )
        if not os.path.exists(config_path):
            self._config = self._create_default_config()
            self._save_config()
        else:
            try:
                data = JsonLoader.load(config_path)
                self._config = self._parse_config(data)
            except Exception:
                self._config = self._create_default_config()

    def _create_default_config(self) -> AppConfig:
        paths = PathsConfig(
            data_dir="data",
            inventory_file="inventory.json",
            recipes_dir="recipes",
            vanilla_recipes_file="vanilla.json",
            mods_recipes_dir="mods",
            app_config_file="app_config.json",
        )
        backup = BackupConfig(
            max_backups=3,
            enabled=True,
            recipes_backup_dir=None,
            inventory_backup_dir=None
        )
        io = IOConfig(max_file_size=10485760, compact_json=True)
        json_loader = JsonLoaderConfig(
            prefer_orjson=True, fallback_to_ujson=True, fallback_to_stdjson=True
        )
        return AppConfig(paths=paths, backup=backup, io=io, json_loader=json_loader)

    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        self._enabled_mods = data.get("enabled_mods", [])
        paths_data = data.get("paths", {})
        paths = PathsConfig(
            data_dir=paths_data.get("data_dir", "data"),
            inventory_file=paths_data.get("inventory_file", "inventory.json"),
            recipes_dir=paths_data.get("recipes_dir", "recipes"),
            vanilla_recipes_file=paths_data.get("vanilla_recipes_file", "vanilla.json"),
            mods_recipes_dir=paths_data.get("mods_recipes_dir", "mods"),
            app_config_file=paths_data.get("app_config_file", "app_config.json"),
        )
        backup_data = data.get("backup", {})
        backup = BackupConfig(
            max_backups=backup_data.get("max_backups", 3),
            enabled=backup_data.get("enabled", True),
            recipes_backup_dir=backup_data.get("recipes_backup_dir", None),
            inventory_backup_dir=backup_data.get("inventory_backup_dir", None),
        )
        io_data = data.get("io", {})
        io = IOConfig(
            max_file_size=io_data.get("max_file_size", 10485760),
            compact_json=io_data.get("compact_json", True),
        )
        json_loader_data = data.get("json_loader", {})
        json_loader = JsonLoaderConfig(
            prefer_orjson=json_loader_data.get("prefer_orjson", True),
            fallback_to_ujson=json_loader_data.get("fallback_to_ujson", True),
            fallback_to_stdjson=json_loader_data.get("fallback_to_stdjson", True),
        )
        return AppConfig(paths=paths, backup=backup, io=io, json_loader=json_loader)

    def _save_config(self):
        config_path = self.get_app_config_path()
        data = {
            "enabled_mods": self._enabled_mods,
            "paths": {
                "data_dir": self._config.paths.data_dir,
                "inventory_file": self._config.paths.inventory_file,
                "recipes_dir": self._config.paths.recipes_dir,
                "vanilla_recipes_file": self._config.paths.vanilla_recipes_file,
                "mods_recipes_dir": self._config.paths.mods_recipes_dir,
                "app_config_file": self._config.paths.app_config_file,
            },
            "backup": {
                "max_backups": self._config.backup.max_backups,
                "enabled": self._config.backup.enabled,
                "recipes_backup_dir": self._config.backup.recipes_backup_dir,
                "inventory_backup_dir": self._config.backup.inventory_backup_dir,
            },
            "io": {
                "max_file_size": self._config.io.max_file_size,
                "compact_json": self._config.io.compact_json,
            },
            "json_loader": {
                "prefer_orjson": self._config.json_loader.prefer_orjson,
                "fallback_to_ujson": self._config.json_loader.fallback_to_ujson,
                "fallback_to_stdjson": self._config.json_loader.fallback_to_stdjson,
            },
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        JsonLoader.save(config_path, data, compact=self._config.io.compact_json)

    @property
    def config(self) -> AppConfig:
        return self._config

    def update_config(self, updates: Dict[str, Any]):
        if "paths" in updates:
            paths_data = updates["paths"]
            for key, value in paths_data.items():
                if hasattr(self._config.paths, key):
                    setattr(self._config.paths, key, value)
        if "backup" in updates:
            backup_data = updates["backup"]
            for key, value in backup_data.items():
                if hasattr(self._config.backup, key):
                    setattr(self._config.backup, key, value)
        if "io" in updates:
            io_data = updates["io"]
            for key, value in io_data.items():
                if hasattr(self._config.io, key):
                    setattr(self._config.io, key, value)
        if "json_loader" in updates:
            json_loader_data = updates["json_loader"]
            for key, value in json_loader_data.items():
                if hasattr(self._config.json_loader, key):
                    setattr(self._config.json_loader, key, value)
        self._save_config()
        self._event_bus.publish_simple(
            EventType.CONFIG_CHANGED, {"config": self._config}, self
        )

    def get_data_path(self, relative_path: str = "") -> str:
        return os.path.join(
            self._base_dir,
            "minecraft_calculator",
            self._config.paths.data_dir,
            relative_path,
        )

    def get_inventory_path(self) -> str:
        return os.path.join(self.get_data_path(), self._config.paths.inventory_file)

    def get_vanilla_recipes_path(self) -> str:
        return os.path.join(
            self.get_data_path(),
            self._config.paths.recipes_dir,
            self._config.paths.vanilla_recipes_file,
        )

    def get_mod_recipes_dir(self) -> str:
        return os.path.join(
            self.get_data_path(),
            self._config.paths.recipes_dir,
            self._config.paths.mods_recipes_dir,
        )

    def get_mod_recipes_path(self, mod_id: str) -> str:
        return os.path.join(self.get_mod_recipes_dir(), f"{mod_id}.json")

    def get_app_config_path(self) -> str:
        return os.path.join(self.get_data_path(), self._config.paths.app_config_file)

    def get_enabled_mods(self) -> list[str]:
        return list(self._enabled_mods)

    def enable_mod(self, mod_id: str) -> None:
        if mod_id not in self._enabled_mods:
            self._enabled_mods.append(mod_id)
            self._save_config()

    def disable_mod(self, mod_id: str) -> None:
        if mod_id in self._enabled_mods:
            self._enabled_mods.remove(mod_id)
            self._save_config()


def get_config_manager() -> ConfigManager:
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance
