# Minecraft 物品合成材料计算器 - 详细设计文档

## 1. 引言

### 1.1 文档目的
本文档是 Minecraft 物品合成材料计算器的详细设计文档，基于需求文档 [proposal.md](file:///C:/Users/LBH24/Documents/PycharmProjects/Minecraft%20Material%20Calculator/doc/proposal.md) 和概要设计文档 [high-level-design.md](file:///C:/Users/LBH24/Documents/PycharmProjects/Minecraft%20Material%20Calculator/doc/high-level-design.md) 进行设计。本文档详细描述每个模块的实现细节、类结构、方法逻辑、数据结构定义和错误处理机制。

### 1.2 设计原则
- **模块化**: 每个模块职责单一，便于独立测试和维护
- **可扩展**: 支持配方选择策略扩展和模组配方扩展
- **健壮性**: 完善的错误处理和参数验证
- **可读性**: 清晰的代码结构和注释

---

## 2. 目录结构

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

---

## 3. 核心模块详细设计

### 3.1 RecipeManager 模块

#### 3.1.1 类定义

```python
class RecipeManager:
    def __init__(self):
        self._recipes: dict[str, ItemRecipe] = {}
        self._loaded_mods: set[str] = set()
        self._vanilla_loaded: bool = False
        self._data_path: str = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'recipes'
        )
```

#### 3.1.2 方法实现

**load_vanilla_recipes()**
- **功能**: 加载原版配方文件
- **文件路径**: `data/recipes/vanilla.yaml`
- **流程**:
  1. 构建文件路径
  2. 使用 YamlLoader 加载文件
  3. 解析并转换为 ItemRecipe 对象
  4. 合并到 `_recipes` 字典
  5. 设置 `_vanilla_loaded = True`
- **异常处理**:
  - 文件不存在: 记录警告日志，继续执行
  - 文件格式错误: 抛出 `RecipeLoadError`

**load_mod_recipes(mod_id: str) -> bool**
- **功能**: 加载指定模组的配方
- **文件路径**: `data/recipes/mods/{mod_id}.yaml`
- **流程**:
  1. 检查模组是否已加载
  2. 构建文件路径
  3. 验证文件存在性
  4. 使用 YamlLoader 加载文件
  5. 解析并合并到 `_recipes` 字典（模组配方优先级高于原版）
  6. 将模组 ID 添加到 `_loaded_mods`
- **返回值**: `True` 表示加载成功，`False` 表示文件不存在
- **异常处理**:
  - 文件格式错误: 抛出 `RecipeLoadError`
  - 模组已加载: 返回 `True`（幂等性）

**unload_mod_recipes(mod_id: str)**
- **功能**: 卸载指定模组的配方
- **流程**:
  1. 检查模组是否已加载
  2. 重新加载原版配方（清除所有模组配方）
  3. 重新加载除指定模组外的其他已加载模组
- **注意**: 卸载模组后需要重新加载其他模组以保持一致性

**get_recipes(item_id: str) -> list[Recipe]**
- **功能**: 获取物品的所有配方
- **流程**:
  1. 检查 `_recipes` 中是否存在该物品
  2. 若存在，返回 `item_recipes.recipes`
  3. 若不存在，返回空列表
- **返回值**: 配方列表，空列表表示物品无配方

**get_item_name(item_id: str) -> str**
- **功能**: 获取物品的中文名称
- **流程**:
  1. 检查 `_recipes` 中是否存在该物品
  2. 若存在，返回 `item_recipes.name`
  3. 若不存在，返回 `item_id` 作为默认值

**is_loaded(mod_id: str) -> bool**
- **功能**: 检查模组是否已加载
- **返回值**: `True` 表示已加载，`False` 表示未加载

**list_loaded_mods() -> list[str]**
- **功能**: 获取已加载模组列表
- **返回值**: 已加载模组 ID 列表

#### 3.1.3 数据结构

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Recipe:
    ingredients: Dict[str, int]  # 材料 ID 到数量的映射
    result: int = 1              # 产出数量（默认 1）

@dataclass
class ItemRecipe:
    item_id: str
    name: str                    # 中文名称
    recipes: List[Recipe]        # 该物品的所有配方
    source_mod: str = "vanilla"  # 来源模组
```

---

### 3.2 Inventory 模块

#### 3.2.1 类定义

```python
class Inventory:
    def __init__(self, file_path: str = None):
        if file_path is None:
            self._file_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'inventory.yaml'
            )
        else:
            self._file_path = file_path
        self._items: Dict[str, int] = {}
        self.load()
