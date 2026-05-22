# Minecraft 材料计算器 - Vibe Coding Prompt

## 项目概述

你正在开发一个 **Minecraft 物品合成材料计算器 CLI 应用**，帮助玩家递归计算合成指定数量物品所需的所有原材料。

### 核心功能

1. **递归材料计算** - 根据目标物品数量，递归计算所有层级的原材料需求
2. **库存管理** - 库存的增删改查和持久化
3. **多配方支持** - 支持同一物品存在多个合成配方
4. **配方分类管理** - 将原版物品和模组物品配方分类存放
5. **堆叠数量输出** - 按 Minecraft 64格堆叠规则输出所需材料的堆叠数
6. **高性能数据管理** - 内存缓存、事件驱动架构、事务支持
7. **搜索功能** - 快速查找物品

---

## 技术栈

- Python 3.10+
- Click 8.4.0+ - CLI 框架
- orjson/ujson/json - JSON 解析（优先 orjson）
- pytest - 单元测试
- mypy - 类型检查
- ruff - 代码规范检查

---

## 架构设计原则

### 核心设计理念

1. **事件驱动** - 使用发布-订阅模式处理数据变更
2. **单一职责** - 各模块职责清晰，DataManager 处理业务逻辑，JsonManager 专门负责 IO
3. **内存缓存** - 配方和库存数据常驻内存，减少 IO 操作
4. **事务支持** - 批量操作全部成功才保存，失败回滚
5. **自动备份** - 文件保存前自动备份

### 数据格式

- **完全使用 JSON** - 彻底移除 YAML 相关代码和文件
- JSON 文件结构与原 YAML 保持一致

---

## 目录结构

```
minecraft_calculator/
├── __init__.py
├── cli.py                              # CLI 入口（重构版）
├── core/
│   ├── __init__.py
│   ├── event_system.py                 # 新增：事件系统
│   ├── config_manager.py               # 新增：配置管理
│   ├── json_manager.py                 # 新增：JSON 文件管理器
│   ├── data_manager.py                 # 重构：数据管理
│   ├── recipe_manager.py               # 重构：依赖 DataManager
│   ├── inventory.py                    # 重构：依赖 DataManager
│   ├── calculator.py                   # 保持/调整
│   ├── strategies.py                   # 保持
│   ├── search_index.py                 # 保持/调整
│   └── transaction_manager.py          # 保持/调整
├── utils/
│   ├── __init__.py
│   ├── json_loader.py                  # 重构：高性能 JSON 加载器
│   └── formatter.py                    # 保持
├── data/
│   ├── app_config.json                 # 新增：应用配置
│   ├── inventory.json                  # 从 YAML 迁移
│   └── recipes/
│       ├── vanilla.json                # 从 YAML 迁移
│       └── mods/
│           └── create.json             # 从 YAML 迁移
└── exceptions/
    └── __init__.py                     # 重构：移除 YAML 异常，保留 JSON 异常
tests/
├── __init__.py
├── test_event_system.py
├── test_config_manager.py
├── test_json_manager.py
├── test_data_manager.py
├── test_recipe_manager.py
├── test_inventory.py
├── test_calculator.py
├── test_json_loader.py
└── test_formatter.py
```

---

## 实现任务清单

### 阶段一：基础设施模块

#### 1. 异常模块 (exceptions/__init__.py)

**任务**：重构异常类，移除 YAML 相关异常，保留和完善 JSON 相关异常

**需要实现的异常**：
- `CalculatorError` - 基类异常
- `ItemNotFoundError` - 物品未找到异常
- `RecipeLoadError` - 配方加载异常
- `InvalidInputError` - 无效输入异常
- `JsonParseError` - JSON 解析异常
- `JsonSaveError` - JSON 保存异常

**需要删除的**：
- `YamlParseError`
- `YamlSaveError`

#### 2. 事件系统 (core/event_system.py)

**任务**：实现发布-订阅模式的事件系统

**核心组件**：
```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Callable

class EventType(Enum):
    INVENTORY_CHANGED = "inventory_changed"
    RECIPE_ADDED = "recipe_added"
    RECIPE_UPDATED = "recipe_updated"
    RECIPE_REMOVED = "recipe_removed"
    RECIPES_LOADED = "recipes_loaded"
    CONFIG_CHANGED = "config_changed"
    MOD_ENABLED = "mod_enabled"
    MOD_DISABLED = "mod_disabled"
    TRANSACTION_COMMIT = "transaction_commit"
    TRANSACTION_ROLLBACK = "transaction_rollback"

@dataclass
class Event:
    event_type: EventType
    data: Dict[str, Any]
    source: Any

class EventBus:
    def __init__(self)
    def subscribe(self, event_type: EventType, callback: Callable)
    def unsubscribe(self, event_type: EventType, callback: Callable)
    def publish(self, event: Event)
    def publish_simple(self, event_type: EventType, data: Dict, source: Any)

# 全局单例
def get_event_bus() -> EventBus
```

