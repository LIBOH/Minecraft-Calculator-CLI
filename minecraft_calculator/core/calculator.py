from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.core.strategies import (
    RecipeSelectionStrategy,
    FirstRecipeStrategy,
    SmartRecipeStrategy,
)
from minecraft_calculator.exceptions import ItemNotFoundError, InvalidInputError


@dataclass
class CalculationResult:
    item_id: str
    name: str
    count: int
    produced: int
    ingredients: Dict[str, int]
    remaining: Dict[str, int]
    children: List["CalculationResult"] = field(default_factory=list)


class MaterialCalculator:
    def __init__(
        self,
        recipe_manager: RecipeManager,
        inventory: Optional[Inventory] = None,
        strategy: RecipeSelectionStrategy = None,
    ):
        self._recipe_manager = recipe_manager
        self._inventory = inventory
        self._strategy = strategy or SmartRecipeStrategy()
        self._cache: Dict[str, Dict[str, int]] = {}

    def calculate(self, name_or_id: str, count: int) -> CalculationResult:
        if not name_or_id:
            raise InvalidInputError("物品ID不能为空")
        if count <= 0:
            raise InvalidInputError("数量必须为正整数")

        item_id = self._recipe_manager.get_item_id(name_or_id)
        recipes = self._recipe_manager.get_recipes(item_id)
        if not recipes:
            raise ItemNotFoundError(name_or_id)

        if self._inventory is not None:
            # 创建临时库存的副本，避免修改原始库存
            temp_inventory = {}
            for inv_key, inv_count in self._inventory.list_items().items():
                try:
                    # 尝试解析为物品ID或名称
                    resolved_id = self._recipe_manager.get_item_id(inv_key)
                    # 正确获取数量
                    actual_count = self._inventory.get_count_by_id(resolved_id)
                    temp_inventory[resolved_id] = actual_count
                except Exception:
                    # 如果解析失败，尝试直接用inv_key
                    # 或者看inventory里本身有没有这个键
                    try:
                        actual_count = self._inventory.get_count_by_id(inv_key)
                        if actual_count > 0:
                            temp_inventory[inv_key] = actual_count
                    except Exception:
                        pass

            # 先检查是否库存中有没有直接有我们要制作的物品（即顶层物品本身）
            inv_count = temp_inventory.get(item_id, 0)
            actual_needed = max(0, count - inv_count)

            if actual_needed == 0:
                return CalculationResult(
                    item_id=item_id,
                    name=self._recipe_manager.get_item_name(item_id),
                    count=count,
                    produced=0,
                    ingredients={},
                    remaining={},
                    children=[],
                )

            # 使用临时库存进行计算
            result, _ = self._recursive_calc(item_id, actual_needed, temp_inventory)
        else:
            # 没有库存，直接计算
            result, _ = self._recursive_calc(item_id, count, {})

        return result

    def _recursive_calc(
        self,
        item_id: str,
        count: int,
        temp_inventory: Dict[str, int],
        visited: Optional[set] = None,
    ) -> Tuple[CalculationResult, Dict[str, int]]:
        """
        递归计算所需材料
        返回: (CalculationResult, 更新后的临时库存)
        """
        if visited is None:
            visited = set()

        # 检查我们是否在循环引用
        if item_id in visited:
            remaining = {}
            if count > 0:
                remaining[item_id] = count
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                produced=count,
                ingredients={},
                remaining=remaining,
                children=[],
            ), temp_inventory

        visited.add(item_id)

        recipes = self._recipe_manager.get_recipes(item_id)
        if not recipes:
            # 没有配方，视为基础材料
            visited.remove(item_id)
            remaining = {}
            if count > 0:
                remaining[item_id] = count
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                produced=count,
                ingredients={},
                remaining=remaining,
                children=[],
            ), temp_inventory

        # 过滤掉会造成循环的配方
        valid_recipes = []
        for recipe in recipes:
            has_cycle = any(ing_id in visited for ing_id in recipe.ingredients.keys())
            if not has_cycle:
                valid_recipes.append(recipe)

        # 如果没有有效配方，也视为基础材料
        if not valid_recipes:
            visited.remove(item_id)
            remaining = {}
            if count > 0:
                remaining[item_id] = count
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                produced=count,
                ingredients={},
                remaining=remaining,
                children=[],
            ), temp_inventory

        recipe = self._strategy.select(valid_recipes)
        if recipe is None:
            visited.remove(item_id)
            remaining = {}
            if count > 0:
                remaining[item_id] = count
            return CalculationResult(
                item_id=item_id,
                name=self._recipe_manager.get_item_name(item_id),
                count=count,
                produced=count,
                ingredients={},
                remaining=remaining,
                children=[],
            ), temp_inventory

        multiplier = (count + recipe.result - 1) // recipe.result
        produced = multiplier * recipe.result

        ingredients: Dict[str, int] = {}
        for ing_id, ing_count in recipe.ingredients.items():
            ingredients[ing_id] = ing_count * multiplier

        remaining = {}
        children: List[CalculationResult] = []

        # 创建当前层级的临时库存副本，避免修改上一级的库存
        current_temp = dict(temp_inventory)

        # 按配方的原始顺序处理材料
        for ing_id, ing_total in ingredients.items():
            # 从当前临时库存中扣减
            avl = current_temp.get(ing_id, 0)
            use = min(avl, ing_total)

            if use > 0:
                current_temp[ing_id] = avl - use
                if current_temp[ing_id] == 0:
                    del current_temp[ing_id]

            actual = ing_total - use
            remaining[ing_id] = actual

            if actual > 0:
                child, current_temp = self._recursive_calc(
                    ing_id, actual, current_temp, visited.copy()
                )
                children.append(child)

        visited.remove(item_id)
        return CalculationResult(
            item_id=item_id,
            name=self._recipe_manager.get_item_name(item_id),
            count=count,
            produced=produced,
            ingredients=ingredients,
            remaining=remaining,
            children=children,
        ), current_temp
