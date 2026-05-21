import os
from typing import Dict, Optional
from datetime import datetime
from minecraft_calculator.utils.yaml_loader import YamlLoader
from minecraft_calculator.exceptions import InvalidInputError

def get_user_data_dir() -> str:
    """获取用户数据目录"""
    if os.name == 'nt':  # Windows
        base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(base_dir, 'minecraft_material_calculator')
    else:  # Linux/macOS
        base_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        return os.path.join(base_dir, 'minecraft_material_calculator')

class Inventory:
    def __init__(self, file_path: str = None):
        if file_path is None:
            user_dir = get_user_data_dir()
            os.makedirs(user_dir, exist_ok=True)
            self._file_path = os.path.join(user_dir, 'inventory.yaml')
        else:
            self._file_path = file_path
        self._items_by_name: Dict[str, int] = {}
        self._recipe_manager: Optional['RecipeManager'] = None
        self.load()

    def set_recipe_manager(self, recipe_manager: 'RecipeManager') -> None:
        self._recipe_manager = recipe_manager

    def load(self) -> None:
        try:
            data = YamlLoader.load(self._file_path)
            self._items_by_name = data.get('items', {})
        except Exception:
            self._items_by_name = {}

    def save(self) -> None:
        data = {
            'items': self._items_by_name,
            'last_updated': datetime.now().isoformat()
        }
        YamlLoader.save(self._file_path, data)

    def add_item(self, name_or_id: str, count: int) -> None:
        if not name_or_id:
            raise InvalidInputError("物品名称或ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")
        
        item_name = self._resolve_item_name(name_or_id)
        
        if item_name in self._items_by_name:
            self._items_by_name[item_name] += count
        else:
            self._items_by_name[item_name] = count
        self.save()

    def remove_item(self, name_or_id: str, count: int) -> bool:
        if not name_or_id:
            raise InvalidInputError("物品名称或ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")
        
        item_name = self._resolve_item_name(name_or_id)
        
        if item_name not in self._items_by_name:
            return False
        
        if self._items_by_name[item_name] >= count:
            self._items_by_name[item_name] -= count
        else:
            self._items_by_name[item_name] = 0
        
        if self._items_by_name[item_name] == 0:
            del self._items_by_name[item_name]
        
        self.save()
        return True

    def get_count(self, name_or_id: str) -> int:
        self.load()  # 每次获取物品数量时重新加载文件
        item_name = self._resolve_item_name(name_or_id)
        return self._items_by_name.get(item_name, 0)

    def get_count_by_id(self, item_id: str) -> int:
        self.load()
        if self._recipe_manager:
            try:
                item_name = self._recipe_manager.get_item_name(item_id)
                return self._items_by_name.get(item_name, 0)
            except Exception:
                pass
        return self._items_by_name.get(item_id, 0)

    def clear(self) -> None:
        self._items_by_name.clear()
        self.save()

    def list_items(self) -> Dict[str, int]:
        self.load()  # 每次列出物品时重新加载文件
        return dict(self._items_by_name)

    def get_items_by_id(self) -> Dict[str, int]:
        self.load()
        items: Dict[str, int] = {}
        if self._recipe_manager:
            for name, count in self._items_by_name.items():
                try:
                    item_id = self._recipe_manager.get_item_id(name)
                    items[item_id] = count
                except Exception:
                    items[name] = count
        else:
            items = dict(self._items_by_name)
        return items

    def _resolve_item_name(self, name_or_id: str) -> str:
        if self._recipe_manager:
            try:
                item_id = self._recipe_manager.get_item_id(name_or_id)
                return self._recipe_manager.get_item_name(item_id)
            except Exception:
                pass
        return name_or_id