**测试要求**：完整的 pytest 单元测试

#### 3. 配置管理 (core/config_manager.py)

**任务**：实现集中式配置管理

**配置数据结构** (app_config.json)：
```json
{
  "paths": {
    "data_dir": "data",
    "inventory_file": "inventory.json",
    "recipes_dir": "recipes",
    "vanilla_recipes_file": "vanilla.json",
    "mods_recipes_dir": "mods",
    "app_config_file": "app_config.json"
  },
  "backup": {
    "max_backups": 3,
    "enabled": true
  },
  "io": {
    "max_file_size": 10485760,
    "compact_json": true
  },
  "json_loader": {
    "prefer_orjson": true,
    "fallback_to_ujson": true,
    "fallback_to_stdjson": true
  }
}
```

**配置类**：
```python
from dataclasses import dataclass

@dataclass
class PathsConfig:
    data_dir: str
    inventory_file: str
    recipes_dir: str
    vanilla_recipes_file: str
    mods_recipes_dir: str
    app_config_file: str

@dataclass
class BackupConfig:
    max_backups: int
    enabled: bool

@dataclass
class IOConfig:
    max_file_size: int
    compact_json: bool

@dataclass
class JsonLoaderConfig:
    prefer_orjson: bool
    fallback_to_ujson: bool
    fallback_to_stdjson: bool

@dataclass
class AppConfig:
    paths: PathsConfig
    backup: BackupConfig
    io: IOConfig
    json_loader: JsonLoaderConfig
```

**ConfigManager 类**：
```python
class ConfigManager:
    def __init__(self, base_dir: str = None)
    @property
    def config(self) -> AppConfig
    def update_config(self, updates: Dict[str, Any])
    def get_data_path(self, relative_path: str = "") -> str
    def get_inventory_path(self) -> str
    def get_vanilla_recipes_path(self) -> str
    def get_mod_recipes_dir(self) -> str
    def get_mod_recipes_path(self, mod_id: str) -> str

# 全局单例
def get_config_manager() -> ConfigManager
```

**测试要求**：完整的 pytest 单元测试

#### 4. JSON 加载器 (utils/json_loader.py)

**任务**：重构为高性能 JSON 加载器，支持多库自动降级

**核心组件**：
```python
class BackupManager:
    MAX_BACKUPS = 3  # 从配置读取
    @staticmethod
    def backup(file_path: str) -> None

class JsonLoader:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 从配置读取
    @staticmethod
    def _validate_path(file_path: str) -> str
    @staticmethod
    def load(file_path: str) -> Dict[str, Any]
    @staticmethod
    def save(file_path: str, data: Dict[str, Any], compact: bool = False)
```

**关键注意事项**：
- `load()` 方法**不自动创建文件**，文件不存在返回空字典
- `save()` 方法在保存前自动备份
- 优先使用 orjson，降级到 ujson，最后标准 json

**测试要求**：完整的 pytest 单元测试

---

### 阶段二：数据管理层

#### 5. JSON 管理器 (core/json_manager.py)

**任务**：实现专门负责 JSON 文件 IO 和事务管理的模块

**核心功能**：
- 订阅并处理数据变更事件
- 事务支持（快照/回滚）
- 批量保存
- 数据验证

**类结构**：
```python
class JsonManager:
    def __init__(self, config_manager: ConfigManager, json_loader: JsonLoader, event_bus: EventBus)
    
    # 事件处理
    def _subscribe_events(self)
    def _on_inventory_changed(self, event: Event)
    def _on_recipe_added(self, event: Event)
    def _on_recipe_updated(self, event: Event)
    def _on_recipe_removed(self, event: Event)
    
    # 事务支持
    def begin_transaction(self)
    def commit_transaction(self)
    def rollback_transaction(self)
    def _create_snapshot(self) -> Dict
    def _restore_snapshot(self, snapshot: Dict)
    def _apply_change(self, change: Dict)
    
    # 文件操作
    def load_inventory(self) -> Dict[str, int]
    def load_all_recipes(self) -> Dict[str, Dict]
    def _load_inventory(self) -> Dict[str, int]
    def _load_all_recipes(self) -> Dict[str, Dict]
    def _save_inventory(self, inventory: Dict[str, int])
    def _save_recipe(self, recipe: Dict, mod_id: str)
    def _remove_recipe(self, item_id: str, mod_id: str)
    def _save_all_recipes(self, recipes: Dict[str, Dict])
```

