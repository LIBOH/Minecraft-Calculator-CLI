import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from minecraft_calculator.core.data_manager import DataManager
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.core.calculator import MaterialCalculator
from minecraft_calculator.utils.formatter import OutputFormatter
from minecraft_calculator.interactive_cli import InteractiveCLI
from minecraft_calculator.core.config_manager import ConfigManager
from minecraft_calculator.exceptions import (
    ItemNotFoundError,
    RecipeLoadError,
    InvalidInputError,
)


console = Console()


@click.group()
def cli():
    pass


@cli.command()
@click.argument("name_or_id")
@click.argument("count", type=int)
@click.option(
    "--inventory",
    "-i",
    "use_inventory",
    is_flag=True,
    flag_value="",
    default=None,
    help="使用库存（使用默认库存文件）",
)
@click.option("--inventory-file", help="指定库存文件路径")
@click.option("--mods", "-m", default="", help="指定加载的模组（逗号分隔）")
def calc(name_or_id, count, use_inventory, inventory_file, mods):
    """
    计算物品数量
    """
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        if mods:
            for mod_id in mods.split(","):
                mod_id = mod_id.strip()
                if mod_id:
                    recipe_manager.load_mod_recipes(mod_id)

        inventory_instance = None
        if use_inventory is not None or inventory_file is not None:
            inv_path = inventory_file if inventory_file else None
            inventory_instance = Inventory(inv_path, data_manager)
            inventory_instance.set_recipe_manager(recipe_manager)

        calculator = MaterialCalculator(recipe_manager, inventory_instance)

        result = calculator.calculate(name_or_id, count)
        OutputFormatter.format_result(result, recipe_manager)
    except ItemNotFoundError as e:
        rprint(f"[red]错误: 物品 '{e}' 未找到[/red]")
    except RecipeLoadError as e:
        rprint(f"[red]错误: {e}[/red]")
    except InvalidInputError as e:
        rprint(f"[red]错误: {e}[/red]")
    except Exception as e:
        rprint(f"[red]未知错误: {e}[/red]")


@cli.group()
def inv():
    """
    管理库存命令
    """
    pass


@inv.command("add")
@click.argument("name_or_id")
@click.argument("count", type=int)
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inv_add(name_or_id, count, file):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        inv = Inventory(file, data_manager)
        inv.set_recipe_manager(recipe_manager)
        inv.add_item(name_or_id, count)

        resolved_name = inv._resolve_item_name(name_or_id)
        rprint(f"[green]已添加 {count} 个 {resolved_name}[/green]")
    except InvalidInputError as e:
        rprint(f"[red]错误: {e}[/red]")
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")



@inv.command("remove")
@click.argument("name_or_id")
@click.argument("count", type=int)
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inventory_remove(name_or_id, count, file):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        inv = Inventory(file, data_manager)
        inv.set_recipe_manager(recipe_manager)
        success = inv.remove_item(name_or_id, count)

        resolved_name = inv._resolve_item_name(name_or_id)
        if success:
            rprint(f"[green]已移除 {count} 个 {resolved_name}[/green]")
        else:
            rprint("[yellow]无法移除: 物品不存在或数量不足[/yellow]")
    except InvalidInputError as e:
        rprint(f"[red]错误: {e}[/red]")
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")


@inv.command("list")
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inv_list(file):
    try:
        data_manager = DataManager()
        inv = Inventory(file, data_manager)
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        inv.set_recipe_manager(recipe_manager)
        items = inv.list_items()
        OutputFormatter.format_inventory(items, recipe_manager)
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")

@inv.command("clear")
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inv_clear(file):
    try:
        data_manager = DataManager()
        inv = Inventory(file, data_manager)
        inv.clear()
        rprint("[green]库存已清空[/green]")
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")


@cli.group()
def recipe():
    """
    配方管理命令
    """
    pass


