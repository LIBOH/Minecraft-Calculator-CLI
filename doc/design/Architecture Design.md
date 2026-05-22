
# Minecraft Calculator CLI - 架构设计文档

## 1. 概述

本文档描述了 Minecraft Calculator CLI 项目的重构架构设计，重点是实现高性能数据管理、配置解耦和事件驱动架构，彻底从 YAML 迁移到高性能 JSON 架构。

## 2. 设计目标

- **高性能 IO**：使用 JSON（优先 orjson，降级 ujson，最后标准 json）替换 YAML
- **减少 IO 操作**：数据内存缓存，避免频繁读写文件
- **配置解耦**：所有可配置项从代码分离，统一管理
- **事件驱动**：数据变更时通过事件系统通知 JsonManager 进行文件操作
- **单一职责**：DataManager 负责缓存和业务逻辑，JsonManager 专门负责文件 IO
- **事务支持**：批量操作时全部成功才保存，失败则回滚
- **向后兼容**：保持现有 API 基本不变
- **备份机制**：文件保存时自动创建备份

## 3. 技术栈

- **JSON 库**：优先使用 orjson（最快），备选 ujson，降级为 Python 标准 json
- **事件系统**：实现发布-订阅模式（同步处理）
- **数据缓存**：内存中缓存配方和库存数据
- **配置管理**：集中式配置管理
- **事务支持**：快照/恢复机制

## 4. 模块架构

### 4.1 核心模块结构

```
minecraft_calculator/
├── core/
│   ├── __init__.py
│   ├── event_system.py      # 新增：事件系统
│   ├── config_manager.py    # 新增：配置管理
│   ├── json_manager.py      # 新增：JSON 文件管理器（专门负责 IO）
│   ├── data_manager.py      # 新增：数据管理（缓存+业务逻辑）
│   ├── recipe_manager.py    # 重构：依赖 data_manager
│   ├── inventory.py         # 重构：依赖 data_manager
│   ├── calculator.py        # 保持不变或轻微调整
│   └── strategies.py        # 保持不变
├── utils/
│   ├── __init__.py
│   ├── json_loader.py       # 新增：高性能 JSON 加载器
│   └── formatter.py         # 保持不变
├── data/
│   ├── app_config.json      # 新增：应用配置文件
│   ├── inventory.json       # 从 inventory.yaml 迁移
│   └── recipes/
│       ├── vanilla.json     # 从 vanilla.yaml 迁移
│       └── mods/
│           └── create.json  # 从 create.yaml 迁移
└── cli.py                   # 重构：使用新架构
```

## 5. 详细设计

### 5.1 事件系统 (event_system.py)

#### 5.1.1 职责
- 实现发布-订阅模式（同步处理）
- 定义标准事件类型
- 提供全局事件总线

#### 5.1.2 事件类型

```python
class EventType(Enum):
    INVENTORY_CHANGED = "inventory_changed"    # 库存变更
    RECIPE_ADDED = "recipe_added"              # 配方添加
    RECIPE_UPDATED = "recipe_updated"          # 配方更新
    RECIPE_REMOVED = "recipe_removed"          # 配方删除
    RECIPES_LOADED = "recipes_loaded"          # 配方加载完成
    CONFIG_CHANGED = "config_changed"          # 配置变更
    MOD_ENABLED = "mod_enabled"                # 模组启用
    MOD_DISABLED = "mod_disabled"              # 模组禁用
    TRANSACTION_COMMIT = "transaction_commit"  # 事务提交
    TRANSACTION_ROLLBACK = "transaction_rollback" # 事务回滚
```

#### 5.1.3 事件对象

```python
@dataclass
class Event:
    event_type: EventType    # 事件类型
    data: Dict[str, Any]     # 事件数据
    source: Any              # 事件源
```

#### 5.1.4 事件总线

```python
class EventBus:
    def subscribe(self, event_type: EventType, callback: Callable)
    def unsubscribe(self, event_type: EventType, callback: Callable)
    def publish(self, event: Event)  # 同步处理
    def publish_simple(self, event_type: EventType, data: Dict, source: Any)
```

提供全局单例：`get_event_bus()`

### 5.2 配置管理 (config_manager.py)

#### 5.2.1 职责
- 统一管理所有可配置项
- 提供类型安全的配置访问
- 配置变更时发布事件

#### 5.2.2 配置结构 (app_config.json)

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

