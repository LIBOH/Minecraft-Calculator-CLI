# Minecraft 物品合成材料计算器 - 需求文档

## 1. 项目概述

### 1.1 项目背景
Minecraft 是一款高度依赖资源收集和合成的沙盒游戏。玩家在游戏中需要计算合成特定物品所需的材料，尤其是在大规模建造或自动化生产时，手动计算复杂配方链非常繁琐且容易出错。

### 1.2 项目目标
开发一个 CLI 应用，帮助玩家：
- 递归计算合成指定数量物品所需的所有原材料
- 考虑库存物品，计算还需获取的材料数量
- 支持多配方选择（如下界合金锭的多种合成方式）
- 兼容原版和模组物品的配方管理

### 1.3 输出格式示例
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

---

## 2. 功能需求

### 2.1 核心功能

| 功能编号 | 功能名称 | 描述 | 优先级 |
| :--- | :--- | :--- | :--- |
| F001 | 递归材料计算 | 根据目标物品数量，递归计算所有层级的原材料需求 | 高 |
| F002 | 库存扣除 | 根据用户输入的库存，计算还需获取的材料数量 | 高 |
| F003 | 多配方支持 | 支持同一物品存在多个合成配方（如下界合金锭） | 高 |
| F004 | 配方分类管理 | 将原版物品和模组物品配方分类存放 | 高 |
| F005 | 堆叠数量输出 | 按 Minecraft 64格堆叠规则输出所需材料的堆叠数 | 高 |

### 2.2 CLI 功能

| 功能编号 | 子命令 | 描述 | 参数 |
| :--- | :--- | :--- | :--- |
| F010 | `calc` | 计算合成材料 | `--item`, `--count`, `--inventory` |
| F011 | `inventory` | 管理库存 | `add`, `remove`, `list`, `clear` |
| F012 | `recipe` | 查看配方 | `list`, `show`, `add`, `remove` |
| F013 | `mod` | 管理模组配方 | `load`, `unload`, `list` |

---

## 3. 数据结构设计

### 3.1 配方数据格式 (YAML)

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

### 3.2 模组配方格式

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

### 3.3 库存数据格式

```yaml
# data/inventory.yaml
items:
  redstone_comparator: 10
  iron_ingot: 32
  diamond: 5
last_updated: 2024-01-01T12:00:00
```

---

## 4. 架构设计

### 4.1 模块结构

```
minecraft_calculator/
├── __init__.py
├── cli.py                 # CLI 入口
├── core/
│   ├── calculator.py      # 材料计算核心逻辑
│   ├── recipe_manager.py  # 配方管理
│   └── inventory.py       # 库存管理
├── data/
│   ├── recipes/
│   │   ├── vanilla.yaml   # 原版配方
│   │   └── mods/          # 模组配方目录
│   └── inventory.yaml     # 库存数据
└── utils/
    ├── yaml_loader.py     # YAML 文件加载
    └── formatter.py       # 输出格式化
```

### 4.2 核心类设计

| 类名 | 职责 | 关键方法 |
| :--- | :--- | :--- |
| `RecipeManager` | 加载和管理配方数据 | `load_recipes()`, `get_recipes(item_id)`, `add_mod_recipes()` |
| `Inventory` | 管理库存数据 | `add_item()`, `remove_item()`, `get_count()`, `save()` |
| `MaterialCalculator` | 递归计算材料需求 | `calculate(item_id, count)`, `_recursive_calc()` |
| `OutputFormatter` | 格式化输出结果 | `format_stack(count)`, `format_result()` |

### 4.3 设计模式

- **策略模式**: 支持不同配方选择策略（如最优材料、最少步骤）
- **工厂模式**: 根据物品类型创建不同的计算器实例
- **单例模式**: 确保全局唯一的配方管理器和库存实例

---

## 5. CLI 接口设计

### 5.1 命令结构

```bash
mcc <subcommand> [options]
```

### 5.2 子命令详解

#### 5.2.1 `calc` - 计算材料

```bash
mcc calc <item_id> <count> [--inventory <file>] [--mods <mod1,mod2>]
```

**参数**:
- `item_id`: 目标物品 ID
- `count`: 需要的数量
- `--inventory`: 指定库存文件路径（默认 `data/inventory.yaml`）
- `--mods`: 指定加载的模组（逗号分隔）

#### 5.2.2 `inventory` - 库存管理

```bash
mcc inventory add <item_id> <count>
mcc inventory remove <item_id> <count>
mcc inventory list
mcc inventory clear
```

#### 5.2.3 `recipe` - 配方管理

```bash
mcc recipe list [--mod <mod_id>]
mcc recipe show <item_id>
mcc recipe add <item_id> <recipe_file>
mcc recipe remove <item_id>
```

#### 5.2.4 `mod` - 模组管理

```bash
mcc mod list
mcc mod load <mod_id>
mcc mod unload <mod_id>
```

---

## 6. 数据流程

### 6.1 材料计算流程

```
用户输入 -> CLI解析 -> RecipeManager加载配方 -> MaterialCalculator递归计算
                                              -> Inventory扣除库存
                                              -> OutputFormatter格式化输出
```

### 6.2 多配方选择流程

```
获取物品配方列表 -> 应用选择策略(默认选择第一个) -> 返回最优配方
```

---

## 7. 扩展性设计

### 7.1 配方扩展

- 支持动态加载模组配方文件
- 支持配方优先级配置
- 支持自定义配方选择策略

### 7.2 数据存储扩展

- 支持多种数据格式（JSON/YAML/TOML）
- 支持远程配方数据加载
- 支持数据库存储（可选）

### 7.3 输出扩展

- 支持多种输出格式（文本/JSON/CSV）
- 支持输出到文件
- 支持可视化输出（如树形结构）

---

## 8. 依赖与环境

### 8.1 Python 依赖

| 依赖 | 版本 | 用途 |
| :--- | :--- | :--- |
| click | ^8.0 | CLI 框架 |
| pyyaml | ^6.0 | YAML 解析 |
| typing-extensions | ^4.0 | 类型提示 |

### 8.2 开发工具

| 工具 | 用途 |
| :--- | :--- |
| pytest | 单元测试 |
| black | 代码格式化 |
| flake8 | 代码检查 |

---

## 9. 安全性考虑

- 配方文件路径验证，防止路径遍历攻击
- 输入参数验证，防止恶意输入
- 敏感数据（如库存）加密存储（可选）
- 模组配方来源验证

---

## 10. 后续开发计划

| 阶段 | 内容 | 时间预估 |
| :--- | :--- | :--- |
| 第一阶段 | 核心计算逻辑 + 原版配方 | 2周 |
| 第二阶段 | CLI 接口 + 库存管理 | 1周 |
| 第三阶段 | 模组支持 + 多配方选择 | 1周 |
| 第四阶段 | 测试与文档完善 | 1周 |