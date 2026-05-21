from dataclasses import dataclass, field
from typing import Dict, List, Optional
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.core.strategies import RecipeSelectionStrategy, FirstRecipeStrategy
from minecraft_calculator.exceptions import ItemNotFoundError, InvalidInputError

@dataclass
class CalculationResult:
    item_id: str
    name: str
    count: int
    ingredients: Dict[str, int]
    remaining: Dict[str, int]
    children: List['CalculationResult'] = field(default_factory=list)

class MaterialCalculator:
    def __init__(
        self,
        recipe_manager: RecipeManager,
        inventory: Inventory,
        strategy: RecipeSelectionStrategy = None
    ):
        self._recipe_manager = recipe_manager
        self._inventory = inventory
        self._strategy = strategy or FirstRecipeStrategy()
        self._cache: Dict[str, Dict[str, int]] = {}

    def calculate(self, item_id: str, count: int) -> CalculationResult:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")
        
        recipes = self._recipe_manager.get_recipes(item_id)
        if not recipes:
            raise ItemNotFoundError(item_id)
        
        result = self._recursive_calc(item_id, count)
        self._deduct_inventory(result)
        return result

    def _recursive_calc(self, item_id: str, count: int, visited: Optional[set] = None) -> CalculationResult:
        if visited is None:
            visited = set()
        
        if item_id in visited:
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                ingredients={},
                remaining={},
                children=[]
            )
        
        visited.add(item_id)
        
        recipes = self._recipe_manager.get_recipes(item_id)
        if not recipes:
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                ingredients={},
                remaining={},
                children=[]
            )
        
        recipe = self._strategy.select(recipes)
        if recipe is None:
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                ingredients={},
                remaining={},
                children=[]
            )
        
        multiplier = (count + recipe.result - 1) // recipe.result
        
        ingredients: Dict[str, int] = {}
        for ing_id, ing_count in recipe.ingredients.items():
            ingredients[ing_id] = ing_count * multiplier
        
        children: List[CalculationResult] = []
        for ing_id, ing_count in ingredients.items():
            child_result = self._recursive_calc(ing_id, ing_count, visited.copy())
            children.append(child_result)
        
        visited.remove(item_id)
        
        return CalculationResult(
            item_id=item_id,
            name=self._recipe_manager.get_item_name(item_id),
            count=count,
            ingredients=ingredients,
            remaining=dict(ingredients),
            children=children
        )

    def _deduct_inventory(self, result: CalculationResult) -> None:
        for ing_id, ing_count in list(result.ingredients.items()):
            inv_count = self._inventory.get_count(ing_id)
            result.remaining[ing_id] = max(0, ing_count - inv_count)
        
        for child in result.children:
            self._deduct_inventory(child)