#### 5.2.3 配置类

```python
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

#### 5.2.4 配置管理器

```python
class ConfigManager:
    def __init__(self, base_dir: str = None)
    @property
    def config(self) -&gt; AppConfig
    def update_config(self, updates: Dict[str, Any])
    def get_data_path(self, relative_path: str = "") -&gt; str
    def get_inventory_path(self) -&gt; str
    def get_vanilla_recipes_path(self) -&gt; str
    def get_mod_recipes_dir(self) -&gt; str
    def get_mod_recipes_path(self, mod_id: str) -&gt; str
```

提供全局单例：`get_config_manager()`

### 5.3 JSON 加载器 (json_loader.py)

#### 5.3.1 职责
- 高性能 JSON 序列化/反序列化
- 支持多种 JSON 库自动降级
- 自动备份机制
- 路径安全验证

#### 5.3.2 JSON 库优先级

1. **orjson**（最快，优先）
   - 极快的序列化/反序列化
   - 原生支持 dataclass
   - 内存效率高
2. **ujson**（备选，次快）
3. **Python 标准 json**（最后降级）

#### 5.3.3 备份管理器

```python
class BackupManager:
    def __init__(self, max_backups: int = 3, enabled: bool = True)
    def backup(self, file_path: str)
```

备份机制：
- 保存前自动创建备份
- 备份目录：`{file_path}.backups/`
- 备份文件命名：`{timestamp}.json`
- 自动清理旧备份，保留 `max_backups` 个

#### 5.3.4 JSON 加载器

```python
class JsonLoader:
    def __init__(self, max_file_size: int = 10*1024*1024, 
                 backup_manager: BackupManager = None)
    def load(self, file_path: str) -&gt; Dict[str, Any]  # 不自动创建文件
    def save(self, file_path: str, data: Dict[str, Any], compact: bool = False)
    def validate_data(self, data: Dict[str, Any], schema: Dict) -&gt; bool
