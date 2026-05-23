from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
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


console = Console()


class InteractiveCLI:
    def __init__(self):
        self.data_manager = DataManager()
        self.recipe_manager = RecipeManager(self.data_manager)
        self.recipe_manager.load_vanilla_recipes()
        self.recipe_manager.load_enabled_mods()
        self.inventory = Inventory(None, self.data_manager)
        self.inventory.set_recipe_manager(self.recipe_manager)
        self.calculator = MaterialCalculator(self.recipe_manager, self.inventory)
        self.use_inventory = False

    def run(self):
        self._show_welcome()

        while True:
            try:
                choice = self._show_main_menu()
                if choice == 0:
                    self._show_help()
                elif choice == 1:
                    self._material_calculator()
                elif choice == 2:
                    self._item_search()
                elif choice == 3:
                    self._recipe_manager()
                elif choice == 4:
                    self._inventory_manager()
                elif choice == 5:
                    self._mod_manager()
                elif choice == 6:
                    rprint(
                        "\n[bold cyan]再见！感谢使用 Minecraft 材料计算器！[/bold cyan]\n"
                    )
                    break
            except KeyboardInterrupt:
                rprint("\n\n[yellow]操作已取消[/yellow]")
            except Exception as e:
                rprint(f"\n[red]错误: {e}[/red]")

    def _show_welcome(self):
        welcome_text = Text()
        welcome_text.append("欢迎使用 Minecraft 材料计算器！\n", style="bold cyan")
        welcome_text.append("为您提供便捷的物品配方计算服务", style="dim")

        panel = Panel(
            welcome_text,
            title="[bold blue]🎮 Minecraft Calculator[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        rprint(panel)
        rprint()

    def _show_main_menu(self) -> int:
        menu_table = Table(
            title="", show_header=False, border_style=None, pad_edge=False
        )
        menu_table.add_column("序号", style="cyan bold", width=6)
        menu_table.add_column("功能", style="white", width=25)
        menu_table.add_column("说明", style="dim")

        menu_table.add_row("[1]", "📊 材料计算", "计算合成物品所需的材料")
        menu_table.add_row("[2]", "🔍 物品搜索", "搜索物品名称或ID")
        menu_table.add_row("[3]", "📋 配方管理", "查看和管理物品配方")
        menu_table.add_row("[4]", "📦 库存管理", "管理你的物品库存")
        menu_table.add_row("[5]", "🔧 模组管理", "加载和卸载模组")
        menu_table.add_row("[0]", "❓ 帮助", "显示帮助信息")
        menu_table.add_row("[Q]", "🚪 退出", "退出程序")

        panel = Panel(
            menu_table,
            title="[bold magenta]主菜单[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
        rprint(panel)
        rprint()

        choice_map = {
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "0": 0,
            "q": 6,
            "quit": 6,
            "exit": 6,
        }

        while True:
            user_input = (
                console.input("[bold cyan]请输入选项 [1-6/0/Q]: [/bold cyan]")
                .strip()
                .lower()
            )
            if user_input in choice_map:
                return choice_map[user_input]
            rprint("[yellow]无效选项，请重新输入[/yellow]")

    def _show_help(self):
        help_text = Text()
        help_text.append("Minecraft 材料计算器 - 帮助指南\n\n", style="bold cyan")

        help_text.append("📌 基本使用\n", style="bold green")
        help_text.append("  • 通过输入序号选择功能菜单\n")
        help_text.append("  • 在任何时候输入 'Q' 返回上级菜单\n")
        help_text.append("  • 输入 '0' 查看帮助信息\n\n")

        help_text.append("📊 材料计算\n", style="bold green")
        help_text.append("  • 输入物品名称或ID和数量\n")
        help_text.append("  • 系统会自动计算所需的所有材料\n")
        help_text.append("  • 可以选择是否启用库存扣除\n\n")

        help_text.append("🔍 物品搜索\n", style="bold green")
        help_text.append("  • 输入关键词搜索物品\n")
        help_text.append("  • 支持中文名称和英文ID搜索\n\n")

        help_text.append("📋 配方管理\n", style="bold green")
        help_text.append("  • 查看所有可用配方\n")
        help_text.append("  • 查看特定物品的配方详情\n")
        help_text.append("  • 支持按模组筛选配方\n\n")

        help_text.append("📦 库存管理\n", style="bold green")
        help_text.append("  • 添加/移除物品到库存\n")
        help_text.append("  • 列出当前库存\n")
        help_text.append("  • 清空库存\n\n")

        help_text.append("🔧 模组管理\n", style="bold green")
        help_text.append("  • 浏览模组目录，查看所有可用模组\n")
        help_text.append("  • 查看已加载的模组\n")
        help_text.append("  • 加载/卸载模组\n")
        help_text.append("  • 加载的模组物品可用于计算\n")
        help_text.append("  • 已加载和可加载的模组会分类显示\n\n")

        help_text.append("💡 提示\n", style="bold yellow")
        help_text.append("  • 物品ID示例: redstone_dust, quartz, iron_ingot\n")
        help_text.append("  • 中文名称示例: 红石粉, 石英, 铁锭\n")
        help_text.append("  • 数量必须为正整数\n")

        panel = Panel(
            help_text,
            title="[bold magenta]📖 帮助信息[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
        rprint(panel)
        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _material_calculator(self):
        rprint("\n[bold cyan]📊 材料计算[/bold cyan]")
        rprint("[dim]输入 'Q' 返回主菜单[/dim]\n")

        while True:
            item_input = console.input(
                "[green]请输入物品名称或ID (输入 Q 返回): [/green]"
            ).strip()
            if item_input.lower() == "q":
                return

            if not item_input:
                rprint("[yellow]请输入物品名称或ID[/yellow]")
                continue

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")
                rprint("[dim]提示: 可以使用物品搜索功能查找正确的物品名称或ID[/dim]\n")

        while True:
            try:
                count_input = console.input(
                    "[green]请输入数量 (输入 Q 返回): [/green]"
                ).strip()
                if count_input.lower() == "q":
                    return
                count = int(count_input)
                if count <= 0:
                    rprint("[yellow]数量必须为正整数[/yellow]")
                    continue
                break
            except ValueError:
                rprint("[red]错误: 数量必须是整数[/red]")

        use_inv = Confirm.ask(
            f"\n[cyan]是否使用库存？[/cyan]\n"
            f"[dim]当前库存状态: {'已启用' if self.use_inventory else '已禁用'}[/dim]\n"
            f"[green]输入 Y 使用库存，N 跳过库存[/green]",
            default=self.use_inventory,
        )

        rprint()

        try:
            inv = self.inventory if use_inv else None
            calculator = MaterialCalculator(self.recipe_manager, inv)
            result = calculator.calculate(item_id, count)
            OutputFormatter.format_result(result, self.recipe_manager)

            if use_inv:
                rprint("\n[green]✓ 已扣除库存中的材料[/green]")
        except ItemNotFoundError as e:
            rprint(f"[red]错误: 物品 '{e}' 未找到[/red]")
        except RecipeLoadError as e:
            rprint(f"[red]错误: {e}[/red]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _item_search(self):
        rprint("\n[bold cyan]🔍 物品搜索[/bold cyan]")
        rprint("[dim]输入 'Q' 返回主菜单[/dim]\n")

        while True:
            keyword = console.input(
                "[green]请输入搜索关键词 (输入 Q 返回): [/green]"
            ).strip()
            if keyword.lower() == "q":
                return

            if not keyword:
                rprint("[yellow]请输入搜索关键词[/yellow]")
                continue

            all_items = self.recipe_manager.get_all_items()
            results = []

            keyword_lower = keyword.lower()
            for item_id in all_items:
                name = self.recipe_manager.get_item_name(item_id)
                if keyword_lower in item_id.lower() or keyword_lower in name.lower():
                    results.append((item_id, name))

            if results:
                table = Table(
                    title=f"[cyan]找到 {len(results)} 个匹配的物品[/cyan]",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("物品ID", style="cyan")
                table.add_column("物品名称", style="green")
                table.add_column("来源", style="dim")

                for item_id, name in sorted(results, key=lambda x: x[1]):
                    mod_source = (
                        self.data_manager.get_recipe(item_id).get(
                            "_source_mod", "unknown"
                        )
                        if hasattr(self.data_manager, "get_recipe")
                        else "unknown"
                    )
                    table.add_row(item_id, name, f"[dim]{mod_source}[/dim]")

                rprint()
                panel = Panel(table, border_style="cyan", padding=(1, 2))
                rprint(panel)
            else:
                rprint(f"[yellow]未找到包含 '{keyword}' 的物品[/yellow]")

            rprint()

    def _recipe_manager(self):
        while True:
            rprint("\n[bold cyan]📋 配方管理[/bold cyan]")
            rprint("[dim]输入 'Q' 返回主菜单[/dim]\n")

            submenu_table = Table(
                title="", show_header=False, border_style=None, pad_edge=False
            )
            submenu_table.add_column("序号", style="cyan bold", width=6)
            submenu_table.add_column("功能", style="white", width=30)

            submenu_table.add_row("[1]", "📜 列出所有配方")
            submenu_table.add_row("[2]", "🔍 查看物品配方")
            submenu_table.add_row("[3]", "🏷️ 按模组查看配方")
            submenu_table.add_row("[4]", "➕ 添加配方")
            submenu_table.add_row("[5]", "✏️ 更新配方")
            submenu_table.add_row("[6]", "🗑️ 删除配方")
            submenu_table.add_row("[7]", "📥 导入配方")
            submenu_table.add_row("[Q]", "↩️ 返回主菜单")

            panel = Panel(submenu_table, border_style="cyan", padding=(1, 2))
            rprint(panel)

            choice = (
                console.input("\n[bold cyan]请输入选项: [/bold cyan]").strip().lower()
            )

            if choice == "q":
                return
            elif choice == "1":
                self._recipe_list_all()
            elif choice == "2":
                self._recipe_show_single()
            elif choice == "3":
                self._recipe_list_by_mod()
            elif choice == "4":
                self._recipe_add()
            elif choice == "5":
                self._recipe_update()
            elif choice == "6":
                self._recipe_remove()
            elif choice == "7":
                self._recipe_import()
            else:
                rprint("[yellow]无效选项[/yellow]")

    def _recipe_list_all(self):
        rprint("\n[cyan]📜 所有可用配方[/cyan]\n")

        items = self.recipe_manager.get_all_items()
        if items:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("物品名称", style="green")
            table.add_column("物品ID", style="white")

            for item in sorted(
                items, key=lambda x: self.recipe_manager.get_item_name(x)
            ):
                name = self.recipe_manager.get_item_name(item)
                table.add_row(name, item)

            panel = Panel(
                table,
                title=f"[magenta]共 {len(items)} 个物品[/magenta]",
                border_style="magenta",
                padding=(1, 2),
            )
            rprint(panel)
        else:
            rprint("[yellow]暂无物品[/yellow]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _recipe_show_single(self):
        rprint("\n[cyan]🔍 查看物品配方[/cyan]")

        while True:
            item_input = console.input(
                "[green]请输入物品名称或ID (输入 Q 返回): [/green]"
            ).strip()
            if item_input.lower() == "q":
                return

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                recipes = self.recipe_manager.get_recipes(item_id)

                if not recipes:
                    rprint(f"[yellow]物品 '{item_input}' 没有配方[/yellow]")
                    continue

                name = self.recipe_manager.get_item_name(item_id)

                for idx, recipe in enumerate(recipes, 1):
                    table = Table(
                        title=f"[yellow]配方 {idx}/{len(recipes)}[/yellow]",
                        show_header=True,
                        header_style="bold green",
                    )
                    table.add_column("材料", style="green")
                    table.add_column("数量", style="yellow", justify="right")

                    for ing_id, ing_count in recipe.ingredients.items():
                        ing_name = self.recipe_manager.get_item_name(ing_id)
                        table.add_row(ing_name, str(ing_count))

                    table.add_section()
                    table.add_row(
                        f"[magenta]→ {name}[/magenta]",
                        f"[magenta]{recipe.result}[/magenta]",
                    )

                    recipe_panel = Panel(
                        table,
                        title=f"[bold cyan]📋 「{name}」的配方[/bold cyan]",
                        border_style="cyan",
                        padding=(1, 2),
                    )
                    rprint()
                    rprint(recipe_panel)

                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")
            except RecipeLoadError as e:
                rprint(f"[red]错误: {e}[/red]")

    def _recipe_list_by_mod(self):
        rprint("\n[cyan]🏷️ 按模组查看配方[/cyan]\n")

        mods = self.recipe_manager.list_loaded_mods()

        if mods:
            mod_table = Table(show_header=True, header_style="bold magenta")
            mod_table.add_column("序号", style="cyan", width=6)
            mod_table.add_column("模组ID", style="green")

            for idx, mod_id in enumerate(sorted(mods), 1):
                mod_table.add_row(str(idx), mod_id)

            panel = Panel(
                mod_table,
                title="[magenta]已加载的模组[/magenta]",
                border_style="magenta",
                padding=(1, 2),
            )
            rprint(panel)

            mod_choice = console.input(
                "\n[green]请选择模组序号 (或输入 Q 返回): [/green]"
            ).strip()
            if mod_choice.lower() == "q":
                return

            try:
                mod_idx = int(mod_choice) - 1
                if 0 <= mod_idx < len(mods):
                    mod_id = sorted(mods)[mod_idx]
                    self._show_mod_recipes(mod_id)
                else:
                    rprint("[yellow]无效的序号[/yellow]")
            except ValueError:
                rprint("[yellow]请输入有效的序号[/yellow]")
        else:
            rprint("[yellow]暂无加载的模组[/yellow]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _show_mod_recipes(self, mod_id: str):
        all_items = self.recipe_manager.get_all_items()
        mod_items = []

        for item_id in all_items:
            try:
                item_data = self.data_manager.get_recipe(item_id)
                if item_data.get("_source_mod") == mod_id:
                    mod_items.append(
                        (item_id, self.recipe_manager.get_item_name(item_id))
                    )
            except Exception:
                pass

        if mod_items:
            table = Table(
                title=f"[cyan]{mod_id} 模组的物品[/cyan]",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("物品名称", style="green")
            table.add_column("物品ID", style="white")

            for item_id, name in sorted(mod_items, key=lambda x: x[1]):
                table.add_row(name, item_id)

            panel = Panel(table, border_style="cyan", padding=(1, 2))
            rprint()
            rprint(panel)
        else:
            rprint(f"[yellow]模组 '{mod_id}' 没有物品[/yellow]")

    def _recipe_add(self):
        rprint("\n[cyan]➕ 添加配方[/cyan]")
        rprint("[dim]输入 'Q' 返回[/dim]\n")

        while True:
            item_id = console.input("[green]请输入物品ID (如 my_item): [/green]").strip()
            if item_id.lower() == "q":
                return
            if not item_id:
                rprint("[yellow]物品ID不能为空[/yellow]")
                continue
            break

        while True:
            name = console.input("[green]请输入物品名称 (如 我的物品): [/green]").strip()
            if name.lower() == "q":
                return
            if not name:
                rprint("[yellow]物品名称不能为空[/yellow]")
                continue
            break

        rprint("\n[cyan]请输入材料配方 (格式: item_id:数量)[/cyan]")
        rprint("[dim]输入空行结束配方输入（可为空，表示基础材料）[/dim]\n")

        ingredients = {}
        while True:
            ing_input = console.input("[green]材料 (item_id:数量) 或回车结束: [/green]").strip()
            if not ing_input:
                break
            if ing_input.lower() == "q":
                return

            parts = ing_input.split(":")
            if len(parts) == 2:
                ing_id, ing_count = parts
                try:
                    ing_count = int(ing_count)
                    if ing_count > 0:
                        ingredients[ing_id] = ing_count
                        rprint(f"[green]  ✓ 已添加: {ing_id} × {ing_count}[/green]")
                    else:
                        rprint("[yellow]  ✗ 数量必须为正整数[/yellow]")
                except ValueError:
                    rprint("[yellow]  ✗ 无效的数量格式[/yellow]")
            else:
                rprint("[yellow]  ✗ 格式错误，请使用 item_id:数量 格式[/yellow]")

        if ingredients:
            rprint("\n[cyan]有材料配方，请输入产出数量[/cyan]")
            try:
                result_input = console.input("[green]请输入产出数量 (默认 1): [/green]").strip()
                if result_input.lower() == "q":
                    return
                result = int(result_input) if result_input else 1
            except ValueError:
                result = 1
        else:
            rprint("\n[dim]无材料配方（基础材料），产出数量将设为 0[/dim]")
            result = 0

        try:
            stack_input = console.input("[green]请输入堆叠大小 (默认 64): [/green]").strip()
            if stack_input.lower() == "q":
                return
            stack_size = int(stack_input) if stack_input else 64
        except ValueError:
            stack_size = 64

        try:
            mod_id = console.input("[green]请输入模组ID (默认 vanilla): [/green]").strip() or "vanilla"
            if mod_id.lower() == "q":
                return
        except Exception:
            mod_id = "vanilla"

        try:
            self.data_manager.add_recipe(item_id, name, ingredients if ingredients else None, result, stack_size, mod_id)
            self.recipe_manager.reload()
            rprint(f"\n[green]✓ 成功添加: {name} ({item_id})[/green]")
            if ingredients:
                rprint(f"[dim]  - 产出: {result} 个[/dim]")
                rprint(f"[dim]  - 材料: {', '.join(f'{k}×{v}' for k, v in ingredients.items())}[/dim]")
            else:
                rprint("[dim]  - 基础材料（无配方）[/dim]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")
        except Exception as e:
            rprint(f"[red]未知错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _recipe_update(self):
        rprint("\n[cyan]✏️ 更新配方[/cyan]")
        rprint("[dim]输入 'Q' 返回[/dim]\n")

        while True:
            item_input = console.input("[green]请输入物品名称或ID (输入 Q 返回): [/green]").strip()
            if item_input.lower() == "q":
                return

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")

        current_recipe = None
        try:
            item_data = self.data_manager.get_recipe(item_id)
            if item_data.get("recipes"):
                current_recipe = item_data["recipes"][0]
        except Exception:
            pass

        if current_recipe:
            rprint(f"\n[dim]当前配方:[/dim]")
            rprint(f"[dim]  - 名称: {item_data.get('name', item_id)}[/dim]")
            rprint(f"[dim]  - 产出: {current_recipe.get('result', 1)} 个[/dim]")
            rprint(f"[dim]  - 材料: {', '.join(f'{k}×{v}' for k, v in current_recipe.get('ingredients', {}).items())}[/dim]")

        rprint("\n[cyan]留空表示不修改该项[/cyan]")

        while True:
            new_name = console.input(f"[green]新名称 (当前: {item_data.get('name', '-')}): [/green]").strip()
            if new_name.lower() == "q":
                return
            if new_name:
                break
            new_name = None
            break

        try:
            result_input = console.input("[green]新产出数量: [/green]").strip()
            if result_input.lower() == "q":
                return
            new_result = int(result_input) if result_input else None
        except ValueError:
            new_result = None

        try:
            stack_input = console.input("[green]新堆叠大小: [/green]").strip()
            if stack_input.lower() == "q":
                return
            new_stack = int(stack_input) if stack_input else None
        except ValueError:
            new_stack = None

        rprint("\n[cyan]输入新材料配方[/cyan]")
        rprint("[dim]输入 'clear' 清空配方，留空表示不修改[/dim]")
        new_ingredients = None
        ingredients_input = []
        
        while True:
            ing_input = console.input("[green]材料 (item_id:数量) 或回车结束: [/green]").strip()
            if not ing_input:
                break
            if ing_input.lower() == "q":
                return
            if ing_input.lower() == "clear":
                new_ingredients = {}
                rprint("[green]  ✓ 配方将被清空[/green]")
                break

            parts = ing_input.split(":")
            if len(parts) == 2:
                ing_id, ing_count = parts
                try:
                    ing_count = int(ing_count)
                    if ing_count > 0:
                        ingredients_input.append((ing_id, ing_count))
                        rprint(f"[green]  ✓ 已添加: {ing_id} × {ing_count}[/green]")
                    else:
                        rprint("[yellow]  ✗ 数量必须为正整数[/yellow]")
                except ValueError:
                    rprint("[yellow]  ✗ 无效的数量格式[/yellow]")
            else:
                rprint("[yellow]  ✗ 格式错误，请使用 item_id:数量 格式[/yellow]")
        
        if ingredients_input:
            new_ingredients = {k: v for k, v in ingredients_input}

        try:
            success = self.data_manager.update_recipe(
                item_id, new_name, new_ingredients,
                new_result, new_stack
            )
            if success:
                self.recipe_manager.reload()
                rprint(f"\n[green]✓ 成功更新配方: {item_id}[/green]")
            else:
                rprint(f"[yellow]未找到物品: {item_id}[/yellow]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")
        except Exception as e:
            rprint(f"[red]未知错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _recipe_remove(self):
        rprint("\n[cyan]🗑️ 删除配方[/cyan]")
        rprint("[dim]输入 'Q' 返回[/dim]\n")

        while True:
            item_input = console.input("[green]请输入要删除的物品名称或ID (输入 Q 返回): [/green]").strip()
            if item_input.lower() == "q":
                return

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                name = self.recipe_manager.get_item_name(item_id)

                try:
                    item_data = self.data_manager.get_recipe(item_id)
                    if item_data.get("recipes"):
                        recipe = item_data["recipes"][0]
                        rprint(f"\n[yellow]即将删除配方:[/yellow]")
                        rprint(f"[yellow]  物品: {name} ({item_id})[/yellow]")
                        rprint(f"[yellow]  产出: {recipe.get('result', 1)} 个[/yellow]")
                        rprint(f"[yellow]  材料: {', '.join(f'{k}×{v}' for k, v in recipe.get('ingredients', {}).items())}[/yellow]")
                except Exception:
                    pass

                if Confirm.ask("\n[red]确定要删除这个配方吗？此操作不可撤销！[/red]", default=False):
                    success = self.data_manager.remove_recipe(item_id)
                    if success:
                        self.recipe_manager.reload()
                        rprint(f"\n[green]✓ 已删除配方: {name}[/green]")
                    else:
                        rprint(f"[yellow]未找到物品: {item_id}[/yellow]")
                else:
                    rprint("\n[yellow]操作已取消[/yellow]")

                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _recipe_import(self):
        rprint("\n[cyan]📥 导入配方[/cyan]")
        rprint("[dim]输入 'Q' 返回[/dim]\n")

        while True:
            file_path = console.input("[green]请输入JSON文件路径: [/green]").strip()
            if file_path.lower() == "q":
                return
            if not file_path:
                rprint("[yellow]文件路径不能为空[/yellow]")
                continue
            break

        try:
            mod_id = console.input("[green]请输入模组ID (默认 vanilla): [/green]").strip() or "vanilla"
            if mod_id.lower() == "q":
                return
        except Exception:
            mod_id = "vanilla"

        try:
            count = self.data_manager.import_recipes_from_file(file_path, mod_id)
            self.recipe_manager.reload()
            rprint(f"\n[green]✓ 成功导入 {count} 个配方 (模组: {mod_id})[/green]")
        except FileNotFoundError:
            rprint(f"[red]错误: 文件 '{file_path}' 未找到[/red]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")
        except Exception as e:
            rprint(f"[red]未知错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _inventory_manager(self):
        while True:
            rprint("\n[bold cyan]📦 库存管理[/bold cyan]")
            rprint(
                f"[dim]当前库存状态: {'已启用' if self.use_inventory else '已禁用'}[/dim]\n"
            )

            submenu_table = Table(
                title="", show_header=False, border_style=None, pad_edge=False
            )
            submenu_table.add_column("序号", style="cyan bold", width=6)
            submenu_table.add_column("功能", style="white", width=30)

            submenu_table.add_row("[1]", "➕ 添加物品")
            submenu_table.add_row("[2]", "➖ 移除物品")
            submenu_table.add_row("[3]", "📋 列出库存")
            submenu_table.add_row("[4]", "🗑️ 清空库存")
            submenu_table.add_row("[5]", "🔄 切换库存状态")
            submenu_table.add_row("[Q]", "↩️ 返回主菜单")

            panel = Panel(submenu_table, border_style="cyan", padding=(1, 2))
            rprint(panel)

            choice = (
                console.input("\n[bold cyan]请输入选项: [/bold cyan]").strip().lower()
            )

            if choice == "q":
                return
            elif choice == "1":
                self._inventory_add()
            elif choice == "2":
                self._inventory_remove()
            elif choice == "3":
                self._inventory_list()
            elif choice == "4":
                self._inventory_clear()
            elif choice == "5":
                self._toggle_inventory_status()
            else:
                rprint("[yellow]无效选项[/yellow]")

    def _inventory_add(self):
        rprint("\n[cyan]➕ 添加物品到库存[/cyan]")

        while True:
            item_input = console.input(
                "[green]请输入物品名称或ID (输入 Q 返回): [/green]"
            ).strip()
            if item_input.lower() == "q":
                return

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")

        while True:
            try:
                count_input = console.input("[green]请输入数量: [/green]").strip()
                count = int(count_input)
                if count <= 0:
                    rprint("[yellow]数量必须为正整数[/yellow]")
                    continue
                break
            except ValueError:
                rprint("[red]错误: 数量必须是整数[/red]")

        try:
            self.inventory.add_item(item_id, count)
            resolved_name = self.inventory._resolve_item_name(item_id)
            rprint(f"\n[green]✓ 已添加 {count} 个 {resolved_name}[/green]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")

    def _inventory_remove(self):
        rprint("\n[cyan]➖ 从库存移除物品[/cyan]")

        while True:
            item_input = console.input(
                "[green]请输入物品名称或ID (输入 Q 返回): [/green]"
            ).strip()
            if item_input.lower() == "q":
                return

            try:
                item_id = self.recipe_manager.get_item_id(item_input)
                break
            except ItemNotFoundError:
                rprint(f"[red]错误: 找不到物品 '{item_input}'[/red]")

        while True:
            try:
                count_input = console.input("[green]请输入数量: [/green]").strip()
                count = int(count_input)
                if count <= 0:
                    rprint("[yellow]数量必须为正整数[/yellow]")
                    continue
                break
            except ValueError:
                rprint("[red]错误: 数量必须是整数[/red]")

        try:
            success = self.inventory.remove_item(item_id, count)
            resolved_name = self.inventory._resolve_item_name(item_id)
            if success:
                rprint(f"\n[green]✓ 已移除 {count} 个 {resolved_name}[/green]")
            else:
                rprint("[yellow]无法移除: 物品不存在或数量不足[/yellow]")
        except InvalidInputError as e:
            rprint(f"[red]错误: {e}[/red]")

    def _inventory_list(self):
        rprint("\n[cyan]📋 当前库存[/cyan]\n")
        items = self.inventory.list_items()
        if items:
            OutputFormatter.format_inventory(items, self.recipe_manager)
        else:
            rprint("[yellow]库存为空[/yellow]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _inventory_clear(self):
        rprint("\n[cyan]🗑️ 清空库存[/cyan]")

        if Confirm.ask(
            "[red]确定要清空所有库存吗？此操作不可撤销！[/red]", default=False
        ):
            self.inventory.clear()
            rprint("\n[green]✓ 库存已清空[/green]")
        else:
            rprint("\n[yellow]操作已取消[/yellow]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _toggle_inventory_status(self):
        self.use_inventory = not self.use_inventory
        status = "已启用" if self.use_inventory else "已禁用"
        rprint(f"\n[green]✓ 库存使用状态: {status}[/green]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _mod_manager(self):
        while True:
            rprint("\n[bold cyan]🔧 模组管理[/bold cyan]\n")

            mods = self.recipe_manager.list_loaded_mods()

            if mods:
                table = Table(
                    title="[magenta]已加载的模组[/magenta]",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("模组ID", style="green")
                table.add_column("物品数量", style="cyan", justify="right")

                for mod_id in sorted(mods):
                    count = 0
                    all_items = self.recipe_manager.get_all_items()
                    for item_id in all_items:
                        try:
                            item_data = self.data_manager.get_recipe(item_id)
                            if item_data.get("_source_mod") == mod_id:
                                count += 1
                        except Exception:
                            pass
                    table.add_row(mod_id, str(count))

                panel = Panel(table, border_style="magenta", padding=(1, 2))
                rprint(panel)
            else:
                rprint("[yellow]暂无加载的模组[/yellow]")

            rprint()
            submenu_table = Table(
                title="", show_header=False, border_style=None, pad_edge=False
            )
            submenu_table.add_column("序号", style="cyan bold", width=6)
            submenu_table.add_column("功能", style="white", width=30)

            submenu_table.add_row("[1]", "� 浏览模组目录")
            submenu_table.add_row("[2]", "�� 加载模组")
            submenu_table.add_row("[3]", "📤 卸载模组")
            submenu_table.add_row("[Q]", "↩️ 返回主菜单")

            panel2 = Panel(submenu_table, border_style="cyan", padding=(1, 2))
            rprint(panel2)

            choice = (
                console.input("\n[bold cyan]请输入选项: [/bold cyan]").strip().lower()
            )

            if choice == "q":
                return
            elif choice == "1":
                self._mod_browse_dir()
            elif choice == "2":
                self._mod_load()
            elif choice == "3":
                self._mod_unload()
            else:
                rprint("[yellow]无效选项[/yellow]")

    def _mod_browse_dir(self):
        rprint("\n[cyan]📂 模组目录[/cyan]\n")
        
        import os
        from rich.text import Text
        
        mods_dir = self.data_manager._config_manager.get_mod_recipes_dir()
        
        title_text = Text()
        title_text.append("📂 模组目录\n", style="bold cyan")
        title_text.append(f"目录: {mods_dir}", style="dim")
        
        panel = Panel(title_text, border_style="cyan", padding=(1, 2))
        rprint(panel)
        rprint()
        
        available_mods = []
        if os.path.exists(mods_dir):
            for filename in os.listdir(mods_dir):
                if filename.endswith('.json'):
                    mod_id = filename[:-5]
                    available_mods.append(mod_id)
        
        enabled_mods = self.data_manager._config_manager.get_enabled_mods()
        
        loaded_mods = [mod for mod in available_mods if mod in enabled_mods]
        unloaded_mods = [mod for mod in available_mods if mod not in enabled_mods]
        
        if loaded_mods:
            table = Table(
                title="[green]✓ 已加载的模组[/green]",
                show_header=True,
                header_style="bold green"
            )
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
            table = Table(
                title="[dim]○ 可加载的模组[/dim]",
                show_header=True,
                header_style="bold white"
            )
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
        
        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _mod_load(self):
        rprint("\n[cyan]📥 加载模组[/cyan]")

        mod_id = console.input("[green]请输入模组ID (输入 Q 返回): [/green]").strip()
        if mod_id.lower() == "q":
            return

        if not mod_id:
            rprint("[yellow]请输入模组ID[/yellow]")
            return

        try:
            success = self.recipe_manager.enable_mod(mod_id)
            if success:
                rprint(f"\n[green]✓ 模组 '{mod_id}' 加载成功[/green]")
                rprint("[dim]现在可以使用该模组的所有物品和配方了[/dim]")
            else:
                rprint(f"[yellow]模组 '{mod_id}' 未找到或已加载[/yellow]")
        except RecipeLoadError as e:
            rprint(f"[red]错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")

    def _mod_unload(self):
        rprint("\n[cyan]📤 卸载模组[/cyan]")

        mods = self.recipe_manager.list_loaded_mods()
        if not mods:
            rprint("[yellow]没有可卸载的模组[/yellow]")
            Prompt.ask("\n[dim]按 Enter 继续...[/dim]")
            return

        mod_id = console.input(
            "[green]请输入要卸载的模组ID (输入 Q 返回): [/green]"
        ).strip()
        if mod_id.lower() == "q":
            return

        if not mod_id:
            rprint("[yellow]请输入模组ID[/yellow]")
            return

        try:
            self.recipe_manager.disable_mod(mod_id)
            rprint(f"\n[green]✓ 模组 '{mod_id}' 已卸载[/green]")
            rprint("[dim]该模组的物品和配方将不再可用[/dim]")
        except Exception as e:
            rprint(f"[red]错误: {e}[/red]")

        Prompt.ask("\n[dim]按 Enter 继续...[/dim]")