```

#### 3.2.2 方法实现

**load()**
- **功能**: 从文件加载库存数据
- **流程**:
  1. 检查文件是否存在
  2. 若存在，使用 YamlLoader 加载
  3. 解析 `items` 字段到 `_items`
  4. 若不存在，初始化空库存
- **异常处理**:
  - 文件格式错误: 记录警告，使用空库存

**save()**
- **功能**: 保存库存数据到文件
- **流程**:
  1. 构建数据结构 `{"items": self._items, "last_updated": 当前时间}`
  2. 使用 YamlLoader 写入文件
  3. 确保父目录存在

**add_item(item_id: str, count: int)**
- **功能**: 添加物品到库存
- **参数校验**:
  - `item_id` 不能为空
  - `count` 必须为正整数
- **流程**:
  1. 校验参数
  2. 更新 `_items[item_id]`（累加）
  3. 调用 `save()` 持久化

**remove_item(item_id: str, count: int) -> bool**
- **功能**: 从库存移除物品
- **参数校验**:
  - `item_id` 不能为空
  - `count` 必须为正整数
- **流程**:
  1. 校验参数
  2. 检查物品是否存在且数量足够
  3. 若足够，扣除数量；若不足，设置为 0
  4. 调用 `save()` 持久化
- **返回值**: `True` 表示成功，`False` 表示物品不存在或数量不足

**get_count(item_id: str) -> int**
- **功能**: 获取物品数量
- **返回值**: 物品数量，不存在返回 0

**clear()**
- **功能**: 清空库存
- **流程**:
  1. 清空 `_items` 字典
  2. 调用 `save()` 持久化

**list_items() -> Dict[str, int]**
- **功能**: 获取所有库存物品
- **返回值**: 物品 ID 到数量的映射

---

### 3.3 MaterialCalculator 模块

#### 3.3.1 类定义

```python
class MaterialCalculator:
    def __init__(
        self,
        recipe_manager: RecipeManager,
        inventory: Inventory,
        strategy: RecipeSelectionStrategy = None
    ):
        self._recipe_manager = recipe_manager
        self._inventory = inventory
        self._strategy = strategy or FirstRecipeStrategy()
        self._cache: Dict[str, Dict[str, int]] = {}  # 缓存已计算的物品
```

#### 3.3.2 方法实现

**calculate(item_id: str, count: int) -> CalculationResult**
- **功能**: 计算合成指定数量物品所需的材料
- **参数校验**:
  - `item_id` 不能为空
  - `count` 必须为正整数
- **流程**:
  1. 校验参数
  2. 获取物品配方
  3. 使用策略选择最优配方
  4. 调用 `_recursive_calc` 递归计算
  5. 扣除库存
  6. 返回计算结果
- **异常处理**:
  - 物品无配方: 抛出 `ItemNotFoundError`

**_recursive_calc(item_id: str, count: int, visited: set = None) -> CalculationResult**
- **功能**: 内部递归计算方法
- **参数**:
  - `item_id`: 物品 ID
  - `count`: 数量
  - `visited`: 已访问物品集合（防止循环依赖）
- **流程**:
  1. 检查是否已访问（防止无限递归）
  2. 获取物品配方
  3. 选择配方并计算直接材料需求
  4. 对每个材料递归计算
  5. 构建并返回 `CalculationResult`

**_deduct_inventory(result: CalculationResult) -> CalculationResult**
- **功能**: 从计算结果中扣除库存
- **流程**:
  1. 遍历所有直接材料
  2. 获取库存数量
  3. 计算剩余需求（需求 - 库存，最小为 0）
  4. 更新 `remaining` 字段
  5. 递归处理子材料

#### 3.3.3 数据结构

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class CalculationResult:
    item_id: str
    name: str
    count: int
    ingredients: Dict[str, int]   # 直接材料需求
    remaining: Dict[str, int]     # 扣除库存后剩余需求
    children: List['CalculationResult'] = field(default_factory=list)
```