```

注意：
- **不自动创建文件**：文件不存在时提示用户
- **数据验证**：保存前验证数据格式

### 5.4 JSON 管理器 (json_manager.py)

#### 5.4.1 职责
- 专门负责 JSON 文件的增删改查操作
- 订阅数据变更事件，同步文件
- 事务支持：批量操作全部成功才保存，失败回滚
- 数据验证：保存前验证数据完整性

#### 5.4.2 核心设计

```python
class JsonManager:
    def __init__(self, config_manager: ConfigManager, json_loader: JsonLoader, event_bus: EventBus):
        self._config_manager = config_manager
        self._json_loader = json_loader
        self._event_bus = event_bus
        self._pending_changes: List[Dict] = []  # 待保存的变更
        self._in_transaction: bool = False
        self._transaction_snapshot: Optional[Dict] = None
        
        # 订阅事件
        self._subscribe_events()
    
    def _subscribe_events(self):
        """订阅数据变更事件"""
        self._event_bus.subscribe(EventType.INVENTORY_CHANGED, self._on_inventory_changed)
        self._event_bus.subscribe(EventType.RECIPE_ADDED, self._on_recipe_added)
        self._event_bus.subscribe(EventType.RECIPE_UPDATED, self._on_recipe_updated)
        self._event_bus.subscribe(EventType.RECIPE_REMOVED, self._on_recipe_removed)
        self._event_bus.subscribe(EventType.TRANSACTION_COMMIT, self._on_transaction_commit)
        self._event_bus.subscribe(EventType.TRANSACTION_ROLLBACK, self._on_transaction_rollback)
    
    # ========== 事件处理 ==========
    def _on_inventory_changed(self, event: Event):
        """库存变更事件处理"""
        if self._in_transaction:
            self._pending_changes.append({"type": "inventory", "data": event.data})
        else:
            self._save_inventory(event.data["inventory"])
    
    def _on_recipe_added(self, event: Event):
        """配方添加事件处理"""
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_add", "data": event.data})
        else:
            self._save_recipe(event.data["recipe"], event.data["mod_id"])
    
    def _on_recipe_updated(self, event: Event):
        """配方更新事件处理"""
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_update", "data": event.data})
        else:
            self._save_recipe(event.data["recipe"], event.data["mod_id"])
    
    def _on_recipe_removed(self, event: Event):
        """配方删除事件处理"""
        if self._in_transaction:
            self._pending_changes.append({"type": "recipe_remove", "data": event.data})
        else:
            self._remove_recipe(event.data["item_id"], event.data["mod_id"])
    
    # ========== 事务支持 ==========
    def begin_transaction(self):
        """开始事务"""
        self._in_transaction = True
        self._pending_changes = []
        self._transaction_snapshot = self._create_snapshot()
    
    def commit_transaction(self):
        """提交事务：全部成功才保存"""
        try:
            # 应用所有待处理变更
            for change in self._pending_changes:
                self._apply_change(change)
            self._pending_changes = []
            self._in_transaction = False
            self._transaction_snapshot = None
        except Exception as e:
            # 失败回滚
            self.rollback_transaction()
            raise e
    
    def rollback_transaction(self):
        """回滚事务：恢复到快照状态"""
        if self._transaction_snapshot:
            self._restore_snapshot(self._transaction_snapshot)
        self._pending_changes = []
        self._in_transaction = False
        self._transaction_snapshot = None
    
    def _create_snapshot(self) -&gt; Dict:
        """创建当前状态快照"""
        return {
            "inventory": self._load_inventory(),
            "recipes": self._load_all_recipes()
        }
    
    def _restore_snapshot(self, snapshot: Dict):
        """从快照恢复"""
        self._save_inventory(snapshot["inventory"])
        self._save_all_recipes(snapshot["recipes"])
    
    def _apply_change(self, change: Dict):
        """应用单个变更"""
        if change["type"] == "inventory":
            self._save_inventory(change["data"]["inventory"])
        elif change["type"] == "recipe_add":
            self._save_recipe(change["data"]["recipe"], change["data"]["mod_id"])
        elif change["type"] == "recipe_update":
            self._save_recipe(change["data"]["recipe"], change["data"]["mod_id"])
        elif change["type"] == "recipe_remove":
            self._remove_recipe(change["data"]["item_id"], change["data"]["mod_id"])
    
    # ========== 文件操作 ==========
    def load_inventory(self) -&gt; Dict[str, int]:
        """加载库存数据"""
        return self._load_inventory()
    
    def load_all_recipes(self) -&gt; Dict[str, Dict]:
        """加载所有配方"""
        return self._load_all_recipes()
    
    def _load_inventory(self) -&gt; Dict[str, int]:
        """内部加载库存"""
        path = self._config_manager.get_inventory_path()
        try:
            data = self._json_loader.load(path)
            return data.get("items", {})
        except FileNotFoundError:
            raise FileNotFoundError(f"库存文件不存在: {path}")
    
    def _load_all_recipes(self) -&gt; Dict[str, Dict]:
        """内部加载所有配方"""
        recipes = {}
        
        # 加载原版配方
        vanilla_path = self._config_manager.get_vanilla_recipes_path()
        try:
            vanilla_data = self._json_loader.load(vanilla_path)
            if "items" in vanilla_data:
                for item_id, item_data in vanilla_data["items"].items():
                    item_data["_source_mod"] = "vanilla"
                    recipes[item_id] = item_data
        except FileNotFoundError:
            pass
        
        # 加载模组配方
        mods_dir = self._config_manager.get_mod_recipes_dir()
        if os.path.exists(mods_dir):
            for filename in os.listdir(mods_dir):
                if filename.endswith(".json"):
                    mod_id = filename[:-5]
                    mod_path = os.path.join(mods_dir, filename)
                    try:
                        mod_data = self._json_loader.load(mod_path)
                        if "items" in mod_data:
                            for item_id, item_data in mod_data["items"].items():
                                item_data["_source_mod"] = mod_id
                                recipes[item_id] = item_data
                    except FileNotFoundError:
                        pass
        
        return recipes
    
    def _save_inventory(self, inventory: Dict[str, int]):
        """保存库存数据"""
        path = self._config_manager.get_inventory_path()
        if not os.path.exists(path):
            raise FileNotFoundError(f"库存文件不存在，请先创建: {path}")
        
        data = {"items": inventory, "last_updated": datetime.now().isoformat()}
        self._json_loader.save(path, data, compact=self._config_manager.config.io.compact_json)
    
    def _save_recipe(self, recipe: Dict, mod_id: str):
        """保存单个配方"""
        if mod_id == "vanilla":
            path = self._config_manager.get_vanilla_recipes_path()
        else:
            path = self._config_manager.get_mod_recipes_path(mod_id)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"配方文件不存在，请先创建: {path}")
        
        # 加载现有配方
        data = self._json_loader.load(path)
        if "items" not in data:
            data["items"] = {}
        
        # 更新配方
        item_id = recipe["item_id"]
        recipe_copy = copy.deepcopy(recipe)
        recipe_copy.pop("_source_mod", None)
        data["items"][item_id] = recipe_copy
        
        # 保存
        self._json_loader.save(path, data, compact=self._config_manager.config.io.compact_json)
    
    def _remove_recipe(self, item_id: str, mod_id: str):
        """删除单个配方"""
        if mod_id == "vanilla":
            path = self._config_manager.get_vanilla_recipes_path()
        else:
            path = self._config_manager.get_mod_recipes_path(mod_id)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"配方文件不存在: {path}")
        
        # 加载现有配方
        data = self._json_loader.load(path)
        if "items" in data and item_id in data["items"]:
            del data["items"][item_id]
            # 保存
            self._json_loader.save(path, data, compact=self._config_manager.config.io.compact_json)
    
    def _save_all_recipes(self, recipes: Dict[str, Dict]):
        """保存所有配方（按模组分组）"""
        # 按模组分组
        vanilla_recipes = {}
        mod_recipes: Dict[str, Dict] = {}
        
        for item_id, item_data in recipes.items():
            item_data_copy = copy.deepcopy(item_data)
            mod_id = item_data_copy.pop("_source_mod", "vanilla")
            
            if mod_id == "vanilla":
                vanilla_recipes[item_id] = item_data_copy
            else:
                if mod_id not in mod_recipes:
                    mod_recipes[mod_id] = {}
                mod_recipes[mod_id][item_id] = item_data_copy
        
        # 保存原版配方
        if vanilla_recipes:
            vanilla_path = self._config_manager.get_vanilla_recipes_path()
            if not os.path.exists(vanilla_path):
                raise FileNotFoundError(f"原版配方文件不存在: {vanilla_path}")
            self._json_loader.save(vanilla_path, {"items": vanilla_recipes}, 
                                  compact=self._config_manager.config.io.compact_json)
        
        # 保存模组配方
        for mod_id, recipes_data in mod_recipes.items():
            mod_path = self._config_manager.get_mod_recipes_path(mod_id)
            if not os.path.exists(mod_path):
                raise FileNotFoundError(f"模组配方文件不存在: {mod_path}")
            self._json_loader.save(mod_path, {"items": recipes_data}, 
                                  compact=self._config_manager.config.io.compact_json)
