# Minecraft 物品合成材料计算器 - Vibe Coding Prompt

## 项目概述

你正在开发一个 **Minecraft 物品合成材料计算器** CLI 应用，帮助玩家递归计算合成指定数量物品所需的所有原材料。

## 核心功能

1. **递归材料计算** - 根据目标物品数量，递归计算所有层级的原材料需求
2. **库存扣除** - 根据用户输入的库存，计算还需获取的材料数量
3. **多配方支持** - 支持同一物品存在多个合成配方
4. **配方分类管理** - 将原版物品和模组物品配方分类存放
5. **堆叠数量输出** - 按 Minecraft 64格堆叠规则输出所需材料的堆叠数

## 目录结构

```
minecraft_calculator/
├── __init__.py
├── cli.py                    # CLI 入口
├── core/
│   ├── __init__.py
│   ├── recipe_manager.py     # 配方管理
│   ├── inventory.py          # 库存管理
│   ├── calculator.py         # 材料计算
│   └── strategies.py         # 配方选择策略
├── utils/
│   ├── __init__.py
│   ├── yaml_loader.py        # YAML 文件加载
│   └── formatter.py          # 输出格式化
├── data/
│   ├── recipes/
│   │   ├── vanilla.yaml      # 原版配方
│   │   └── mods/             # 模组配方目录
│   └── inventory.yaml        # 库存数据
├── exceptions/
│   └── __init__.py           # 异常定义
└── tests/
    ├── __init__.py
    ├── test_calculator.py
    ├── test_inventory.py
    └── test_recipe_manager.py
```

## 模块实现任务

### 1. Exceptions 模块
- `CalculatorError` - 基类异常
- `ItemNotFoundError` - 物品未找到异常
- `RecipeLoadError` - 配方加载异常
- `YamlParseError` - YAML 解析异常
- `YamlSaveError` - YAML 保存异常
- `InvalidInputError` - 无效输入异常

### 2. YamlLoader 模块
- `load(file_path: str)` - 加载 YAML 文件
- `save(file_path: str, data: dict)` - 保存数据到 YAML 文件
- 路径安全验证（防止路径遍历攻击）

### 3. RecipeManager 模块
- `Recipe` 和 `ItemRecipe` 数据类
- `load_vanilla_recipes()` - 加载原版配方
- `load_mod_recipes(mod_id: str)` - 加载模组配方
- `unload_mod_recipes(mod_id: str)` - 卸载模组配方
- `get_recipes(item_id: str)` - 获取物品配方
- `get_item_name(item_id: str)` - 获取物品中文名称

### 4. Inventory 模块
- `load()` - 从文件加载库存
- `save()` - 保存库存到文件
- `add_item(item_id: str, count: int)` - 添加物品
- `remove_item(item_id: str, count: int)` - 移除物品
- `get_count(item_id: str)` - 获取物品数量
- `clear()` - 清空库存
- `list_items()` - 获取所有库存物品

### 5. Strategies 模块
- `RecipeSelectionStrategy` - 抽象基类
- `FirstRecipeStrategy` - 默认选择第一个配方
- `MinIngredientStrategy` - 选择材料种类最少的配方
- `MinTotalCountStrategy` - 选择材料总数量最少的配方

### 6. MaterialCalculator 模块
- `CalculationResult` 数据类
- `calculate(item_id: str, count: int)` - 计算材料需求
- `_recursive_calc()` - 递归计算内部方法
- `_deduct_inventory()` - 扣除库存内部方法
- 缓存机制实现
- 循环依赖检测

### 7. OutputFormatter 模块
- `format_stack(count: int)` - 按64格堆叠规则格式化
- `format_result(result, indent)` - 递归格式化计算结果
- `format_inventory(items)` - 格式化库存列表

### 8. CLI 模块
- `calc` 命令 - 计算合成材料
- `inventory` 命令组 - 库存管理（add/remove/list/clear）
- `recipe` 命令组 - 配方管理（list/show）
- `mod` 命令组 - 模组管理（list/load/unload）

## 数据文件

### 原版配方文件 (data/recipes/vanilla.yaml)
```yaml
items:
  redstone_comparator:
    name: 红石比较器
    recipes:
      - ingredients:
          quartz: 1
          redstone_torch: 3
          stone: 3
        result: 1
  redstone_torch:
    name: 红石火把
    recipes:
      - ingredients:
          redstone_dust: 1
          stick: 1
        result: 1
  stick:
    name: 木棍
    recipes:
      - ingredients:
          planks: 2
        result: 4
```

### 库存文件 (data/inventory.yaml)
```yaml
items: {}
last_updated: 2024-01-01T12:00:00
```

## 代码质量要求

1. **单元测试** - 每个模块必须有完整的 pytest 单元测试
2. **类型检查** - 通过 mypy 静态类型检测
3. **代码规范** - 通过 ruff 代码检查

## 输出格式示例

```
制作「50」个「红石比较器」需要:
  石英: 50 = 0 x 64 + 50 ... 50
  红石火把: 150 = 2 x 64 + 22 ... 22
  石头: 150 = 2 x 64 + 22 ... 22
-----------------------------------
制作「150」个「红石火把」需要:
  红石粉: 150 = 2 x 64 + 22 ... 22
  木棍: 150 = 2 x 64 + 22 ... 22
-----------------------------------
```

## 执行流程

1. 主Agent初始化，创建整体进度跟踪
2. 依次创建子Agent实现每个模块：
   - Exceptions → YamlLoader → RecipeManager → Inventory → Strategies → MaterialCalculator → OutputFormatter → CLI
3. 每个子Agent完成后返回完成信号
4. 主Agent汇总所有模块，运行测试验证
5. 完成整个项目

## 技术栈

- Python 3.10+
- Click 8.0+ - CLI 框架
- PyYAML 6.0+ - YAML 解析
- pytest - 单元测试
- mypy - 类型检查
- ruff - 代码规范检查

## 注意事项

- 所有代码必须遵循 PEP 8 规范
- 使用 dataclasses 定义数据结构
- 实现完整的异常处理机制
- 添加适当的类型提示
- 代码中禁止添加注释

开始实现！