**测试要求**：完整的 pytest 单元测试

#### 6. 数据管理器 (core/data_manager.py)

**任务**：实现内存缓存、业务逻辑、事件发布的核心模块

**核心功能**：
- 内存缓存配方和库存数据
- 提供数据操作的业务方法
- 数据变更时发布事件
- 事务支持（使用 JsonManager）
- 搜索索引管理
- **不直接操作文件**

**类结构**：
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

class DataManager:
    def __init__(self, config_manager: ConfigManager = None, 
                 json_manager: JsonManager = None,
                 event_bus: EventBus = None)
    
    # 初始化
    def _load_all(self)
    
    # 事务
    def snapshot(self) -> Dict[str, Any]
    def restore(self, snapshot: Dict[str, Any])
    def transaction(self) -> 'DataManagerTransaction'
    
    # 配方管理
    def get_recipe(self, item_id: str) -> Optional[Dict]
    def get_all_recipes(self) -> List[str]
    def add_recipe(self, item_id: str, name: str, ingredients: Dict, 
                   result: int = 1, stack_size: int = 64, mod_id: str = "vanilla") -> bool
    def update_recipe(self, item_id: str, name: Optional[str] = None, 
                     ingredients: Optional[Dict] = None, 
                     result: Optional[int] = None, 
                     stack_size: Optional[int] = None) -> bool
    def remove_recipe(self, item_id: str) -> bool
    
    # 库存管理
    def get_inventory_item(self, item_id: str) -> int
    def list_inventory(self) -> Dict[str, int]
    def add_item(self, item_id: str, count: int) -> bool
    def remove_item(self, item_id: str, count: int) -> bool
    def set_item(self, item_id: str, count: int) -> bool
    def clear_inventory(self) -> None
    
    # 搜索
    def search(self, query: str) -> List['SearchResult']
    
    # 模组管理
    def get_enabled_mods(self) -> List[str]
    def enable_mod(self, mod_id: str) -> None
    def disable_mod(self, mod_id: str) -> None

@dataclass
class DataManagerTransaction:
    data_manager: DataManager
    def __enter__(self)
    def __exit__(self, exc_type, exc_val, exc_tb)
```

**关键注意事项**：
- `get_inventory_item()` 和 `list_inventory()` 必须返回缓存数据，确保一致性
- 所有数据变更方法都必须发布相应事件

**测试要求**：完整的 pytest 单元测试

#### 7. 搜索索引 (core/search_index.py)

**任务**：确保搜索索引与新架构兼容（可能需要轻微调整）

**测试要求**：确保现有功能正常

---

### 阶段三：业务逻辑层重构

#### 8. 配方管理器 (core/recipe_manager.py)

**任务**：重构为依赖 DataManager，保持现有 API 不变

**核心类**：
```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Recipe:
    ingredients: Dict[str, int]
    result: int = 1

@dataclass
class ItemRecipe:
    item_id: str
    name: str
    recipes: List[Recipe]
    stack_size: int = 64
    source_mod: str = "vanilla"

class RecipeManager:
    def __init__(self, data_manager: DataManager = None)
    def load_vanilla_recipes(self) -> None
    def load_mod_recipes(self, mod_id: str) -> bool
    def unload_mod_recipes(self, mod_id: str) -> None
    def get_recipes(self, item_id: str) -> List[Recipe]
    def get_item_name(self, item_id: str) -> str
    def get_item_id(self, name_or_id: str) -> str
    def get_item_stack_size(self, item_id: str) -> int
    def is_loaded(self, mod_id: str) -> bool
    def list_loaded_mods(self) -> List[str]
    def get_all_items(self) -> List[str]