```

### 5.5 数据管理 (data_manager.py)

#### 5.5.1 职责
- 集中管理内存数据缓存（配方、库存）
- 提供数据操作的业务逻辑
- 数据变更时发布事件（通知 JsonManager）
- 提供事务支持（快照/恢复）
- 搜索索引功能
- **不直接操作文件**：文件操作委托给 JsonManager

#### 5.5.2 数据结构

```python
class DataManager:
    # 依赖
    _config_manager: ConfigManager
    _json_manager: JsonManager
    _event_bus: EventBus
    
    # 数据缓存
    _recipes: Dict[str, Dict[str, Any]]      # {item_id: item_data}
    _inventory: Dict[str, int]               # {item_id: count}
    _enabled_mods: List[str]                 # 已启用的模组
    
    # 搜索索引
    _search_index: SearchIndex
    
    # 事务状态
    _in_transaction: bool = False
    
    def __init__(self, config_manager: ConfigManager = None, 
                 json_manager: JsonManager = None,
                 event_bus: EventBus = None):
        self._config_manager = config_manager or get_config_manager()
        self._event_bus = event_bus or get_event_bus()
        
        # 创建 JsonManager（如果未提供）
        if json_manager is None:
            json_loader = JsonLoader(max_file_size=self._config_manager.config.io.max_file_size)
            json_manager = JsonManager(self._config_manager, json_loader, self._event_bus)
        self._json_manager = json_manager
        
        # 初始化数据
        self._load_all()
    
    def _load_all(self):
        """初始化加载数据"""
        self._inventory = self._json_manager.load_inventory()
        self._recipes = self._json_manager.load_all_recipes()
        self._search_index.build(self._recipes)
        self._event_bus.publish_simple(EventType.RECIPES_LOADED, {"count": len(self._recipes)}, self)
    
    # ========== 事务支持 ==========
    def snapshot(self) -&gt; Dict[str, Any]:
        """创建快照"""
        return {
            "recipes": copy.deepcopy(self._recipes),
            "inventory": copy.deepcopy(self._inventory)
        }
    
    def restore(self, snapshot: Dict[str, Any]):
        """恢复快照"""
        self._recipes = snapshot.get("recipes", {})
        self._inventory = snapshot.get("inventory", {})
        self._search_index.build(self._recipes)
    
    def transaction(self):
        """开始事务（上下文管理器）"""
        return DataManagerTransaction(self)
    
    # ========== 配方管理 ==========
    def get_recipe(self, item_id: str) -&gt; Optional[Dict]:
        return self._recipes.get(item_id)
    
    def get_all_recipes(self) -&gt; List[str]:
        return list(self._recipes.keys())
    
    def add_recipe(self, item_id: str, name: str, ingredients: Dict, 
                   result: int = 1, stack_size: int = 64, mod_id: str = "vanilla") -&gt; bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if not name:
            raise InvalidInputError("物品名称不能为空")
        
        item_data = {
            "item_id": item_id,
            "name": name,
            "stack": stack_size,
            "recipes": [{"ingredients": ingredients, "result": result}],
            "_source_mod": mod_id,
        }
        
        self._recipes[item_id] = item_data
        self._search_index.build(self._recipes)
        
        # 发布事件（JsonManager 会监听并保存）
        self._event_bus.publish_simple(
            EventType.RECIPE_ADDED,
            {"recipe": item_data, "mod_id": mod_id},
            self
        )
        return True
    
    def update_recipe(self, item_id: str, name: Optional[str] = None, 
                     ingredients: Optional[Dict] = None, 
                     result: Optional[int] = None, 
                     stack_size: Optional[int] = None) -&gt; bool:
        if item_id not in self._recipes:
            return False
        
        if name is not None:
            self._recipes[item_id]["name"] = name
        if ingredients is not None:
            if self._recipes[item_id]["recipes"]:
                self._recipes[item_id]["recipes"][0]["ingredients"] = ingredients
        if result is not None:
            if self._recipes[item_id]["recipes"]:
                self._recipes[item_id]["recipes"][0]["result"] = result
        if stack_size is not None:
            self._recipes[item_id]["stack"] = stack_size
        
        self._search_index.build(self._recipes)
        
        # 发布事件
        mod_id = self._recipes[item_id].get("_source_mod", "vanilla")
        self._event_bus.publish_simple(
            EventType.RECIPE_UPDATED,
            {"recipe": self._recipes[item_id], "mod_id": mod_id},
            self
        )
        return True
    
    def remove_recipe(self, item_id: str) -&gt; bool:
        if item_id in self._recipes:
            mod_id = self._recipes[item_id].get("_source_mod", "vanilla")
            del self._recipes[item_id]
            self._search_index.build(self._recipes)
            
            # 发布事件
            self._event_bus.publish_simple(
                EventType.RECIPE_REMOVED,
                {"item_id": item_id, "mod_id": mod_id},
                self
            )
            return True
        return False
    
    # ========== 库存管理 ==========
    def get_inventory_item(self, item_id: str) -&gt; int:
        return self._inventory.get(item_id, 0)
    
    def list_inventory(self) -&gt; Dict[str, int]:
        return dict(self._inventory)
    
    def add_item(self, item_id: str, count: int) -&gt; bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count &lt;= 0:
            raise InvalidInputError("数量必须为正整数")
        
        if item_id in self._inventory:
            self._inventory[item_id] += count
        else:
            self._inventory[item_id] = count
        
        # 发布事件
        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {"inventory": self._inventory, "action": "add", "item_id": item_id, "count": count},
            self
        )
        return True
    
    def remove_item(self, item_id: str, count: int) -&gt; bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count &lt;= 0:
            raise InvalidInputError("数量必须为正整数")
        
        if item_id not in self._inventory:
            return False
        
        if self._inventory[item_id] &gt;= count:
            self._inventory[item_id] -= count
            if self._inventory[item_id] == 0:
                del self._inventory[item_id]
        else:
            del self._inventory[item_id]
        
        # 发布事件
        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {"inventory": self._inventory, "action": "remove", "item_id": item_id, "count": count},
            self
        )
        return True
    
    def set_item(self, item_id: str, count: int) -&gt; bool:
        if not item_id:
            raise InvalidInputError("物品ID不能为空")
        if count &lt; 0:
            raise InvalidInputError("数量不能为负数")
        
        if count == 0:
            if item_id in self._inventory:
                del self._inventory[item_id]
        else:
            self._inventory[item_id] = count
        
        # 发布事件
        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {"inventory": self._inventory, "action": "set", "item_id": item_id, "count": count},
            self
        )
        return True
    
    def clear_inventory(self) -&gt; None:
        self._inventory.clear()
        
        # 发布事件
        self._event_bus.publish_simple(
            EventType.INVENTORY_CHANGED,
            {"inventory": self._inventory, "action": "clear"},
            self
        )
    
    # ========== 搜索 ==========
    def search(self, query: str) -&gt; List[SearchResult]:
        return self._search_index.search(query)
    
    # ========== 模组管理 ==========
    def get_enabled_mods(self) -&gt; List[str]:
        return self._enabled_mods
    
    def enable_mod(self, mod_id: str) -&gt; None:
        if mod_id not in self._enabled_mods:
            self._enabled_mods.append(mod_id)
            self._event_bus.publish_simple(EventType.MOD_ENABLED, {"mod_id": mod_id}, self)
    
    def disable_mod(self, mod_id: str) -&gt; None:
        if mod_id in self._enabled_mods:
            self._enabled_mods.remove(mod_id)
            self._event_bus.publish_simple(EventType.MOD_DISABLED, {"mod_id": mod_id}, self)


