from abc import ABC, abstractmethod
from typing import List, Optional
from minecraft_calculator.core.recipe_manager import Recipe

class RecipeSelectionStrategy(ABC):
    @abstractmethod
    def select(self, recipes: List[Recipe]) -> Optional[Recipe]:
        pass

class FirstRecipeStrategy(RecipeSelectionStrategy):
    def select(self, recipes: List[Recipe]) -> Optional[Recipe]:
        return recipes[0] if recipes else None

class MinIngredientStrategy(RecipeSelectionStrategy):
    def select(self, recipes: List[Recipe]) -> Optional[Recipe]:
        if not recipes:
            return None
        
        min_ingredients = float('inf')
        selected = None
        
        for recipe in recipes:
            ingredient_count = len(recipe.ingredients)
            if ingredient_count < min_ingredients:
                min_ingredients = ingredient_count
                selected = recipe
        
        return selected

class MinTotalCountStrategy(RecipeSelectionStrategy):
    def select(self, recipes: List[Recipe]) -> Optional[Recipe]:
        if not recipes:
            return None
        
        min_total = float('inf')
        selected = None
        
        for recipe in recipes:
            total = sum(recipe.ingredients.values()) / recipe.result
            if total < min_total:
                min_total = total
                selected = recipe
        
        return selected
