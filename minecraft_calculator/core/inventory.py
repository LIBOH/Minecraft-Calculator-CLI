import os
from typing import Dict, Optional
from datetime import datetime
from minecraft_calculator.utils.yaml_loader import YamlLoader
from minecraft_calculator.exceptions import InvalidInputError, ItemNotFoundError
from minecraft_calculator.core.recipe_manager import RecipeManager


class Inventory:
    def __init__(self, file_path: str = None):
        if file_path is None:
            self._file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 'data', 'inventory.yaml'
            )
        else:
            self._file_path = file_path

        self._items: Dict[str, int] = {}
        self._recipe_manager: Optional[RecipeManager] = None
        self.load()

    def set_recipe_manager(self, recipe_manager: RecipeManager) -> None:
        """设置RecipeManager用于物品ID和名称的转换"""
        self._recipe_manager = recipe_manager

    def load(self) -> None:
        try:
            data = YamlLoader.load(self._file_path)
            self._items = data.get("items", {})
        except Exception:
            self._items = {}

    def save(self) -> None:
        data = {"items": self._items, "last_updated": datetime.now().isoformat()}
        YamlLoader.save(self._file_path, data)

    def _resolve_item_id(self, name_or_id: str) -> str:
        """将物品名或物品ID解析为物品ID"""
        if self._recipe_manager is None:
            return name_or_id
        try:
            return self._recipe_manager.get_item_id(name_or_id)
        except ItemNotFoundError:
            return name_or_id

    def _resolve_item_name(self, name_or_id: str) -> str:
        """将物品名或物品ID解析为物品名称"""
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

        if item_id in self._items:
            self._items[item_id] += count
        else:
            self._items[item_id] = count
        self.save()

    def remove_item(self, name_or_id: str, count: int) -> bool:
        if not name_or_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        item_id = self._resolve_item_id(name_or_id)

        if item_id not in self._items:
            return False

        if self._items[item_id] >= count:
            self._items[item_id] -= count
        else:
            self._items[item_id] = 0

        if self._items[item_id] == 0:
            del self._items[item_id]

        self.save()
        return True

    def get_count(self, name_or_id: str) -> int:
        """通过物品名或物品ID获取物品数量"""
        item_id = self._resolve_item_id(name_or_id)
        return self._items.get(item_id, 0)

    def get_count_by_id(self, item_id: str) -> int:
        """直接通过物品ID获取物品数量（用于计算器）"""
        if item_id in self._items:
            return self._items[item_id]

        if self._recipe_manager is not None:
            try:
                item_name = self._recipe_manager.get_item_name(item_id)
                if item_name in self._items:
                    return self._items[item_name]
            except Exception:
                pass

        return 0

    def clear(self) -> None:
        self._items.clear()
        self.save()

    def list_items(self) -> Dict[str, int]:
        """返回库存中的物品，键可以是物品ID或物品名（如果有RecipeManager）"""
        if self._recipe_manager is None:
            return dict(self._items)

        result: Dict[str, int] = {}
        for item_id, count in self._items.items():
            try:
                item_name = self._recipe_manager.get_item_name(item_id)
                result[item_name] = count
            except Exception:
                result[item_id] = count
        return result