@dataclass
class DataManagerTransaction:
    """事务上下文管理器"""
    data_manager: DataManager
    
    def __enter__(self):
        self.data_manager._json_manager.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.data_manager._json_manager.rollback_transaction()
            return False
        else:
            self.data_manager._json_manager.commit_transaction()
            return True
```

#### 5.5.3 核心数据流

```
初始化:
  1. ConfigManager 加载 app_config.json
  2. DataManager 初始化，创建 JsonManager
  3. JsonManager 从磁盘加载 inventory.json 和所有配方
  4. DataManager 缓存数据，构建搜索索引
  5. 发布 RECIPES_LOADED 事件

数据变更（非事务模式）:
  1. 用户调用 DataManager.add_item() / add_recipe() 等
  2. DataManager 更新内存缓存
  3. DataManager 发布事件（INVENTORY_CHANGED / RECIPE_*）
  4. JsonManager 监听到事件，立即执行对应的文件操作
  5. JsonLoader 处理实际的 JSON 序列化和备份

数据变更（事务模式）:
  1. 使用 with DataManager.transaction(): 开始事务
  2. JsonManager 创建快照，记录 pending_changes（不立即保存）
  3. 执行多个数据操作
  4. 事务结束时：
     a. 成功：JsonManager 应用所有 pending_changes，一次性保存所有变更
     b. 失败：JsonManager 回滚到快照状态，恢复文件