---

### 3.4 RecipeSelectionStrategy 模块

#### 3.4.1 接口定义

```python
from abc import ABC, abstractmethod
from typing import List

class RecipeSelectionStrategy(ABC):
    @abstractmethod
    def select(self, recipes: List[Recipe]) -> Recipe:
        pass
```

#### 3.4.2 实现类

**FirstRecipeStrategy**
- **策略**: 默认选择第一个配方
- **适用场景**: 物品只有一个配方或不需要特殊选择逻辑
- **实现逻辑**:
  ```python
  def select(self, recipes: List[Recipe]) -> Recipe:
      return recipes[0] if recipes else None
  ```

**MinIngredientStrategy**
- **策略**: 选择材料种类最少的配方
- **适用场景**: 希望减少收集的材料种类
- **实现逻辑**:
  1. 遍历所有配方
  2. 计算每个配方的材料种类数
  3. 返回材料种类最少的配方
  4. 若有多个，选择第一个

**MinTotalCountStrategy**
- **策略**: 选择材料总数量最少的配方
- **适用场景**: 希望减少总材料消耗
- **实现逻辑**:
  1. 遍历所有配方
  2. 计算每个配方的材料总数（考虑产出比例）
  3. 返回材料总数最少的配方
  4. 若有多个，选择第一个

---

### 3.5 Utils 工具模块

#### 3.5.1 YamlLoader 模块

**类定义**:

```python
class YamlLoader:
    @staticmethod
    def load(file_path: str) -> dict:
        """加载 YAML 文件"""
        pass
    
    @staticmethod
    def save(file_path: str, data: dict):
        """保存数据到 YAML 文件"""
        pass
```

**方法实现**:

**load(file_path: str) -> dict**
- **功能**: 加载 YAML 文件
- **流程**:
  1. 检查文件路径安全性（防止路径遍历攻击）
  2. 打开并读取文件
  3. 使用 PyYAML 解析
  4. 返回解析结果
- **异常处理**:
  - 文件不存在: 返回空字典
  - 文件格式错误: 抛出 `YamlParseError`

**save(file_path: str, data: dict)**
- **功能**: 保存数据到 YAML 文件
- **流程**:
  1. 确保父目录存在
  2. 使用 PyYAML 序列化数据
  3. 写入文件
- **异常处理**:
  - 权限错误: 抛出 `YamlSaveError`

#### 3.5.2 OutputFormatter 模块

**类定义**:

```python
class OutputFormatter:
    @staticmethod
    def format_stack(count: int) -> str:
        """格式化为堆叠数"""
        pass
    
    @staticmethod
    def format_result(result: CalculationResult, indent: int = 0) -> str:
        """格式化完整计算结果"""
        pass
    
    @staticmethod
    def format_inventory(items: Dict[str, int]) -> str:
        """格式化库存列表"""
        pass
```

**方法实现**:

**format_stack(count: int) -> str**
- **功能**: 按 Minecraft 64格堆叠规则格式化数量
- **输出格式**: `{full_stacks} x 64 + {remainder} ... {remainder}`
- **示例**: `150 = 2 x 64 + 22 ... 22`

**format_result(result: CalculationResult, indent: int = 0) -> str**
- **功能**: 递归格式化计算结果
- **流程**:
  1. 格式化当前物品的材料需求
  2. 递归格式化子材料
  3. 添加适当的缩进

**format_inventory(items: Dict[str, int]) -> str**
- **功能**: 格式化库存列表输出
- **输出格式**: 每行显示一个物品及其数量

---

### 3.6 CLI 模块

