from dataclasses import dataclass
from typing import Dict, List, Optional
from minecraft_calculator.core.data_manager import DataManager
from minecraft_calculator.exceptions import ItemNotFoundError


@dataclass
class Recipe:
    ingredients: Dict[str, int]
    result: int = 1


@dataclass
class ItemRecipe:
    item_id: str
    name: str
    recipes: List[Recipe]
    stack_size: int = 64
    source_mod: str = "vanilla"


class RecipeManager:
    def __init__(self, data_manager: Optional[DataManager] = None):
        if data_manager is None:
            self._data_manager = DataManager()
        else:
            self._data_manager = data_manager
        self._name_to_id: Dict[str, str] = {}
        self._loaded_mods: set[str] = set()
        self._vanilla_loaded: bool = False
        self._load_recipes_from_data_manager()

    def _load_recipes_from_data_manager(self):
        for item_id in self._data_manager.get_all_recipes():
            item_data = self._data_manager.get_recipe(item_id)
            if item_data:
                self._name_to_id[item_data.get("name", item_id)] = item_id

    def load_vanilla_recipes(self) -> None:
        if self._vanilla_loaded:
            return
        self._vanilla_loaded = True
        self._load_recipes_from_data_manager()

    def load_mod_recipes(self, mod_id: str) -> bool:
        if mod_id in self._loaded_mods:
            return True
        self._loaded_mods.add(mod_id)
        self._data_manager.enable_mod(mod_id)
        self._load_recipes_from_data_manager()
        return True

    def unload_mod_recipes(self, mod_id: str) -> None:
        if mod_id not in self._loaded_mods:
            return
        self._loaded_mods.remove(mod_id)
        self._data_manager.disable_mod(mod_id)
        self._name_to_id.clear()
        self._load_recipes_from_data_manager()

    def get_recipes(self, item_id: str) -> List[Recipe]:
        item_data = self._data_manager.get_recipe(item_id)
        if item_data:
            recipes_data = item_data.get("recipes", [])
            return [
                Recipe(
                    ingredients=recipe.get("ingredients", {}),
                    result=recipe.get("result", 1),
                )
                for recipe in recipes_data
            ]
        return []

    def get_item_name(self, item_id: str) -> str:
        item_data = self._data_manager.get_recipe(item_id)
        if item_data:
            return item_data.get("name", item_id)
        return item_id

    def get_item_id(self, name_or_id: str) -> str:
        item_data = self._data_manager.get_recipe(name_or_id)
        if item_data:
            return name_or_id
        if name_or_id in self._name_to_id:
            return self._name_to_id[name_or_id]
        raise ItemNotFoundError(name_or_id)

    def get_item_stack_size(self, item_id: str) -> int:
        item_data = self._data_manager.get_recipe(item_id)
        if item_data:
            return item_data.get("stack", 64)
        return 64

    def is_loaded(self, mod_id: str) -> bool:
        return mod_id in self._loaded_mods

    def list_loaded_mods(self) -> List[str]:
        return self._data_manager.get_enabled_mods()

    def get_all_items(self) -> List[str]:
        return self._data_manager.get_all_recipes()

    def load_enabled_mods(self) -> None:
        """加载已启用的模组（与之前的接口兼容）"""
        for mod_id in self._data_manager.get_enabled_mods():
            self._loaded_mods.add(mod_id)

    def enable_mod(self, mod_id: str) -> bool:
        """启用模组（与之前的接口兼容）"""
        # 检查模组文件是否存在
        mod_path = self._data_manager._config_manager.get_mod_recipes_path(mod_id)
        import os

        if not os.path.exists(mod_path):
            return False
        self._data_manager.enable_mod(mod_id)
        self._loaded_mods.add(mod_id)
        self._load_recipes_from_data_manager()
        return True

    def disable_mod(self, mod_id: str) -> None:
        """禁用模组（与之前的接口兼容）"""
        self._data_manager.disable_mod(mod_id)
        if mod_id in self._loaded_mods:
            self._loaded_mods.remove(mod_id)
        self._load_recipes_from_data_manager()

    def reload(self) -> None:
        """重新加载所有配方数据"""
        self._name_to_id.clear()
        self._load_recipes_from_data_manager()