```

### 5.6 重构的模块

#### 5.6.1 recipe_manager.py

保持现有 API，但内部实现改为依赖 DataManager：

```python
class RecipeManager:
    def __init__(self, data_manager: DataManager = None)
    # 现有方法保持不变，内部委托给 data_manager
```

#### 5.6.2 inventory.py

保持现有 API，但内部实现改为依赖 DataManager：

```python
class Inventory:
    def __init__(self, file_path: str = None, data_manager: DataManager = None)
    # 现有方法保持不变，内部委托给 data_manager
```

#### 5.6.3 cli.py

重构为使用新架构，减少重复初始化：

```python
# 初始化一次 data_manager，共享使用
data_manager = DataManager()
recipe_manager = RecipeManager(data_manager)
inventory = Inventory(data_manager=data_manager)
```

## 6. 数据文件迁移

### 6.1 彻底删除 YAML

- **删除所有 YAML 文件**：不再保留任何 YAML 格式文件
- **删除 yaml_loader.py**：彻底移除 YAML 相关代码
- **删除异常类**：移除 YamlParseError、YamlSaveError 等

### 6.2 YAML -&gt; JSON 迁移

将以下文件从 YAML 格式迁移到 JSON 格式：

| 原文件 | 新文件 |
|--------|--------|
| data/inventory.yaml | data/inventory.json |
| data/recipes/vanilla.yaml | data/recipes/vanilla.json |
| data/recipes/mods/create.yaml | data/recipes/mods/create.json |

### 6.3 数据格式保持不变

JSON 结构与原 YAML 结构完全一致，确保平滑迁移：

```json
{
  "items": {
    "minecraft:iron_ingot": {
      "name": "铁锭",
      "stack": 64,
      "recipes": [...]
    }
  }
}
```

## 7. 性能优化

### 7.1 IO 优化

- **内存缓存**：配方和库存数据常驻内存
- **按需加载**：模组配方只在启用时加载
- **批量保存**：事务模式下批量操作一次保存
- **减少 IO**：DataManager 不直接操作文件，JsonManager 负责 IO

### 7.2 JSON 性能

使用 orjson 获得最佳性能：
- 序列化速度：约为标准 json 的 10-20 倍
- 反序列化速度：约为标准 json 的 5-10 倍
- 内存占用更低

### 7.3 搜索优化

- 保持搜索索引在内存中
- 数据变更时重建索引（或增量更新）

### 7.4 事件效率

- **同步事件**：避免异步复杂性，保证数据一致性
- **批量处理**：事务模式下收集变更，一次性处理

## 8. 事件流程示例

### 8.1 库存添加物品（非事务模式）

```
1. 用户调用 inventory.add_item("iron_ingot", 10)
2. Inventory 委托给 DataManager.add_item()
3. DataManager:
   a. 更新 _inventory 缓存
   b. 发布 INVENTORY_CHANGED 事件
