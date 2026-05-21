import os
import pytest
from minecraft_calculator.core.recipe_manager import RecipeManager, Recipe, ItemRecipe
from minecraft_calculator.exceptions import RecipeLoadError

class TestRecipeManager:
    def test_load_vanilla_recipes(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("""
items:
  redstone_comparator:
    name: 红石比较器
    recipes:
      - ingredients:
          quartz: 1
          redstone_torch: 3
          stone: 3
        result: 1
""", encoding='utf-8')
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        assert rm._vanilla_loaded is True
        assert "redstone_comparator" in rm._recipes
        assert rm._recipes["redstone_comparator"].name == "红石比较器"

    def test_get_recipes(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("""
items:
  redstone_comparator:
    name: 红石比较器
    recipes:
      - ingredients:
          quartz: 1
          redstone_torch: 3
          stone: 3
        result: 1
""", encoding='utf-8')
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        recipes = rm.get_recipes("redstone_comparator")
        assert len(recipes) == 1
        assert recipes[0].ingredients == {"quartz": 1, "redstone_torch": 3, "stone": 3}

    def test_get_item_name(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("""
items:
  redstone_comparator:
    name: 红石比较器
    recipes: []
""", encoding='utf-8')
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        assert rm.get_item_name("redstone_comparator") == "红石比较器"
        assert rm.get_item_name("unknown_item") == "unknown_item"

    def test_load_mod_recipes(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        mods_dir = recipe_dir / "mods"
        mods_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("""
items:
  iron_ingot:
    name: 铁锭
    recipes: []
""", encoding='utf-8')
        
        mod_file = mods_dir / "example_mod.yaml"
        mod_file.write_text("""
mod_id: example_mod
mod_name: Example Mod
items:
  custom_item:
    name: 自定义物品
    recipes:
      - ingredients:
          iron_ingot: 4
        result: 1
""", encoding='utf-8')
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        success = rm.load_mod_recipes("example_mod")
        assert success is True
        assert "custom_item" in rm._recipes
        assert rm.is_loaded("example_mod") is True

    def test_list_loaded_mods(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        mods_dir = recipe_dir / "mods"
        mods_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("items: {}")
        
        mod_file = mods_dir / "example_mod.yaml"
        mod_file.write_text("mod_id: example_mod\nmod_name: Example Mod\nitems: {}")
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        rm.load_mod_recipes("example_mod")
        
        assert rm.list_loaded_mods() == ["example_mod"]
