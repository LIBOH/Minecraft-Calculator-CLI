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

class SmartRecipeStrategy(RecipeSelectionStrategy):
    """
    A smart strategy that prefers recipes that are more efficient,
    and avoids recipes that create cycles.
    """
    def select(self, recipes: List[Recipe]) -> Optional[Recipe]:
        if not recipes:
            return None
        
        # Prefer recipes that produce more output per unit ingredient (more efficient)
        best_efficiency: float = -1.0
        best_recipe = None
        
        for recipe in recipes:
            # Efficiency is (result count) / (total ingredients)
            total_ingredients = sum(recipe.ingredients.values())
            efficiency: float
            if total_ingredients == 0:
                efficiency = 0.0
            else:
                efficiency = recipe.result / total_ingredients
            
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_recipe = recipe
        
        return best_recipe
