# Minecraft 物品合成材料计算器 - 概要设计文档

## 1. 引言

### 1.1 文档目的
本文档是 Minecraft 物品合成材料计算器的概要设计文档，基于需求文档 [proposal.md](file:///C:/Users/LBH24/Documents/PycharmProjects/Minecraft%20Material%20Calculator/doc/proposal.md) 进行设计。本文档将详细描述系统的架构设计、模块划分、核心类设计、数据流程和接口设计。

### 1.2 设计原则
- **模块化**: 按功能划分独立模块，降低耦合度
- **可扩展**: 支持模组配方扩展和配方选择策略扩展
- **易维护**: 清晰的代码结构和接口定义
- **面向对象**: 使用类封装数据和行为

---

## 2. 系统架构设计

### 2.1 整体架构

```
┌────────────────────────────────────────────────────────────────┐
│                        CLI 层 (cli.py)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  calc    │ │inventory │ │ recipe   │ │   mod    │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼─────────────────┐
│                    业务逻辑层 (core/)                           │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │    RecipeManager     │  │     Inventory        │           │
│  │  (配方加载与管理)       │  │    (库存管理)          │           │
│  └──────────┬───────────┘  └──────────┬───────────┘           │
│             │                         │                        │
│             └──────────┬──────────────┘                        │
│                        ▼                                       │
│  ┌──────────────────────────────────────┐                      │
│  │        MaterialCalculator            │                      │
│  │       (递归材料计算核心)                │                      │
│  └──────────────────┬───────────────────┘                      │
└─────────────────────┼──────────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                     数据层 (data/)                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ recipes/         │  │ inventory.yaml   │                   │
│  │  ├─ vanilla.yaml │  │   (库存持久化)    │                    │
│  │  └─ mods/        │  └──────────────────┘                   │
│  │      └─ *.yaml   │                                         │
│  └──────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块名称 | 职责说明 | 文件路径 |
| :--- | :--- | :--- |
| **CLI 层** | 命令行接口，处理用户输入和输出 | `minecraft_calculator/cli.py` |
| **RecipeManager** | 配方加载、管理和查询 | `minecraft_calculator/core/recipe_manager.py` |
| **Inventory** | 库存数据管理和持久化 | `minecraft_calculator/core/inventory.py` |
| **MaterialCalculator** | 递归计算材料需求 | `minecraft_calculator/core/calculator.py` |
| **OutputFormatter** | 输出格式化 | `minecraft_calculator/utils/formatter.py` |
| **YamlLoader** | YAML 文件加载工具 | `minecraft_calculator/utils/yaml_loader.py` |

### 2.3 模块间关系

| 模块 | 依赖模块 | 说明 |
| :--- | :--- | :--- |
| CLI | RecipeManager, Inventory, MaterialCalculator, OutputFormatter | 调用所有核心模块 |
| MaterialCalculator | RecipeManager, Inventory | 使用配方和库存数据进行计算 |
| RecipeManager | YamlLoader | 加载 YAML 配方文件 |
| Inventory | YamlLoader | 加载和保存库存数据 |
| OutputFormatter | 无 | 纯工具类 |

---

## 3. 核心类设计

### 3.1 RecipeManager 类

**职责**: 管理所有配方数据，支持原版和模组配方的加载与查询

**类结构**:

| 属性 | 类型 | 说明 |
| :--- | :--- | :--- |
| `_recipes` | `dict[str, ItemRecipe]` | 物品配方字典，key 为 item_id |
| `_loaded_mods` | `set[str]` | 已加载的模组 ID 集合 |
| `_vanilla_loaded` | `bool` | 原版配方是否已加载 |

**方法**:

| 方法名 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `__init__()` | 无 | `RecipeManager` | 初始化 |
| `load_vanilla_recipes()` | 无 | `None` | 加载原版配方 |
| `load_mod_recipes(mod_id: str)` | `mod_id`: 模组 ID | `bool` | 加载指定模组配方 |
| `unload_mod_recipes(mod_id: str)` | `mod_id`: 模组 ID | `None` | 卸载指定模组配方 |
| `get_recipes(item_id: str)` | `item_id`: 物品 ID | `list[Recipe]` | 获取物品的所有配方 |
| `get_item_name(item_id: str)` | `item_id`: 物品 ID | `str` | 获取物品中文名 |
| `is_loaded(mod_id: str)` | `mod_id`: 模组 ID | `bool` | 检查模组是否已加载 |
| `list_loaded_mods()` | 无 | `list[str]` | 获取已加载模组列表 |

### 3.2 Inventory 类

**职责**: 管理玩家库存，支持库存的增删改查和持久化

**类结构**:

| 属性 | 类型 | 说明 |
| :--- | :--- | :--- |
| `_items` | `dict[str, int]` | 库存物品字典，key 为 item_id |
| `_file_path` | `str` | 库存文件路径 |

**方法**:

| 方法名 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `__init__(file_path: str)` | `file_path`: 库存文件路径 | `Inventory` | 初始化 |
| `load()` | 无 | `None` | 从文件加载库存 |
| `save()` | 无 | `None` | 保存库存到文件 |
| `add_item(item_id: str, count: int)` | `item_id`: 物品 ID, `count`: 数量 | `None` | 添加物品 |
| `remove_item(item_id: str, count: int)` | `item_id`: 物品 ID, `count`: 数量 | `bool` | 移除物品 |
| `get_count(item_id: str)` | `item_id`: 物品 ID | `int` | 获取物品数量 |
| `clear()` | 无 | `None` | 清空库存 |
| `list_items()` | 无 | `dict[str, int]` | 获取所有库存物品 |

### 3.3 MaterialCalculator 类

**职责**: 递归计算合成指定数量物品所需的材料

**类结构**:

| 属性 | 类型 | 说明 |
| :--- | :--- | :--- |
| `_recipe_manager` | `RecipeManager` | 配方管理器引用 |
| `_inventory` | `Inventory` | 库存引用 |
| `_recipe_strategy` | `RecipeSelectionStrategy` | 配方选择策略 |

**方法**:

| 方法名 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `__init__(recipe_manager, inventory, strategy)` | 三个依赖对象 | `MaterialCalculator` | 初始化 |
| `calculate(item_id: str, count: int)` | `item_id`: 物品 ID, `count`: 数量 | `CalculationResult` | 计算材料需求 |
| `_recursive_calc(item_id, count, visited)` | 内部递归方法 | `dict[str, int]` | 递归计算 |

### 3.4 OutputFormatter 类

**职责**: 格式化计算结果输出

**方法**:

| 方法名 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `format_stack(count: int)` | `count`: 数量 | `str` | 格式化为堆叠数（如 `2 x 64 + 22`） |
| `format_result(result: CalculationResult)` | `result`: 计算结果 | `str` | 格式化完整输出 |

### 3.5 RecipeSelectionStrategy 接口

**职责**: 定义配方选择策略接口

**方法**:

| 方法名 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `select(recipes: list[Recipe])` | `recipes`: 配方列表 | `Recipe` | 选择最优配方 |

**实现类**:
- `FirstRecipeStrategy`: 默认选择第一个配方
- `MinIngredientStrategy`: 选择材料种类最少的配方
- `MinTotalCountStrategy`: 选择材料总数最少的配方

---

## 4. 数据结构设计

### 4.1 Recipe 数据结构

```python
class Recipe:
    ingredients: dict[str, int]  # 材料: 数量
    result: int                   # 产出数量
```

### 4.2 ItemRecipe 数据结构

```python
class ItemRecipe:
    item_id: str
    name: str                     # 中文名称
    recipes: list[Recipe]         # 该物品的所有配方
```

### 4.3 CalculationResult 数据结构

```python
class CalculationResult:
    item_id: str
    name: str
    count: int
    ingredients: dict[str, int]   # 直接材料需求
    remaining: dict[str, int]     # 扣除库存后剩余需求
    children: list[CalculationResult]  # 子材料的计算结果
```

---

## 5. 数据流程

### 5.1 材料计算流程

```
用户输入: item_id, count
         │
         ▼
┌──────────────────────────────┐
│     CLI 解析参数             │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  RecipeManager.get_recipes() │  获取物品配方
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  Strategy.select(recipes)   │  选择配方
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  MaterialCalculator.calculate│  递归计算
│     ├─ 计算直接材料需求        │
│     ├─ Inventory.get_count() │  获取库存
│     ├─ 扣除库存              │
│     └─ 递归计算子材料         │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  OutputFormatter.format()    │  格式化输出
└─────────────┬────────────────┘
              │
              ▼
        输出结果
```

### 5.2 库存管理流程

```
用户命令: inventory add/del/list/clear
           │
           ▼
┌──────────────────────────────┐
│     CLI 解析命令             │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│   Inventory 执行操作         │
│   ├─ add_item()             │
│   ├─ remove_item()          │
│   ├─ list_items()           │
│   └─ clear()                │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│      Inventory.save()       │  持久化到文件
└─────────────┬────────────────┘
              │
              ▼
        返回结果给用户
```

### 5.3 模组加载流程

```
用户命令: mod load <mod_id>
           │
           ▼
┌──────────────────────────────┐
│  RecipeManager.load_mod_     │
│      recipes(mod_id)         │
│   ├─ 检查模组文件是否存在     │
│   ├─ YamlLoader 加载文件     │
│   ├─ 合并到 _recipes        │
│   └─ 添加到 _loaded_mods     │
└─────────────┬────────────────┘
              │
              ▼
        返回加载结果
```

---

## 6. CLI 接口设计

### 6.1 命令结构

```
mcc <subcommand> [options]
```

### 6.2 子命令详解

#### 6.2.1 `calc` - 计算材料

```bash
mcc calc <item_id> <count> [--inventory <file>] [--mods <mod1,mod2>]
```

**参数**:
- `item_id`: 目标物品 ID（必需）
- `count`: 需要的数量（必需，正整数）
- `--inventory`: 指定库存文件路径（可选，默认 `data/inventory.yaml`）
- `--mods`: 指定加载的模组（可选，逗号分隔）

**输出示例**:
```
制作「50」个「红石比较器」需要:
  石英: 50 = 0 x 64 + 50 ... 0
  红石火把: 150 = 2 x 64 + 22 ... 0
  石头: 150 = 2 x 64 + 22 ... 0
-----------------------------------
制作「150」个「红石火把」需要:
  红石粉: 150 = 2 x 64 + 22 ... 0
  木棍: 150 = 2 x 64 + 22 ... 0
-----------------------------------
```

#### 6.2.2 `inventory` - 库存管理

```bash
mcc inventory add <item_id> <count>
mcc inventory remove <item_id> <count>
mcc inventory list
mcc inventory clear
```

**子命令**:
- `add`: 添加物品到库存
- `remove`: 从库存移除物品
- `list`: 列出所有库存物品
- `clear`: 清空库存

#### 6.2.3 `recipe` - 配方管理

```bash
mcc recipe list [--mod <mod_id>]
mcc recipe show <item_id>
```

**子命令**:
- `list`: 列出所有物品（可按模组过滤）
- `show`: 显示指定物品的配方

#### 6.2.4 `mod` - 模组管理

```bash
mcc mod list
mcc mod load <mod_id>
mcc mod unload <mod_id>
```

**子命令**:
- `list`: 列出已加载的模组
- `load`: 加载指定模组
- `unload`: 卸载指定模组

---

## 7. 文件目录结构

```
minecraft_calculator/
├── __init__.py
├── cli.py                    # CLI 入口
├── core/
│   ├── __init__.py
│   ├── recipe_manager.py     # 配方管理
│   ├── inventory.py          # 库存管理
│   └── calculator.py         # 材料计算
├── utils/
│   ├── __init__.py
│   ├── yaml_loader.py        # YAML 加载工具
│   └── formatter.py          # 输出格式化
├── data/
│   ├── recipes/
│   │   ├── vanilla.yaml      # 原版配方
│   │   └── mods/             # 模组配方目录
│   │       └── example_mod.yaml
│   └── inventory.yaml        # 库存数据
└── tests/                    # 测试目录
    ├── __init__.py
    ├── test_calculator.py
    ├── test_inventory.py
    └── test_recipe_manager.py
```

---

## 8. 关键设计决策

### 8.1 配方选择策略

采用策略模式，允许用户选择不同的配方选择策略：
- **默认策略**: 选择第一个配方
- **材料最少策略**: 选择所需材料种类最少的配方
- **数量最少策略**: 选择材料总数量最少的配方

### 8.2 数据持久化

- 配方数据：YAML 格式，按原版/模组分类存放
- 库存数据：YAML 格式，自动持久化到文件

### 8.3 递归计算优化

使用缓存机制避免重复计算同一物品，记录已访问的物品及其计算结果。

---

## 9. 接口契约

### 9.1 RecipeManager 接口

```python
class RecipeManager:
    def load_vanilla_recipes() -> None: ...
    def load_mod_recipes(mod_id: str) -> bool: ...
    def unload_mod_recipes(mod_id: str) -> None: ...
    def get_recipes(item_id: str) -> list[Recipe]: ...
    def get_item_name(item_id: str) -> str: ...
    def is_loaded(mod_id: str) -> bool: ...
    def list_loaded_mods() -> list[str]: ...
```

### 9.2 Inventory 接口

```python
class Inventory:
    def __init__(self, file_path: str) -> None: ...
    def load() -> None: ...
    def save() -> None: ...
    def add_item(item_id: str, count: int) -> None: ...
    def remove_item(item_id: str, count: int) -> bool: ...
    def get_count(item_id: str) -> int: ...
    def clear() -> None: ...
    def list_items() -> dict[str, int]: ...
```

### 9.3 MaterialCalculator 接口

```python
class MaterialCalculator:
    def __init__(
        self,
        recipe_manager: RecipeManager,
        inventory: Inventory,
        strategy: RecipeSelectionStrategy
    ) -> None: ...
    def calculate(item_id: str, count: int) -> CalculationResult: ...
```

---

## 10. 扩展点设计

### 10.1 配方选择策略扩展

通过实现 `RecipeSelectionStrategy` 接口添加新策略：

```python
class CustomStrategy(RecipeSelectionStrategy):
    def select(self, recipes: list[Recipe]) -> Recipe:
        # 自定义选择逻辑
        pass
```

### 10.2 数据格式扩展

通过抽象数据加载接口，支持 JSON/TOML 等其他格式。

### 10.3 模组扩展

只需在 `data/recipes/mods/` 目录下添加新的 YAML 文件即可。