@recipe.command("list")
@click.option("--mod", "-m", default=None, help="指定模组ID")
def recipe_list(mod):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        if mod:
            recipe_manager.load_mod_recipes(mod)

        items = recipe_manager.get_all_items()
        if items:
            table = Table(
                title="[cyan]可用物品[/cyan]",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("物品名称", style="green")
            table.add_column("物品ID", style="white")

            for item in sorted(items):
                name = recipe_manager.get_item_name(item)
                table.add_row(name, item)

            panel = Panel(
                table, title="[bold cyan]📜 配方列表[/bold cyan]", border_style="cyan"
            )
            rprint(panel)
        else:
            rprint("[yellow]暂无物品[/yellow]")
    except RecipeLoadError as e:
        rprint(f"[red]错误: {e}[/red]")


@recipe.command("show")
@click.argument("name_or_id")
def recipe_show(name_or_id):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        item_id = recipe_manager.get_item_id(name_or_id)
        recipes = recipe_manager.get_recipes(item_id)
        if not recipes:
            rprint(f"[yellow]物品 '{name_or_id}' 未找到或没有配方[/yellow]")
            return

        name = recipe_manager.get_item_name(item_id)

        for idx, recipe in enumerate(recipes, 1):
            table = Table(
                title=f"[yellow]配方 {idx}[/yellow]",
                show_header=True,
                header_style="bold green",
            )
            table.add_column("材料", style="green")
            table.add_column("数量", style="yellow", justify="right")

            for ing_id, ing_count in recipe.ingredients.items():
                ing_name = recipe_manager.get_item_name(ing_id)
                table.add_row(ing_name, str(ing_count))

            table.add_section()
            table.add_row(
                f"[magenta]→ {name}[/magenta]", f"[magenta]{recipe.result}[/magenta]"
            )

            panel = Panel(
                table,
                title=f"[bold cyan]📋 「{name}」的配方[/bold cyan]",
                border_style="cyan",
            )
            rprint(panel)
    except ItemNotFoundError as e:
        rprint(f"[red]错误: 物品 '{e}' 未找到[/red]")
    except RecipeLoadError as e:
        rprint(f"[red]错误: {e}[/red]")


@recipe.command("add")
@click.argument("item_id")
@click.argument("name")
@click.argument("ingredients", nargs=-1)
@click.option("--result", "-r", type=int, default=1, help="产出数量")
@click.option("--stack", "-s", type=int, default=64, help="堆叠大小")
@click.option("--mod", "-m", default="vanilla", help="模组ID")
def recipe_add(item_id, name, ingredients, result, stack, mod):
    try:
        data_manager = DataManager()
        ingredient_dict = {}
        for ing in ingredients:
            parts = ing.split(":")
            if len(parts) == 2:
                ing_id, ing_count = parts
                try:
                    ingredient_dict[ing_id] = int(ing_count)
                except ValueError:
                    rprint(f"[red]错误: 无效的数量 '{ing_count}'[/red]")
                    return
            else:
                rprint("[red]错误: 配料格式应为 'item_id:count'[/red]")
                return

        data_manager.add_recipe(item_id, name, ingredient_dict, result, stack, mod)
        rprint(f"[green]成功添加配方: {name} ({item_id})[/green]")
    except InvalidInputError as e:
        rprint(f"[red]错误: {e}[/red]")
    except Exception as e:
        rprint(f"[red]未知错误: {e}[/red]")


@recipe.command("update")
@click.argument("item_id")
@click.option("--name", "-n", help="物品名称")
@click.option("--ingredients", "-i", multiple=True, help="配料 (格式: item_id:count)")
@click.option("--result", "-r", type=int, help="产出数量")
@click.option("--stack", "-s", type=int, help="堆叠大小")
def recipe_update(item_id, name, ingredients, result, stack):
    try:
        data_manager = DataManager()
        ingredient_dict = None
        if ingredients:
            ingredient_dict = {}
            for ing in ingredients:
                parts = ing.split(":")
                if len(parts) == 2:
                    ing_id, ing_count = parts
                    try:
                        ingredient_dict[ing_id] = int(ing_count)
                    except ValueError:
                        rprint(f"[red]错误: 无效的数量 '{ing_count}'[/red]")
                        return
                else:
                    rprint("[red]错误: 配料格式应为 'item_id:count'[/red]")
                    return

        success = data_manager.update_recipe(
            item_id, name, ingredient_dict, result, stack
        )
        if success:
            rprint(f"[green]成功更新配方: {item_id}[/green]")
        else:
            rprint(f"[yellow]未找到物品: {item_id}[/yellow]")
    except Exception as e:
        rprint(f"[red]未知错误: {e}[/red]")


@recipe.command("remove")
@click.argument("item_id")
def recipe_remove(item_id):
    try:
        data_manager = DataManager()
        success = data_manager.remove_recipe(item_id)
        if success:
            rprint(f"[green]成功删除配方: {item_id}[/green]")
        else:
            rprint(f"[yellow]未找到物品: {item_id}[/yellow]")
    except Exception as e:
        rprint(f"[red]未知错误: {e}[/red]")


@recipe.command("import")
@click.argument("file_path")
@click.option("--mod", "-m", default="vanilla", help="模组ID")
def recipe_import(file_path, mod):
    try:
        data_manager = DataManager()
        count = data_manager.import_recipes_from_file(file_path, mod)
        rprint(f"[green]成功导入 {count} 个配方[/green]")
    except InvalidInputError as e:
        rprint(f"[red]错误: {e}[/red]")
    except Exception as e:
        rprint(f"[red]未知错误: {e}[/red]")


@cli.command("i")
def i():
    """进入交互式模式"""
    _run_interactive()


def _run_interactive():
    cli = InteractiveCLI()
    cli.run()


@cli.group()
def mod():
    """模组管理命令"""
    pass


@mod.command("list")
def mod_list():
    """列出已加载的模组"""
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        mods = recipe_manager.list_loaded_mods()
        if mods:
            table = Table(title="[cyan]已加载的模组[/cyan]", show_header=False)
            table.add_column("模组ID", style="green")

            for mod_id in sorted(mods):
                table.add_row(mod_id)

            panel = Panel(
                table,
                title="[bold magenta]🔧 模组管理[/bold magenta]",
                border_style="magenta",
            )
            rprint(panel)
        else:
            rprint("[yellow]暂无加载的模组[/yellow]")
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")


@mod.command("dir")
def mod_dir():
    """列出模组目录中的所有模组（已加载和可加载的）"""
    try:
        config_manager = ConfigManager()
        mods_dir = config_manager.get_mod_recipes_dir()

        available_mods = []
        unloaded_mods = []

        if os.path.exists(mods_dir):
            for filename in os.listdir(mods_dir):
                if filename.endswith(".json"):
                    mod_id = filename[:-5]
                    available_mods.append(mod_id)

        enabled_mods = config_manager.get_enabled_mods()

        loaded_mods = [mod for mod in available_mods if mod in enabled_mods]
        unloaded_mods = [mod for mod in available_mods if mod not in enabled_mods]

        title_text = Text()
        title_text.append("📂 模组目录\n", style="bold cyan")
        title_text.append(f"目录: {mods_dir}", style="dim")

        panel = Panel(title_text, border_style="cyan", padding=(1, 2))
        rprint(panel)
        rprint()

        if loaded_mods:
            table = Table(title="[green]✓ 已加载的模组[/green]", show_header=False)
            table.add_column("序号", style="cyan", width=6)
            table.add_column("模组ID", style="green")

            for idx, mod_id in enumerate(sorted(loaded_mods), 1):
                table.add_row(str(idx), mod_id)

            panel = Panel(table, border_style="green", padding=(1, 2))
            rprint(panel)
            rprint()
        else:
            rprint("[yellow]暂无已加载的模组[/yellow]")
            rprint()

        if unloaded_mods:
            table = Table(title="[dim]○ 可加载的模组[/dim]", show_header=False)
            table.add_column("序号", style="white", width=6)
            table.add_column("模组ID", style="white")

            for idx, mod_id in enumerate(sorted(unloaded_mods), 1):
                table.add_row(str(idx), mod_id)

            panel = Panel(table, border_style="white", padding=(1, 2))
            rprint(panel)
        else:
            rprint("[dim]所有模组均已加载[/dim]")

        if not available_mods:
            rprint("\n[yellow]模组目录为空，请将模组JSON文件放入以下目录:[/yellow]")
            rprint(f"[dim]{mods_dir}[/dim]")

    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")


@mod.command("load")
@click.argument("mod_id")
def mod_load(mod_id):
    """加载指定的模组"""
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()

        success = recipe_manager.enable_mod(mod_id)
        if success:
            rprint(f"[green]模组 '{mod_id}' 加载成功[/green]")
        else:
            rprint(f"[yellow]模组 '{mod_id}' 未找到[/yellow]")
    except RecipeLoadError as e:
        rprint(f"[red]错误: {e}[/red]")


@mod.command("unload")
@click.argument("mod_id")
def mod_unload(mod_id):
    """卸载指定的模组"""
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        recipe_manager.disable_mod(mod_id)
        rprint(f"[green]模组 '{mod_id}' 已卸载[/green]")
    except Exception as e:
        rprint(f"[red]错误: {e}[/red]")


def main():
    if len(sys.argv) == 1:
        # 没有参数时进入交互模式
        interactive_cli = InteractiveCLI()
        interactive_cli.run()
    else:
        # 有参数时正常执行命令
        cli()


if __name__ == "__main__":
    main()
