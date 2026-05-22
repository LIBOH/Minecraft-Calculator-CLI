import os
import copy
from typing import Dict, Any, List, Optional
from datetime import datetime
from minecraft_calculator.core.event_system import (
    EventBus,
    EventType,
    Event,
    get_event_bus,
)
from minecraft_calculator.core.config_manager import ConfigManager, get_config_manager
from minecraft_calculator.utils.json_loader import JsonLoader


class JsonManager:
    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self._config_manager = config_manager or get_config_manager()
        self._event_bus = event_bus or get_event_bus()
        self._pending_changes: List[Dict[str, Any]] = []
        self._in_transaction: bool = False
        self._transaction_snapshot: Optional[Dict[str, Any]] = None
        self._subscribe_events()

    def _subscribe_events(self):
        self._event_bus.subscribe(
            EventType.INVENTORY_CHANGED, self._on_inventory_changed
        )
        self._event_bus.subscribe(EventType.RECIPE_ADDED, self._on_recipe_added)
        self._event_bus.subscribe(EventType.RECIPE_UPDATED, self._on_recipe_updated)
        self._event_bus.subscribe(EventType.RECIPE_REMOVED, self._on_recipe_removed)

    def _on_inventory_changed(self, event: Event):
        if self._in_transaction:
            self._pending_changes.append({"type": "inventory", "data": event.data})
        else:
            self._save_inventory(event.data.get("inventory", {}))

    def _on_recipe_added(self, event: Event):
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_add", "data": event.data})
        else:
            self._save_recipe(
                event.data.get("recipe", {}), event.data.get("mod_id", "vanilla")
            )

    def _on_recipe_updated(self, event: Event):
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_update", "data": event.data})
        else:
            self._save_recipe(
                event.data.get("recipe", {}), event.data.get("mod_id", "vanilla")
            )

    def _on_recipe_removed(self, event: Event):
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_remove", "data": event.data})
        else:
            self._remove_recipe(
                event.data.get("item_id", ""), event.data.get("mod_id", "vanilla")
            )

    def begin_transaction(self):
        self._in_transaction = True
        self._pending_changes = []
        self._transaction_snapshot = self._create_snapshot()

    def commit_transaction(self):
        try:
            for change in self._pending_changes:
                self._apply_change(change)
            self._pending_changes = []
            self._in_transaction = False
            self._transaction_snapshot = None
            self._event_bus.publish_simple(EventType.TRANSACTION_COMMIT, {}, self)
        except Exception as e:
            self.rollback_transaction()
            raise e

    def rollback_transaction(self):
        if self._transaction_snapshot:
            self._restore_snapshot(self._transaction_snapshot)
        self._pending_changes = []
        self._in_transaction = False
        self._transaction_snapshot = None
        self._event_bus.publish_simple(EventType.TRANSACTION_ROLLBACK, {}, self)

    def _create_snapshot(self) -> Dict[str, Any]:
        return {"inventory": self.load_inventory(), "recipes": self.load_all_recipes()}

    def _restore_snapshot(self, snapshot: Dict[str, Any]):
        if "inventory" in snapshot:
            self._save_inventory(snapshot["inventory"])
        if "recipes" in snapshot:
            self._save_all_recipes(snapshot["recipes"])

    def _apply_change(self, change: Dict[str, Any]):
        change_type = change.get("type")
        data = change.get("data", {})
        if change_type == "inventory":
            self._save_inventory(data.get("inventory", {}))
        elif change_type == "recipe_add" or change_type == "recipe_update":
            self._save_recipe(data.get("recipe", {}), data.get("mod_id", "vanilla"))
        elif change_type == "recipe_remove":
            self._remove_recipe(data.get("item_id", ""), data.get("mod_id", "vanilla"))

    def load_inventory(self) -> Dict[str, int]:
        return self._load_inventory()

    def load_all_recipes(self) -> Dict[str, Dict[str, Any]]:
        return self._load_all_recipes()

    def _load_inventory(self) -> Dict[str, int]:
        file_path = self._config_manager.get_inventory_path()
        try:
            data = JsonLoader.load(
                file_path,
                max_file_size=self._config_manager.config.io.max_file_size,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            )
            return data.get("items", {})
        except FileNotFoundError:
            return {}

    def _load_all_recipes(self) -> Dict[str, Dict[str, Any]]:
        recipes = {}
        vanilla_path = self._config_manager.get_vanilla_recipes_path()
        try:
            data = JsonLoader.load(
                vanilla_path,
                max_file_size=self._config_manager.config.io.max_file_size,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            )
            if "items" in data:
                for item_id, item_data in data["items"].items():
                    item_data_copy = copy.deepcopy(item_data)
                    item_data_copy["_source_mod"] = "vanilla"
                    recipes[item_id] = item_data_copy
        except FileNotFoundError:
            pass

        enabled_mods = self._config_manager.get_enabled_mods()
        mods_dir = self._config_manager.get_mod_recipes_dir()
        if os.path.exists(mods_dir):
            for filename in os.listdir(mods_dir):
                if filename.endswith(".json"):
                    mod_id = filename[:-5]
                    if mod_id not in enabled_mods:
                        continue
                    mod_path = os.path.join(mods_dir, filename)
                    try:
                        data = JsonLoader.load(
                            mod_path,
                            max_file_size=self._config_manager.config.io.max_file_size,
                            prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                            fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                            fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
                        )
                        if "items" in data:
                            for item_id, item_data in data["items"].items():
                                item_data_copy = copy.deepcopy(item_data)
                                item_data_copy["_source_mod"] = mod_id
                                recipes[item_id] = item_data_copy
                    except FileNotFoundError:
                        pass
        return recipes

    def _save_inventory(self, inventory: Dict[str, int]):
        file_path = self._config_manager.get_inventory_path()
        data = {"items": inventory, "last_updated": datetime.now().isoformat()}
        JsonLoader.save(
            file_path,
            data,
            compact=self._config_manager.config.io.compact_json,
            prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
            fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
            fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            backup_enabled=self._config_manager.config.backup.enabled,
            max_backups=self._config_manager.config.backup.max_backups,
        )

    def _save_recipe(self, recipe: Dict[str, Any], mod_id: str):
        recipe_copy = copy.deepcopy(recipe)
        item_id = recipe_copy.get("item_id")
        if not item_id:
            return
        recipe_copy.pop("_source_mod", None)

        if mod_id == "vanilla":
            file_path = self._config_manager.get_vanilla_recipes_path()
        else:
            file_path = self._config_manager.get_mod_recipes_path(mod_id)

        try:
            data = JsonLoader.load(
                file_path,
                max_file_size=self._config_manager.config.io.max_file_size,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            )
        except FileNotFoundError:
            data = {}

        if "items" not in data:
            data["items"] = {}
        data["items"][item_id] = recipe_copy

        JsonLoader.save(
            file_path,
            data,
            compact=self._config_manager.config.io.compact_json,
            prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
            fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
            fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            backup_enabled=self._config_manager.config.backup.enabled,
            max_backups=self._config_manager.config.backup.max_backups,
        )

    def _remove_recipe(self, item_id: str, mod_id: str):
        if not item_id:
            return

        if mod_id == "vanilla":
            file_path = self._config_manager.get_vanilla_recipes_path()
        else:
            file_path = self._config_manager.get_mod_recipes_path(mod_id)

        try:
            data = JsonLoader.load(
                file_path,
                max_file_size=self._config_manager.config.io.max_file_size,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
            )
        except FileNotFoundError:
            return

        if "items" in data and item_id in data["items"]:
            del data["items"][item_id]
            JsonLoader.save(
                file_path,
                data,
                compact=self._config_manager.config.io.compact_json,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
                backup_enabled=self._config_manager.config.backup.enabled,
                max_backups=self._config_manager.config.backup.max_backups,
            )

    def _save_all_recipes(self, recipes: Dict[str, Dict[str, Any]]):
        vanilla_recipes = {}
        mod_recipes: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for item_id, item_data in recipes.items():
            item_data_copy = copy.deepcopy(item_data)
            mod_id = item_data_copy.pop("_source_mod", "vanilla")
            if mod_id == "vanilla":
                vanilla_recipes[item_id] = item_data_copy
            else:
                if mod_id not in mod_recipes:
                    mod_recipes[mod_id] = {}
                mod_recipes[mod_id][item_id] = item_data_copy

        if vanilla_recipes:
            vanilla_path = self._config_manager.get_vanilla_recipes_path()
            data = {"items": vanilla_recipes}
            JsonLoader.save(
                vanilla_path,
                data,
                compact=self._config_manager.config.io.compact_json,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
                backup_enabled=self._config_manager.config.backup.enabled,
                max_backups=self._config_manager.config.backup.max_backups,
            )

        for mod_id, mod_data in mod_recipes.items():
            mod_path = self._config_manager.get_mod_recipes_path(mod_id)
            data = {"items": mod_data}
            JsonLoader.save(
                mod_path,
                data,
                compact=self._config_manager.config.io.compact_json,
                prefer_orjson=self._config_manager.config.json_loader.prefer_orjson,
                fallback_to_ujson=self._config_manager.config.json_loader.fallback_to_ujson,
                fallback_to_stdjson=self._config_manager.config.json_loader.fallback_to_stdjson,
                backup_enabled=self._config_manager.config.backup.enabled,
                max_backups=self._config_manager.config.backup.max_backups,
            )