4. JsonManager 监听到事件：
   a. 调用 _save_inventory()
   b. 通过 JsonLoader 保存到文件
```

### 8.2 库存添加物品（事务模式）

```
1. with data_manager.transaction():
   a. data_manager.add_item("iron_ingot", 10)
   b. data_manager.add_item("gold_ingot", 5)
2. DataManager 在每次操作时发布事件
3. JsonManager 在事务中：
   a. 收集 pending_changes（不立即保存）
   b. 创建快照
4. 事务结束：
   a. 成功：应用所有变更，一次性保存
   b. 失败：回滚到快照
```

### 8.3 添加新配方

```
1. 调用 data_manager.add_recipe(...)
2. DataManager:
   a. 更新 _recipes 缓存
   b. 重建搜索索引
   c. 发布 RECIPE_ADDED 事件
3. JsonManager 监听到事件：
   a. 调用 _save_recipe()
   b. 通过 JsonLoader 保存到对应模组文件
```

## 9. 架构优势分析

### 9.1 耦合度

| 模块 | 耦合对象 | 耦合度 | 评价 |
|------|----------|--------|------|
| DataManager | ConfigManager, EventBus, JsonManager | 低 | 依赖抽象，通过事件解耦 |
| JsonManager | ConfigManager, EventBus, JsonLoader | 低 | 专门负责 IO，单一职责 |
| RecipeManager | DataManager | 极低 | 仅作为适配层 |

### 9.2 可扩展性

- ✅ 易替换持久化方式：只需替换 JsonManager
- ✅ 易添加新数据类型：只需扩展事件和 DataManager
- ✅ 易添加缓存策略：在 DataManager 层实现

### 9.3 可测试性

- ✅ DataManager 可独立测试（Mock JsonManager）
- ✅ JsonManager 可独立测试（Mock 文件系统）
- ✅ 事件系统可独立测试

## 10. 向后兼容性

### 10.1 API 兼容

- 保持 recipe_manager.py 现有 API 不变
- 保持 inventory.py 现有 API 不变
- 保持 cli.py 现有命令接口不变

### 10.2 数据兼容

- 提供 YAML -&gt; JSON 迁移工具（一次性）
- 迁移后彻底删除 YAML 相关代码

## 11. 实施步骤

1. 创建事件系统模块
2. 创建配置管理模块
3. 实现 JsonLoader（带备份，不自动创建文件）
4. 创建 app_config.json
5. 实现 JsonManager（专门负责 IO，事务支持）
6. 实现 DataManager（缓存+业务逻辑，发布事件）
7. 迁移数据文件 (YAML -&gt; JSON)
8. 重构 recipe_manager.py（依赖 DataManager）
9. 重构 inventory.py（依赖 DataManager）
10. 删除 yaml_loader.py 和 YAML 相关异常
11. 重构 cli.py
12. 测试所有功能

## 12. 后续可扩展功能

- 配置热重载
- 数据同步（多实例）
- 远程数据存储
- 性能监控
- 用户自定义事件
- 异步事件处理（可选）

