import pytest
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.exceptions import InvalidInputError

class TestInventory:
    def test_add_item(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        inv.add_item("iron_ingot", 10)
        
        assert inv.get_count("iron_ingot") == 10
        
        inv.add_item("iron_ingot", 5)
        assert inv.get_count("iron_ingot") == 15

    def test_remove_item(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        inv.add_item("iron_ingot", 10)
        
        result = inv.remove_item("iron_ingot", 3)
        assert result is True
        assert inv.get_count("iron_ingot") == 7
        
        result = inv.remove_item("iron_ingot", 10)
        assert result is True
        assert inv.get_count("iron_ingot") == 0

    def test_remove_item_not_found(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        result = inv.remove_item("nonexistent", 5)
        assert result is False

    def test_get_count(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        inv.add_item("diamond", 5)
        
        assert inv.get_count("diamond") == 5
        assert inv.get_count("nonexistent") == 0

    def test_clear(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        inv.add_item("iron_ingot", 10)
        inv.add_item("diamond", 5)
        
        inv.clear()
        
        assert inv.list_items() == {}

    def test_list_items(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        inv.add_item("iron_ingot", 10)
        inv.add_item("diamond", 5)
        
        items = inv.list_items()
        assert items == {"iron_ingot": 10, "diamond": 5}

    def test_add_item_invalid_input(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        
        with pytest.raises(InvalidInputError):
            inv.add_item("", 5)
        
        with pytest.raises(InvalidInputError):
            inv.add_item("iron_ingot", -1)
        
        with pytest.raises(InvalidInputError):
            inv.add_item("iron_ingot", 0)

    def test_remove_item_invalid_input(self, tmp_path):
        inv_file = tmp_path / "inventory.yaml"
        
        inv = Inventory(str(inv_file))
        
        with pytest.raises(InvalidInputError):
            inv.remove_item("", 5)
        
        with pytest.raises(InvalidInputError):
            inv.remove_item("iron_ingot", -1)
