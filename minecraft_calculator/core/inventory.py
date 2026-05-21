import os
from typing import Dict
from datetime import datetime
from minecraft_calculator.utils.yaml_loader import YamlLoader
from minecraft_calculator.exceptions import InvalidInputError

class Inventory:
    def __init__(self, file_path: str = None):
        if file_path is None:
            self._file_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'inventory.yaml'
            )
        else:
            self._file_path = file_path
        self._items: Dict[str, int] = {}
        self.load()

    def load(self) -> None:
        try:
            data = YamlLoader.load(self._file_path)
            self._items = data.get('items', {})
        except Exception:
            self._items = {}

    def save(self) -> None:
        data = {
            'items': self._items,
            'last_updated': datetime.now().isoformat()
        }
        YamlLoader.save(self._file_path, data)

    def add_item(self, item_id: str, count: int) -> None:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")
        
        if item_id in self._items:
            self._items[item_id] += count
        else:
            self._items[item_id] = count
        self.save()

    def remove_item(self, item_id: str, count: int) -> bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")
        
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

    def get_count(self, item_id: str) -> int:
        return self._items.get(item_id, 0)

    def clear(self) -> None:
        self._items.clear()
        self.save()

    def list_items(self) -> Dict[str, int]:
        return dict(self._items)
