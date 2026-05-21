import os
from dataclasses import dataclass
from typing import Dict, List
from minecraft_calculator.utils.yaml_loader import YamlLoader
from minecraft_calculator.exceptions import RecipeLoadError

@dataclass
class Recipe:
    ingredients: Dict[str, int]
    result: int = 1

@dataclass
class ItemRecipe:
    item_id: str
    name: str
    recipes: List[Recipe]
    source_mod: str = "vanilla"

class RecipeManager:
    def __init__(self):
        self._recipes: Dict[str, ItemRecipe] = {}
        self._loaded_mods: set[str] = set()
        self._vanilla_loaded: bool = False
        self._data_path: str = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'recipes'
        )

    def load_vanilla_recipes(self) -> None:
        if self._vanilla_loaded:
            return
        
        file_path = os.path.join(self._data_path, 'vanilla.yaml')
        
        try:
            data = YamlLoader.load(file_path)
            if 'items' in data:
                for item_id, item_data in data['items'].items():
                    recipes = []
                    for recipe_data in item_data.get('recipes', []):
                        ingredients = recipe_data.get('ingredients', {})
                        result = recipe_data.get('result', 1)
                        recipes.append(Recipe(ingredients=ingredients, result=result))
                    
                    self._recipes[item_id] = ItemRecipe(
                        item_id=item_id,
                        name=item_data.get('name', item_id),
                        recipes=recipes,
                        source_mod="vanilla"
                    )
            self._vanilla_loaded = True
        except Exception as e:
            raise RecipeLoadError(file_path, str(e))

    def load_mod_recipes(self, mod_id: str) -> bool:
        if mod_id in self._loaded_mods:
            return True
        
        file_path = os.path.join(self._data_path, 'mods', f'{mod_id}.yaml')
        
        if not os.path.exists(file_path):
            return False
        
        try:
            data = YamlLoader.load(file_path)
            if 'items' in data:
                for item_id, item_data in data['items'].items():
                    recipes = []
                    for recipe_data in item_data.get('recipes', []):
                        ingredients = recipe_data.get('ingredients', {})
                        result = recipe_data.get('result', 1)
                        recipes.append(Recipe(ingredients=ingredients, result=result))
                    
                    self._recipes[item_id] = ItemRecipe(
                        item_id=item_id,
                        name=item_data.get('name', item_id),
                        recipes=recipes,
                        source_mod=mod_id
                    )
            self._loaded_mods.add(mod_id)
            return True
        except Exception as e:
            raise RecipeLoadError(file_path, str(e))

    def unload_mod_recipes(self, mod_id: str) -> None:
        if mod_id not in self._loaded_mods:
            return
        
        self._loaded_mods.remove(mod_id)
        
        self._recipes.clear()
        self._vanilla_loaded = False
        self.load_vanilla_recipes()
        
        for mod in self._loaded_mods:
            self.load_mod_recipes(mod)

    def get_recipes(self, item_id: str) -> List[Recipe]:
        item_recipe = self._recipes.get(item_id)
        return item_recipe.recipes if item_recipe else []

    def get_item_name(self, item_id: str) -> str:
        item_recipe = self._recipes.get(item_id)
        return item_recipe.name if item_recipe else item_id

    def is_loaded(self, mod_id: str) -> bool:
        return mod_id in self._loaded_mods

    def list_loaded_mods(self) -> List[str]:
        return list(self._loaded_mods)

    def get_all_items(self) -> List[str]:
        return list(self._recipes.keys())
