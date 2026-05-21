import click
from minecraft_calculator.core.recipe_manager import RecipeManager
from minecraft_calculator.core.inventory import Inventory
from minecraft_calculator.core.calculator import MaterialCalculator
from minecraft_calculator.utils.formatter import OutputFormatter
from minecraft_calculator.exceptions import ItemNotFoundError, RecipeLoadError, InvalidInputError

@click.group()
def cli():
    pass

@cli.command()
@click.argument('item_id')
@click.argument('count', type=int)
@click.option('--inventory', '-i', default=None, help='指定库存文件路径')
@click.option('--mods', '-m', default='', help='指定加载的模组（逗号分隔）')
def calc(item_id, count, inventory, mods):
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        
        if mods:
            for mod_id in mods.split(','):
                mod_id = mod_id.strip()
                if mod_id:
                    recipe_manager.load_mod_recipes(mod_id)
        
        inventory_instance = Inventory(inventory)
        calculator = MaterialCalculator(recipe_manager, inventory_instance)
        
        result = calculator.calculate(item_id, count)
        output = OutputFormatter.format_result(result, recipe_manager)
        click.echo(output)
    except ItemNotFoundError as e:
        click.echo(f"错误: {e}", err=True)
    except RecipeLoadError as e:
        click.echo(f"错误: {e}", err=True)
    except InvalidInputError as e:
        click.echo(f"错误: {e}", err=True)
    except Exception as e:
        click.echo(f"未知错误: {e}", err=True)

@cli.group()
def inventory():
    pass

@inventory.command('add')
@click.argument('item_id')
@click.argument('count', type=int)
@click.option('--file', '-f', default=None, help='指定库存文件路径')
def inventory_add(item_id, count, file):
    try:
        inv = Inventory(file)
        inv.add_item(item_id, count)
        click.echo(f"已添加 {count} 个 {item_id}")
    except InvalidInputError as e:
        click.echo(f"错误: {e}", err=True)

@inventory.command('remove')
@click.argument('item_id')
@click.argument('count', type=int)
@click.option('--file', '-f', default=None, help='指定库存文件路径')
def inventory_remove(item_id, count, file):
    try:
        inv = Inventory(file)
        success = inv.remove_item(item_id, count)
        if success:
            click.echo(f"已移除 {count} 个 {item_id}")
        else:
            click.echo("无法移除: 物品不存在或数量不足", err=True)
    except InvalidInputError as e:
        click.echo(f"错误: {e}", err=True)

@inventory.command('list')
@click.option('--file', '-f', default=None, help='指定库存文件路径')
def inventory_list(file):
    try:
        inv = Inventory(file)
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        items = inv.list_items()
        output = OutputFormatter.format_inventory(items, recipe_manager)
        click.echo(output)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)

@inventory.command('clear')
@click.option('--file', '-f', default=None, help='指定库存文件路径')
def inventory_clear(file):
    try:
        inv = Inventory(file)
        inv.clear()
        click.echo("库存已清空")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)

@cli.group()
def recipe():
    pass

@recipe.command('list')
@click.option('--mod', '-m', default=None, help='指定模组ID')
def recipe_list(mod):
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        
        if mod:
            recipe_manager.load_mod_recipes(mod)
        
        items = recipe_manager.get_all_items()
        if items:
            click.echo("可用物品:")
            for item in sorted(items):
                name = recipe_manager.get_item_name(item)
                click.echo(f"  {item} - {name}")
        else:
            click.echo("暂无物品")
    except RecipeLoadError as e:
        click.echo(f"错误: {e}", err=True)

@recipe.command('show')
@click.argument('item_id')
def recipe_show(item_id):
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        
        recipes = recipe_manager.get_recipes(item_id)
        if not recipes:
            click.echo(f"物品 '{item_id}' 未找到或没有配方", err=True)
            return
        
        name = recipe_manager.get_item_name(item_id)
        click.echo(f"「{name}」的配方:")
        
        for idx, recipe in enumerate(recipes, 1):
            click.echo(f"\n配方 {idx}:")
            for ing_id, ing_count in recipe.ingredients.items():
                ing_name = recipe_manager.get_item_name(ing_id)
                click.echo(f"  {ing_name} x {ing_count}")
            click.echo(f"  → {name} x {recipe.result}")
    except RecipeLoadError as e:
        click.echo(f"错误: {e}", err=True)

@cli.group()
def mod():
    pass

@mod.command('list')
def mod_list():
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        mods = recipe_manager.list_loaded_mods()
        if mods:
            click.echo("已加载的模组:")
            for mod_id in sorted(mods):
                click.echo(f"  {mod_id}")
        else:
            click.echo("暂无加载的模组")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)

@mod.command('load')
@click.argument('mod_id')
def mod_load(mod_id):
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        
        success = recipe_manager.load_mod_recipes(mod_id)
        if success:
            click.echo(f"模组 '{mod_id}' 加载成功")
        else:
            click.echo(f"模组 '{mod_id}' 未找到", err=True)
    except RecipeLoadError as e:
        click.echo(f"错误: {e}", err=True)

@mod.command('unload')
@click.argument('mod_id')
def mod_unload(mod_id):
    try:
        recipe_manager = RecipeManager()
        recipe_manager.load_vanilla_recipes()
        recipe_manager.unload_mod_recipes(mod_id)
        click.echo(f"模组 '{mod_id}' 已卸载")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)

if __name__ == '__main__':
    cli()
