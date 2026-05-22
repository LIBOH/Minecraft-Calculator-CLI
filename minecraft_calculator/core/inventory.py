from typing import Dict, Optional
from minecraft_calculator.core.data_manager import DataManager
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.exceptions import InvalidInputError, ItemNotFoundError


class Inventory:
    def __init__(
        self,
        file_path: Optional[str] = None,
        data_manager: Optional[DataManager] = None,
    ):
        if data_manager is None:
            self._data_manager = DataManager()
        else:
            self._data_manager = data_manager
        self._recipe_manager: Optional[RecipeManager] = None

    def set_recipe_manager(self, recipe_manager: RecipeManager) -> None:
        self._recipe_manager = recipe_manager

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def _resolve_item_id(self, name_or_id: str) -> str:
        if self._recipe_manager is None:
            return name_or_id
        try:
            return self._recipe_manager.get_item_id(name_or_id)
        except ItemNotFoundError:
            return name_or_id

    def _resolve_item_name(self, name_or_id: str) -> str:
        if self._recipe_manager is None:
            return name_or_id
        try:
            item_id = self._recipe_manager.get_item_id(name_or_id)
            return self._recipe_manager.get_item_name(item_id)
        except ItemNotFoundError:
            return name_or_id

    def add_item(self, name_or_id: str, count: int) -> None:
        if not name_or_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        item_id = self._resolve_item_id(name_or_id)
        self._data_manager.add_item(item_id, count)

    def remove_item(self, name_or_id: str, count: int) -> bool:
        if not name_or_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        item_id = self._resolve_item_id(name_or_id)
        return self._data_manager.remove_item(item_id, count)

    def get_count(self, name_or_id: str) -> int:
        item_id = self._resolve_item_id(name_or_id)
        return self._data_manager.get_inventory_item(item_id)

    def get_count_by_id(self, item_id: str) -> int:
        count = self._data_manager.get_inventory_item(item_id)
        if count > 0:
            return count

        if self._recipe_manager is not None:
            try:
                item_name = self._recipe_manager.get_item_name(item_id)
                name_count = self._data_manager.get_inventory_item(item_name)
                if name_count > 0:
                    return name_count
            except Exception:
                pass

        return 0

    def clear(self) -> None:
        self._data_manager.clear_inventory()

    def list_items(self) -> Dict[str, int]:
        if self._recipe_manager is None:
            return self._data_manager.list_inventory()

        result: Dict[str, int] = {}
        inventory = self._data_manager.list_inventory()
        for item_id, count in inventory.items():
            try:
                item_name = self._recipe_manager.get_item_name(item_id)
                result[item_name] = count
            except Exception:
                result[item_id] = count
        return result
