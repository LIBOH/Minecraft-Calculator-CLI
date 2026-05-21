from typing import Dict
import sys
from minecraft_calculator.core.calculator import CalculationResult
from minecraft_calculator.core.recipe_manager import RecipeManager
from colorama import init, Fore, Style

# Initialize colorama with proper Windows support
if sys.platform == "win32":
    init(autoreset=True, strip=False)
else:
    init(autoreset=True)


class OutputFormatter:
    # Define colors for different indent levels
    LEVEL_COLORS = [
        Fore.CYAN,  # Level 0 - Primary recipe (cyan)
        Fore.GREEN,  # Level 1 - Green
        Fore.YELLOW,  # Level 2 - Yellow
        Fore.MAGENTA,  # Level 3 - Magenta
        Fore.BLUE,  # Level 4 - Blue
        Fore.WHITE,  # Level 5 and beyond - White
    ]

    @staticmethod
    def format_stack(needed: int, produced: int = 0, stack_size: int = 64) -> str:
        if needed <= 0:
            return f"0 = 0 x {stack_size} + 0 ... 0"

        actual_produced = produced if produced > 0 else needed
        excess = actual_produced - needed

        full_stacks = actual_produced // stack_size
        remainder = actual_produced % stack_size

        return f"{needed} = {full_stacks} x {stack_size} + {remainder} ... {excess}"

    @staticmethod
    def format_result(
        result: CalculationResult, recipe_manager: RecipeManager, indent: int = 0
    ) -> str:
        lines = []
        prefix = "  " * indent

        # Get color for current level
        level_color = OutputFormatter.LEVEL_COLORS[
            min(indent, len(OutputFormatter.LEVEL_COLORS) - 1)
        ]

        lines.append(
            f"{prefix}{level_color}制作「{result.count}」个「{result.name}」需要:{Style.RESET_ALL}"
        )

        for ing_id, _ in result.ingredients.items():
            ing_name = recipe_manager.get_item_name(ing_id)
            stack_size = recipe_manager.get_item_stack_size(ing_id)
            child_produced = 0
            for child in result.children:
                if child.item_id == ing_id:
                    child_produced = child.produced
                    break
            stack_info = OutputFormatter.format_stack(
                result.remaining.get(ing_id, 0), child_produced, stack_size
            )

            # Check if this ingredient was partially or fully from inventory
            inv_used = result.inventory_used.get(ing_id, 0)
            if inv_used > 0:
                lines.append(
                    f"{prefix}{level_color}  {ing_name}: {stack_info} {Fore.WHITE}(从库存使用 {inv_used} 个){Style.RESET_ALL}"
                )
            else:
                lines.append(
                    f"{prefix}{level_color}  {ing_name}: {stack_info}{Style.RESET_ALL}"
                )

        if result.children:
            lines.append(f"{prefix}{level_color}{'-' * 40}{Style.RESET_ALL}")
            for child in result.children:
                if child.ingredients and any(v > 0 for v in child.ingredients.values()):
                    child_output = OutputFormatter.format_result(
                        child, recipe_manager, indent + 1
                    )
                    lines.append(child_output)

        return "\n".join(lines)

    @staticmethod
    def format_inventory(items: Dict[str, int], recipe_manager: RecipeManager) -> str:
        if not items:
            return f"{Fore.RED}库存为空{Style.RESET_ALL}"

        lines = [f"{Fore.CYAN}库存列表:{Style.RESET_ALL}"]
        for name_or_id, count in sorted(items.items()):
            try:
                item_id = recipe_manager.get_item_id(name_or_id)
                item_name = recipe_manager.get_item_name(item_id)
                stack_size = recipe_manager.get_item_stack_size(item_id)
            except Exception:
                item_name = name_or_id
                stack_size = 64

            stack_info = OutputFormatter.format_stack(count, count, stack_size)
            lines.append(f"  {Fore.GREEN}{item_name}: {stack_info}{Style.RESET_ALL}")

        return "\n".join(lines)