#### 3.6.1 命令结构

```bash
mcc <subcommand> [options]
```

#### 3.6.2 子命令实现

**calc 命令**
- **功能**: 计算合成材料
- **命令**: `mcc calc <item_id> <count> [--inventory <file>] [--mods <mod1,mod2>]`
- **参数解析**:
  - `item_id`: 目标物品 ID
  - `count`: 需要的数量
  - `--inventory`: 指定库存文件路径
  - `--mods`: 指定加载的模组（逗号分隔）
- **流程**:
  1. 解析命令行参数
  2. 初始化 RecipeManager 并加载配方
  3. 初始化 Inventory
  4. 创建 MaterialCalculator
  5. 调用 calculate 方法
  6. 使用 OutputFormatter 格式化输出

**inventory 命令**
- **功能**: 库存管理
- **子命令**:
  - `add`: `mcc inventory add <item_id> <count>`
  - `remove`: `mcc inventory remove <item_id> <count>`
  - `list`: `mcc inventory list`
  - `clear`: `mcc inventory clear`
- **流程**:
  1. 解析子命令
  2. 初始化 Inventory
  3. 执行对应的操作
  4. 输出结果

**recipe 命令**
- **功能**: 配方管理
- **子命令**:
  - `list`: `mcc recipe list [--mod <mod_id>]`
  - `show`: `mcc recipe show <item_id>`
- **流程**:
  1. 解析子命令
  2. 初始化 RecipeManager
  3. 执行对应的查询操作
  4. 输出结果

**mod 命令**
- **功能**: 模组管理
- **子命令**:
  - `list`: `mcc mod list`
  - `load`: `mcc mod load <mod_id>`
  - `unload`: `mcc mod unload <mod_id>`
- **流程**:
  1. 解析子命令
  2. 初始化 RecipeManager
  3. 执行对应的模组操作
  4. 输出结果

---

## 4. 错误处理与异常定义

### 4.1 异常类定义

```python
class CalculatorError(Exception):
    """计算器基类异常"""
    pass

class ItemNotFoundError(CalculatorError):
    """物品未找到异常"""
    def __init__(self, item_id: str):
        super().__init__(f"物品 '{item_id}' 未找到")
        self.item_id = item_id

class RecipeLoadError(CalculatorError):
    """配方加载异常"""
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"加载配方文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason

class YamlParseError(CalculatorError):
    """YAML 解析异常"""
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"解析 YAML 文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason

class YamlSaveError(CalculatorError):
    """YAML 保存异常"""
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"保存 YAML 文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason

class InvalidInputError(CalculatorError):
    """无效输入异常"""
    def __init__(self, message: str):
        super().__init__(message)
```

### 4.2 异常处理策略

| 异常类型 | 触发场景 | 处理方式 |
| :--- | :--- | :--- |
| `ItemNotFoundError` | 计算不存在的物品 | 捕获并提示用户 |
| `RecipeLoadError` | 配方文件加载失败 | 记录日志并提示用户 |
| `YamlParseError` | YAML 文件格式错误 | 记录日志并使用默认值 |
| `YamlSaveError` | 保存文件失败 | 记录日志并提示用户 |
| `InvalidInputError` | 用户输入无效 | 提示用户正确的输入格式 |

---

## 5. 测试用例设计

### 5.1 RecipeManager 测试

**test_load_vanilla_recipes**
- **测试目的**: 验证原版配方加载功能
- **测试步骤**:
  1. 创建 RecipeManager 实例
  2. 调用 load_vanilla_recipes()
  3. 验证 `_vanilla_loaded` 为 True
  4. 验证常见物品（如 `redstone_comparator`）存在

**test_load_mod_recipes**
- **测试目的**: 验证模组配方加载功能
- **测试步骤**:
  1. 创建 RecipeManager 实例
  2. 调用 load_mod_recipes("example_mod")
  3. 验证模组已加载
  4. 验证模组物品存在

