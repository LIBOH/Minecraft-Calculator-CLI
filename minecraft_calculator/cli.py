import click
import sys
from colorama import init, Fore, Style
from minecraft_calculator.core.data_manager import DataManager
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.core.calculator import MaterialCalculator
from minecraft_calculator.utils.formatter import OutputFormatter
from minecraft_calculator.exceptions import (
    ItemNotFoundError,
    RecipeLoadError,
    InvalidInputError,
)

# Initialize colorama with proper Windows support
if sys.platform == "win32":
    init(autoreset=True, strip=False)
else:
    init(autoreset=True)


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
        output = OutputFormatter.format_result(result, recipe_manager)
        click.echo(output)
    except ItemNotFoundError as e:
        click.echo(f"{Fore.RED}错误: 物品 '{e}' 未找到{Style.RESET_ALL}", err=True)
    except RecipeLoadError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)
    except InvalidInputError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)
    except Exception as e:
        click.echo(f"{Fore.RED}未知错误: {e}{Style.RESET_ALL}", err=True)


@cli.group()
def inventory():
    pass


@inventory.command("add")
@click.argument("name_or_id")
@click.argument("count", type=int)
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inventory_add(name_or_id, count, file):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()

        inv = Inventory(file, data_manager)
        inv.set_recipe_manager(recipe_manager)
        inv.add_item(name_or_id, count)

        resolved_name = inv._resolve_item_name(name_or_id)
        click.echo(f"{Fore.GREEN}已添加 {count} 个 {resolved_name}{Style.RESET_ALL}")
    except InvalidInputError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@inventory.command("remove")
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
            click.echo(
                f"{Fore.GREEN}已移除 {count} 个 {resolved_name}{Style.RESET_ALL}"
            )
        else:
            click.echo(
                f"{Fore.YELLOW}无法移除: 物品不存在或数量不足{Style.RESET_ALL}",
                err=True,
            )
    except InvalidInputError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@inventory.command("list")
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inventory_list(file):
    try:
        data_manager = DataManager()
        inv = Inventory(file, data_manager)
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        inv.set_recipe_manager(recipe_manager)
        items = inv.list_items()
        output = OutputFormatter.format_inventory(items, recipe_manager)
        click.echo(output)
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@inventory.command("clear")
@click.option("--file", "-f", default=None, help="指定库存文件路径")
def inventory_clear(file):
    try:
        data_manager = DataManager()
        inv = Inventory(file, data_manager)
        inv.clear()
        click.echo(f"{Fore.GREEN}库存已清空{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@cli.group()
def recipe():
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
            click.echo(f"{Fore.CYAN}可用物品:{Style.RESET_ALL}")
            for item in sorted(items):
                name = recipe_manager.get_item_name(item)
                click.echo(
                    f"  {Fore.GREEN}{name}{Style.RESET_ALL} ({Fore.WHITE}{item}{Style.RESET_ALL})"
                )
        else:
            click.echo(f"{Fore.YELLOW}暂无物品{Style.RESET_ALL}")
    except RecipeLoadError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@recipe.command("show")
@click.argument("name_or_id")
def recipe_show(name_or_id):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()

        item_id = recipe_manager.get_item_id(name_or_id)
        recipes = recipe_manager.get_recipes(item_id)
        if not recipes:
            click.echo(
                f"{Fore.YELLOW}物品 '{name_or_id}' 未找到或没有配方{Style.RESET_ALL}",
                err=True,
            )
            return

        name = recipe_manager.get_item_name(item_id)
        click.echo(f"{Fore.CYAN}「{name}」的配方:{Style.RESET_ALL}")

        for idx, recipe in enumerate(recipes, 1):
            click.echo(f"\n{Fore.YELLOW}配方 {idx}:{Style.RESET_ALL}")
            for ing_id, ing_count in recipe.ingredients.items():
                ing_name = recipe_manager.get_item_name(ing_id)
                click.echo(f"  {Fore.GREEN}{ing_name}: {ing_count}{Style.RESET_ALL}")
            click.echo(f"  {Fore.MAGENTA}→ {name} x {recipe.result}{Style.RESET_ALL}")
    except ItemNotFoundError as e:
        click.echo(f"{Fore.RED}错误: 物品 '{e}' 未找到{Style.RESET_ALL}", err=True)
    except RecipeLoadError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@cli.group()
def mod():
    pass


@mod.command("list")
def mod_list():
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        mods = recipe_manager.list_loaded_mods()
        if mods:
            click.echo(f"{Fore.CYAN}已加载的模组:{Style.RESET_ALL}")
            for mod_id in sorted(mods):
                click.echo(f"  {Fore.GREEN}{mod_id}{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.YELLOW}暂无加载的模组{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@mod.command("load")
@click.argument("mod_id")
def mod_load(mod_id):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()

        success = recipe_manager.enable_mod(mod_id)
        if success:
            click.echo(f"{Fore.GREEN}模组 '{mod_id}' 加载成功{Style.RESET_ALL}")
        else:
            click.echo(
                f"{Fore.YELLOW}模组 '{mod_id}' 未找到{Style.RESET_ALL}", err=True
            )
    except RecipeLoadError as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


@mod.command("unload")
@click.argument("mod_id")
def mod_unload(mod_id):
    try:
        data_manager = DataManager()
        recipe_manager = RecipeManager(data_manager)
        recipe_manager.load_vanilla_recipes()
        recipe_manager.load_enabled_mods()
        recipe_manager.disable_mod(mod_id)
        click.echo(f"{Fore.GREEN}模组 '{mod_id}' 已卸载{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}错误: {e}{Style.RESET_ALL}", err=True)


if __name__ == "__main__":
    cli()
