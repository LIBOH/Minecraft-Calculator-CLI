# CLI 模块任务列表

## 命令初始化

- [ ] 初始化 Click 应用
- [ ] 设置命令组结构

## calc 命令

- [ ] `calc` 命令定义
- [ ] 解析 `item_id` 和 `count` 参数
- [ ] `--inventory` 可选参数
- [ ] `--mods` 可选参数（逗号分隔）
- [ ] 调用 MaterialCalculator 计算
- [ ] 使用 OutputFormatter 输出结果

## inventory 命令

- [ ] `inventory` 命令组定义
- [ ] `add` 子命令
- [ ] `remove` 子命令
- [ ] `list` 子命令
- [ ] `clear` 子命令

## recipe 命令

- [ ] `recipe` 命令组定义
- [ ] `list` 子命令（支持 `--mod` 参数）
- [ ] `show` 子命令（显示物品配方）

## mod 命令

- [ ] `mod` 命令组定义
- [ ] `list` 子命令（列出已加载模组）
- [ ] `load` 子命令（加载模组配方）
- [ ] `unload` 子命令（卸载模组配方）

## 异常处理

- [ ] 捕获并处理 `ItemNotFoundError`
- [ ] 捕获并处理 `RecipeLoadError`
- [ ] 捕获并处理 `InvalidInputError`

## 测试用例

- [ ] `test_calc_command`
- [ ] `test_inventory_commands`
- [ ] `test_recipe_commands`
- [ ] `test_mod_commands`