**test_get_recipes**
- **测试目的**: 验证获取配方功能
- **测试步骤**:
  1. 加载配方
  2. 调用 get_recipes("redstone_comparator")
  3. 验证返回的配方包含正确的材料

**test_get_item_name**
- **测试目的**: 验证获取物品名称功能
- **测试步骤**:
  1. 加载配方
  2. 调用 get_item_name("redstone_comparator")
  3. 验证返回 "红石比较器"

### 5.2 Inventory 测试

**test_add_item**
- **测试目的**: 验证添加物品功能
- **测试步骤**:
  1. 创建 Inventory 实例
  2. 调用 add_item("iron_ingot", 10)
  3. 验证库存中 iron_ingot 数量为 10

**test_remove_item**
- **测试目的**: 验证移除物品功能
- **测试步骤**:
  1. 创建 Inventory 实例
  2. 添加物品后调用 remove_item
  3. 验证数量正确减少

**test_get_count**
- **测试目的**: 验证获取数量功能
- **测试步骤**:
  1. 创建 Inventory 实例
  2. 添加物品
  3. 调用 get_count 验证数量

**test_clear**
- **测试目的**: 验证清空库存功能
- **测试步骤**:
  1. 创建 Inventory 实例
  2. 添加物品后调用 clear()
  3. 验证库存为空

### 5.3 MaterialCalculator 测试

**test_calculate_simple**
- **测试目的**: 验证简单物品计算
- **测试步骤**:
  1. 创建 MaterialCalculator 实例
  2. 调用 calculate("redstone_comparator", 1)
  3. 验证直接材料需求正确

**test_calculate_recursive**
- **测试目的**: 验证递归计算功能
- **测试步骤**:
  1. 创建 MaterialCalculator 实例
  2. 调用 calculate("redstone_comparator", 1)
  3. 验证子材料（如红石火把）也被计算

**test_calculate_with_inventory**
- **测试目的**: 验证库存扣除功能
- **测试步骤**:
  1. 创建 Inventory 并添加材料
  2. 创建 MaterialCalculator 实例
  3. 调用 calculate
  4. 验证剩余需求正确扣除库存

### 5.4 OutputFormatter 测试

**test_format_stack**
- **测试目的**: 验证堆叠格式化功能
- **测试步骤**:
  1. 调用 format_stack(150)
  2. 验证输出为 "2 x 64 + 22 ... 22"

**test_format_result**
- **测试目的**: 验证结果格式化功能
- **测试步骤**:
  1. 创建 CalculationResult 对象
  2. 调用 format_result
  3. 验证输出格式正确

---

## 6. 数据格式规范

### 6.1 配方文件格式 (YAML)

```yaml
# data/recipes/vanilla.yaml
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
```

### 6.2 模组配方格式

```yaml
# data/recipes/mods/example_mod.yaml
mod_id: example_mod
mod_name: Example Mod
items:
  custom_item:
    name: 自定义物品
    recipes:
      - ingredients:
          iron_ingot: 4
          diamond: 1
        result: 1
```

### 6.3 库存文件格式

```yaml
# data/inventory.yaml
items:
  redstone_comparator: 10
  iron_ingot: 32
  diamond: 5
last_updated: 2024-01-01T12:00:00
```

---

## 7. 安全考虑

### 7.1 路径安全
- 验证文件路径，防止路径遍历攻击
- 使用 `os.path.abspath()` 和 `os.path.normpath()` 规范化路径

### 7.2 输入验证
- 对所有用户输入进行参数校验
- 验证 item_id 格式（仅允许字母、数字、下划线）
- 验证 count 为正整数

### 7.3 文件操作安全
- 使用 try-except 包裹文件操作
- 限制文件大小，防止 DoS 攻击
- 验证文件内容格式

---

## 8. 性能优化

### 8.1 缓存机制
- 使用 `_cache` 字典缓存已计算的物品
- 避免重复计算相同物品

### 8.2 延迟加载
- 模组配方按需加载
- 只有在需要时才加载模组文件

### 8.3 内存优化
- 使用生成器减少内存占用
- 及时清理不再需要的临时数据