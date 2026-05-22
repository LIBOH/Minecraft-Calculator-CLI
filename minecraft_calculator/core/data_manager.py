import copy
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from minecraft_calculator.core.event_system import EventBus, EventType, get_event_bus
from minecraft_calculator.core.config_manager import ConfigManager, get_config_manager
from minecraft_calculator.core.json_manager import JsonManager
from minecraft_calculator.core.search_index import SearchIndex, SearchResult
from minecraft_calculator.exceptions import InvalidInputError


@dataclass
class DataManagerTransaction:
    data_manager: "DataManager"

    def __enter__(self):
        self.data_manager._json_manager.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.data_manager._json_manager.rollback_transaction()
            return False
        else:
            self.data_manager._json_manager.commit_transaction()
            return True


class DataManager:
    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        json_manager: Optional[JsonManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self._config_manager = config_manager or get_config_manager()
        self._event_bus = event_bus or get_event_bus()

        if json_manager is None:
            self._json_manager = JsonManager(self._config_manager, self._event_bus)
        else:
            self._json_manager = json_manager

        self._recipes: Dict[str, Dict[str, Any]] = {}
        self._inventory: Dict[str, int] = {}
        self._enabled_mods: List[str] = []
        self._search_index = SearchIndex()

        self._load_all()

    def _load_all(self):
        self._inventory = self._json_manager.load_inventory()
        self._recipes = self._json_manager.load_all_recipes()
        self._search_index.build(self._recipes)
        self._event_bus.publish_simple(
            EventType.RECIPES_LOADED, {"count": len(self._recipes)}, self
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "recipes": copy.deepcopy(self._recipes),
            "inventory": copy.deepcopy(self._inventory),
        }

    def restore(self, snapshot: Dict[str, Any]):
        self._recipes = snapshot.get("recipes", {})
        self._inventory = snapshot.get("inventory", {})
        self._search_index.build(self._recipes)

    def transaction(self) -> DataManagerTransaction:
        return DataManagerTransaction(self)

    def search(self, query: str) -> List[SearchResult]:
        return self._search_index.search(query)

    def get_recipe(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self._recipes.get(item_id)

    def get_all_recipes(self) -> List[str]:
        return list(self._recipes.keys())

    def add_recipe(
        self,
        item_id: str,
        name: str,
        ingredients: Dict[str, int],
        result: int = 1,
        stack_size: int = 64,
        mod_id: str = "vanilla",
    ) -> bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if not name:
            raise InvalidInputError("物品名称不能为空")

        item_data = {
            "item_id": item_id,
            "name": name,
            "stack": stack_size,
            "recipes": [{"ingredients": ingredients, "result": result}],
            "_source_mod": mod_id,
        }

        self._recipes[item_id] = item_data
        self._search_index.build(self._recipes)

        self._event_bus.publish_simple(
            EventType.RECIPE_ADDED, {"recipe": item_data, "mod_id": mod_id}, self
        )
        return True

    def update_recipe(
        self,
        item_id: str,
        name: Optional[str] = None,
        ingredients: Optional[Dict[str, int]] = None,
        result: Optional[int] = None,
        stack_size: Optional[int] = None,
    ) -> bool:
        if item_id not in self._recipes:
            return False

        if name is not None:
            self._recipes[item_id]["name"] = name
        if ingredients is not None:
            if self._recipes[item_id]["recipes"]:
                self._recipes[item_id]["recipes"][0]["ingredients"] = ingredients
        if result is not None:
            if self._recipes[item_id]["recipes"]:
                self._recipes[item_id]["recipes"][0]["result"] = result
        if stack_size is not None:
            self._recipes[item_id]["stack"] = stack_size

        self._search_index.build(self._recipes)

        mod_id = self._recipes[item_id].get("_source_mod", "vanilla")
        self._event_bus.publish_simple(
            EventType.RECIPE_UPDATED,
            {"recipe": self._recipes[item_id], "mod_id": mod_id},
            self,
        )
        return True

    def remove_recipe(self, item_id: str) -> bool:
        if item_id in self._recipes:
            mod_id = self._recipes[item_id].get("_source_mod", "vanilla")
            del self._recipes[item_id]
            self._search_index.build(self._recipes)

            self._event_bus.publish_simple(
                EventType.RECIPE_REMOVED, {"item_id": item_id, "mod_id": mod_id}, self
            )
            return True
        return False

    def get_inventory_item(self, item_id: str) -> int:
        return self._inventory.get(item_id, 0)

    def list_inventory(self) -> Dict[str, int]:
        return dict(self._inventory)

    def add_item(self, item_id: str, count: int) -> bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        if item_id in self._inventory:
            self._inventory[item_id] += count
        else:
            self._inventory[item_id] = count

        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {
                "inventory": self._inventory,
                "action": "add",
                "item_id": item_id,
                "count": count,
            },
            self,
        )
        return True

    def remove_item(self, item_id: str, count: int) -> bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        if item_id not in self._inventory:
            return False

        if self._inventory[item_id] >= count:
            self._inventory[item_id] -= count
            if self._inventory[item_id] == 0:
                del self._inventory[item_id]
            removed = True
        else:
            # 如果数量不够，不要删除，返回False
            removed = False

        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {
                "inventory": self._inventory,
                "action": "remove",
                "item_id": item_id,
                "count": count,
            },
            self,
        )
        return removed

    def set_item(self, item_id: str, count: int) -> bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count < 0:
            raise InvalidInputError("数量不能为负数")

        if count == 0:
            if item_id in self._inventory:
                del self._inventory[item_id]
        else:
            self._inventory[item_id] = count

        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {
                "inventory": self._inventory,
                "action": "set",
                "item_id": item_id,
                "count": count,
            },
            self,
        )
        return True

    def clear_inventory(self) -> None:
        self._inventory.clear()

        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {"inventory": self._inventory, "action": "clear"},
            self,
        )

    def get_enabled_mods(self) -> List[str]:
        return self._config_manager.get_enabled_mods()

    def enable_mod(self, mod_id: str) -> None:
        if mod_id not in self._config_manager.get_enabled_mods():
            self._config_manager.enable_mod(mod_id)
            self._load_all()
            self._event_bus.publish_simple(
                EventType.MOD_ENABLED, {"mod_id": mod_id}, self
            )

    def disable_mod(self, mod_id: str) -> None:
        if mod_id in self._config_manager.get_enabled_mods():
            self._config_manager.disable_mod(mod_id)
            self._load_all()
            self._event_bus.publish_simple(
                EventType.MOD_DISABLED, {"mod_id": mod_id}, self
            )

    def get_item_count(self) -> int:
        return len(self._inventory)

    def get_recipe_count(self) -> int:
        return len(self._recipes)
