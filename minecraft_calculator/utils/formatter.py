from typing import Dict
from minecraft_calculator.core.calculator import CalculationResult
from minecraft_calculator.core.recipe_manager import RecipeManager
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint


console = Console()


class OutputFormatter:
    # Define styles for different indent levels
    LEVEL_STYLES = [
        "cyan",  # Level 0 - Primary recipe
        "green",  # Level 1
        "yellow",  # Level 2
        "magenta",  # Level 3
        "blue",  # Level 4
        "white",  # Level 5 and beyond
    ]

    @staticmethod
    def format_stack(needed: int, produced: int = 0, stack_size: int = 64) -> str:
        if needed <= 0:
            return f"0 = 0 × {stack_size} + 0 ... 0"

        actual_produced = produced if produced > 0 else needed
        excess = actual_produced - needed

        full_stacks = actual_produced // stack_size
        remainder = actual_produced % stack_size

        return f"{needed} = {full_stacks} × {stack_size} + {remainder} ... {excess}"

    @staticmethod
    def _build_tree(
        result: CalculationResult,
        recipe_manager: RecipeManager,
        tree: Tree = None,
        indent: int = 0,
    ) -> Tree:
        style = OutputFormatter.LEVEL_STYLES[min(indent, len(OutputFormatter.LEVEL_STYLES) - 1)]
        
        if tree is None:
            root_label = Text(f"📦 制作 {result.count} 个「{result.name}」", style=style)
            tree = Tree(root_label)
        else:
            child_label = Text(f"📦 制作 {result.count} 个「{result.name}」", style=style)
            tree = tree.add(child_label)

        # Add ingredients table
        if result.ingredients:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("材料", style="green")
            table.add_column("数量 (总需求)", style="yellow")
            table.add_column("库存使用", style="cyan")
            
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
                
                inv_used = result.inventory_used.get(ing_id, 0)
                inv_text = f"{inv_used} 个" if inv_used > 0 else "-"
                
                table.add_row(ing_name, stack_info, inv_text)
            
            tree.add(table)

        # Add children
        if result.children:
            for child in result.children:
                if child.ingredients and any(v > 0 for v in child.ingredients.values()):
                    OutputFormatter._build_tree(child, recipe_manager, tree, indent + 1)

        return tree

    @staticmethod
    def _aggregate_materials(
        result: CalculationResult,
        totals: Dict[str, int] = None,
        remaining: Dict[str, int] = None,
        inventory_used: Dict[str, int] = None,
    ) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
        """
        递归汇总所有层级的基础材料需求（只汇总没有配方的材料）
        返回: (总需求材料, 剩余需求材料, 库存使用材料)
        """
        if totals is None:
            totals = {}
        if remaining is None:
            remaining = {}
        if inventory_used is None:
            inventory_used = {}

        if not result.children:
            for ing_id, ing_count in result.remaining.items():
                if ing_count > 0:
                    remaining[ing_id] = remaining.get(ing_id, 0) + ing_count

        for ing_id, ing_count in result.inventory_used.items():
            if ing_count > 0:
                inventory_used[ing_id] = inventory_used.get(ing_id, 0) + ing_count

        for child in result.children:
            OutputFormatter._aggregate_materials(child, totals, remaining, inventory_used)

        return totals, remaining, inventory_used

    @staticmethod
    def format_summary(
        result: CalculationResult, recipe_manager: RecipeManager
    ) -> None:
        """
        显示材料汇总信息
        """
        _, remaining, inventory_used = OutputFormatter._aggregate_materials(result)

        all_materials = set(list(remaining.keys()) + list(inventory_used.keys()))
        
        if not all_materials:
            panel = Panel(
                "[green]✓ 所有材料均已从库存中获取[/green]",
                title="[bold green]📊 材料汇总[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
            rprint(panel)
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("材料", style="green")
        table.add_column("总需求", style="yellow", justify="right")
        table.add_column("库存使用", style="cyan", justify="right")
        table.add_column("仍需收集", style="red", justify="right")
        table.add_column("堆叠详情", style="dim")

        for ing_id in sorted(all_materials):
            ing_name = recipe_manager.get_item_name(ing_id)
            still_needed = remaining.get(ing_id, 0)
            used = inventory_used.get(ing_id, 0)
            total_needed = still_needed + used
            stack_size = recipe_manager.get_item_stack_size(ing_id)
            
            full_stacks = still_needed // stack_size
            remainder = still_needed % stack_size
            stack_info = f"{full_stacks}×{stack_size} + {remainder}" if still_needed > 0 else "-"

            table.add_row(
                ing_name,
                str(total_needed),
                str(used),
                str(still_needed),
                stack_info,
            )

        panel = Panel(
            table,
            title="[bold green]📊 材料汇总[/bold green]",
            subtitle=f"[dim]共 {len(all_materials)} 种材料需要收集[/dim]",
            border_style="green",
            padding=(1, 2),
        )
        rprint(panel)

    @staticmethod
    def format_result(
        result: CalculationResult, recipe_manager: RecipeManager, indent: int = 0
    ) -> None:
        tree = OutputFormatter._build_tree(result, recipe_manager)
        panel = Panel(
            tree,
            title="[bold blue]Minecraft 材料计算器[/bold blue]",
            subtitle="[dim]计算完成[/dim]",
            border_style="blue",
        )
        rprint(panel)
        
        rprint()
        
        OutputFormatter.format_summary(result, recipe_manager)

    @staticmethod
    def format_inventory(items: Dict[str, int], recipe_manager: RecipeManager) -> None:
        if not items:
            panel = Panel(
                "[red]库存为空[/red]",
                title="[bold yellow]📦 库存管理[/bold yellow]",
                border_style="yellow",
            )
            rprint(panel)
            return

        table = Table(title="", show_header=True, header_style="bold cyan")
        table.add_column("物品名称", style="green", no_wrap=True)
        table.add_column("数量", style="yellow", justify="right")
        table.add_column("堆叠详情", style="magenta")

        for name_or_id, count in sorted(items.items()):
            try:
                item_id = recipe_manager.get_item_id(name_or_id)
                item_name = recipe_manager.get_item_name(item_id)
                stack_size = recipe_manager.get_item_stack_size(item_id)
            except Exception:
                item_name = name_or_id
                stack_size = 64

            stack_info = OutputFormatter.format_stack(count, count, stack_size)
            table.add_row(item_name, str(count), stack_info)

        panel = Panel(
            table,
            title="[bold yellow]📦 库存管理[/bold yellow]",
            border_style="yellow",
        )
        rprint(panel)
