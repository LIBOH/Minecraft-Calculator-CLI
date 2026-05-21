import pytest
from minecraft_calculator.core.calculator import MaterialCalculator, CalculationResult
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.exceptions import ItemNotFoundError, InvalidInputError

class TestMaterialCalculator:
    def test_calculate_simple(self, tmp_path):
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
  quartz:
    name: 石英
    recipes: []
  redstone_torch:
    name: 红石火把
    recipes: []
  stone:
    name: 石头
    recipes: []
""", encoding='utf-8')
        
        inv_file = tmp_path / "inventory.yaml"
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        inv = Inventory(str(inv_file))
        calculator = MaterialCalculator(rm, inv)
        
        result = calculator.calculate("redstone_comparator", 1)
        
        assert result.item_id == "redstone_comparator"
        assert result.count == 1
        assert result.ingredients == {"quartz": 1, "redstone_torch": 3, "stone": 3}

    def test_calculate_recursive(self, tmp_path):
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
  redstone_torch:
    name: 红石火把
    recipes:
      - ingredients:
          redstone_dust: 1
          stick: 1
        result: 1
  quartz:
    name: 石英
    recipes: []
  redstone_dust:
    name: 红石粉
    recipes: []
  stick:
    name: 木棍
    recipes: []
  stone:
    name: 石头
    recipes: []
""", encoding='utf-8')
        
        inv_file = tmp_path / "inventory.yaml"
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        inv = Inventory(str(inv_file))
        calculator = MaterialCalculator(rm, inv)
        
        result = calculator.calculate("redstone_comparator", 1)
        
        assert len(result.children) > 0
        
        torch_child = None
        for child in result.children:
            if child.item_id == "redstone_torch":
                torch_child = child
                break
        
        assert torch_child is not None
        assert torch_child.count == 3
        assert torch_child.ingredients == {"redstone_dust": 3, "stick": 3}

    def test_calculate_with_inventory(self, tmp_path):
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
  quartz:
    name: 石英
    recipes: []
  redstone_torch:
    name: 红石火把
    recipes: []
  stone:
    name: 石头
    recipes: []
""", encoding='utf-8')
        
        inv_file = tmp_path / "inventory.yaml"
        inv_file.write_text("""
items:
  quartz: 1
  stone: 1
last_updated: 2024-01-01T12:00:00
""", encoding='utf-8')
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        inv = Inventory(str(inv_file))
        calculator = MaterialCalculator(rm, inv)
        
        result = calculator.calculate("redstone_comparator", 1)
        
        assert result.remaining["quartz"] == 0
        assert result.remaining["stone"] == 2
        assert result.remaining["redstone_torch"] == 3

    def test_calculate_item_not_found(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("items: {}")
        
        inv_file = tmp_path / "inventory.yaml"
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        inv = Inventory(str(inv_file))
        calculator = MaterialCalculator(rm, inv)
        
        with pytest.raises(ItemNotFoundError):
            calculator.calculate("unknown_item", 1)

    def test_calculate_invalid_input(self, tmp_path):
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir()
        
        vanilla_file = recipe_dir / "vanilla.yaml"
        vanilla_file.write_text("items: {}")
        
        inv_file = tmp_path / "inventory.yaml"
        
        rm = RecipeManager()
        rm._data_path = str(recipe_dir)
        rm.load_vanilla_recipes()
        
        inv = Inventory(str(inv_file))
        calculator = MaterialCalculator(rm, inv)
        
        with pytest.raises(InvalidInputError):
            calculator.calculate("", 1)
        
        with pytest.raises(InvalidInputError):
            calculator.calculate("item", 0)
        
        with pytest.raises(InvalidInputError):
            calculator.calculate("item", -1)