```

**关键注意事项**：
- 内部实现委托给 DataManager
- 保持现有 API 完全不变，确保向后兼容

**测试要求**：完整的 pytest 单元测试

#### 9. 库存管理 (core/inventory.py)

**任务**：重构为依赖 DataManager，保持现有 API 不变

**核心类**：
```python
class Inventory:
    def __init__(self, file_path: str = None, data_manager: DataManager = None)
    def set_recipe_manager(self, recipe_manager: RecipeManager) -> None
    def load(self) -> None
    def save(self) -> None
    def add_item(self, name_or_id: str, count: int) -> None
    def remove_item(self, name_or_id: str, count: int) -> bool
    def get_count(self, name_or_id: str) -> int
    def get_count_by_id(self, item_id: str) -> int
    def clear(self) -> None
    def list_items(self) -> Dict[str, int]
```

**关键注意事项**：
- 内部实现委托给 DataManager
- 保持现有 API 完全不变，确保向后兼容

**测试要求**：完整的 pytest 单元测试

#### 10. 材料计算器 (core/calculator.py)

**任务**：确保与新架构兼容（可能需要轻微调整）

**测试要求**：确保现有功能正常，完整的 pytest 单元测试

#### 11. 配方选择策略 (core/strategies.py)

**任务**：保持现有实现

**测试要求**：确保现有功能正常

---

### 阶段四：数据迁移和清理

#### 12. 数据文件迁移

**任务**：将 YAML 文件转换为 JSON 格式

**需要迁移的文件**：
- `data/inventory.yaml` → `data/inventory.json`
- `data/recipes/vanilla.yaml` → `data/recipes/vanilla.json`
- `data/recipes/mods/create.yaml` → `data/recipes/mods/create.json`

**关键注意事项**：
- JSON 结构与原 YAML 保持一致
- 创建 `data/app_config.json` 配置文件

#### 13. 清理 YAML 相关代码

**需要删除的文件**：
- `minecraft_calculator/utils/yaml_loader.py`
- `data/inventory.yaml`
- `data/recipes/vanilla.yaml`
- `data/recipes/mods/create.yaml`
- 其他 YAML 相关文件

---

### 阶段五：CLI 重构

#### 14. CLI 入口 (cli.py)

**任务**：重构为使用新架构

**关键注意事项**：
- 初始化一次 DataManager，共享使用
- 保持现有的命令接口完全不变
- 命令包括：
  - `calc` - 计算材料
  - `inventory` - 库存管理（add/remove/list/clear）
  - `recipe` - 配方管理（list/show）
  - `mod` - 模组管理（list/load/unload）
  - `search` - 搜索物品

**测试要求**：确保所有命令正常工作

---

### 阶段六：工具模块和收尾

#### 15. 输出格式化 (utils/formatter.py)

**任务**：保持现有实现

**测试要求**：确保现有功能正常

#### 16. 事务管理器 (core/transaction_manager.py)

**任务**：确保与新架构兼容（可能需要调整或移除，如果 DataManager 已集成事务功能）

---

## 代码质量要求

### 1. 单元测试

- 每个模块必须有完整的 pytest 单元测试
- 测试覆盖率应达到 80% 以上
- 测试文件放在 `tests/` 目录

### 2. 类型检查

- 所有代码必须有完整的类型提示
- 通过 mypy 静态类型检查（无错误）

### 3. 代码规范

- 所有代码必须通过 ruff 代码规范检查
- 遵循 PEP 8 规范
- 代码中**禁止添加注释**（除非特别必要）

### 4. 数据一致性

- DataManager 的 `get_inventory_item()` 和 `list_inventory()` 必须返回缓存数据
- 所有数据变更必须通过事件系统通知 JsonManager
- 事务模式下必须全部成功才保存

---

## 测试验证步骤

1. 运行所有单元测试：`pytest`
2. 运行类型检查：`mypy minecraft_calculator/`
3. 运行代码规范检查：`ruff check minecraft_calculator/`
4. 手动测试 CLI 功能

---

## 关键技术决策回顾

1. **完全使用 JSON** - 彻底移除 YAML
2. **事件驱动架构** - 发布-订阅模式处理数据变更
3. **内存缓存** - 减少 IO 操作
4. **事务支持** - 确保数据一致性
5. **自动备份** - 防止数据丢失
6. **向后兼容** - 保持现有 API 不变

---

## 实施顺序建议

1. 异常模块
2. 事件系统
3. 配置管理
4. JSON 加载器
5. JSON 管理器
6. 数据管理器
7. 搜索索引
8. 配方管理器（重构）
9. 库存管理（重构）
10. 材料计算器（适配）
11. 数据文件迁移
12. 清理 YAML 相关代码
13. CLI 重构
14. 全面测试

---

## 输出格式示例（保持不变）

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

---

开始实现！
