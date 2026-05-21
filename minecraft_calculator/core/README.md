# Minecraft 材料计算器 CLI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/包管理-uv-orange.svg" alt="Package Manager">
</p>

一款强大的 Minecraft 材质计算命令行工具，帮助玩家快速计算合成物品所需的材料，支持库存管理、模组扩展和智能配方选择。

---

## 功能特性

### 🎯 核心功能

- **智能材料计算** - 递归计算任意物品的完整材料需求树
- **库存管理** - 管理个人物品库存，自动扣除已有材料
- **多模组支持** - 通过 YAML 文件轻松添加和管理模组配方
- **配方可视化** - 查看任意物品的合成配方详情

### 🧠 智能特性

- **高效配方选择** - 自动选择产出效率最高的配方
- **循环检测** - 智能检测并避免配方循环依赖
- **堆叠显示** - 自动将材料数量转换为堆叠格式 (如 `1 x 64 + 23`)
- **多语言支持** - 支持物品名称和 ID 两种查询方式

### 🎨 用户体验

- **彩色终端输出** - 层次分明的彩色显示
- **中文界面** - 全中文提示信息
- **清晰的错误处理** - 友好的错误提示

---

## 安装

### 前置要求

- Python 3.10 或更高版本
- uv 包管理器

### 使用 uv 安装

```bash
# 克隆项目
git clone https://github.com/LIBOH/Minecraft-Calculaor-CLI.git
cd Minecraft-Calculaor-CLI

# 使用 uv 安装依赖
uv sync

# 安装为命令行工具
uv pip install -e .
```

安装完成后，你可以使用 `mcc` 命令运行工具：

```bash
mcc --help
```

---

## 快速开始

### 计算材料需求

计算制作 10 个红石中继器所需的材料：

```bash
mcc calc redstone_repeater 10
```

使用库存计算（自动扣除已有材料）：

```bash
mcc calc redstone_repeater 10 --inventory
```

### 管理库存

添加物品到库存：

```bash
mcc inventory add redstone 64
mcc inventory add stone 128
```

查看当前库存：

```bash
mcc inventory list
```

移除物品：

```bash
mcc inventory remove redstone 16
```

清空库存：

```bash
mcc inventory clear
```

### 配方查询

列出所有可用物品：

```bash
mcc recipe list
```

查看物品配方：

```bash
mcc recipe show redstone_repeater
```

### 模组管理

加载模组配方：

```bash
mcc mod load create
```

查看已加载的模组：

```bash
mcc mod list
```

卸载模组配方：

```bash
mcc mod unload create
```

---

## 命令参考

### `mcc calc` - 计算材料

| 参数/选项 | 说明 |
|---------|------|
| `name_or_id` | 物品名称或 ID |
| `count` | 需要制作的数量 |
| `-i, --inventory` | 使用默认库存文件 |
| `--inventory-file` | 指定库存文件路径 |
| `-m, --mods` | 指定加载的模组（逗号分隔）|

### `mcc inventory` - 库存管理

| 子命令 | 说明 |
|-------|------|
| `add <物品> <数量>` | 添加物品到库存 |
| `remove <物品> <数量>` | 从库存移除物品 |
| `list` | 列出库存中的所有物品 |
| `clear` | 清空库存 |

### `mcc recipe` - 配方查询

| 子命令 | 说明 |
|-------|------|
| `list [--mod <模组>]` | 列出所有可用物品 |
| `show <物品>` | 显示物品的配方信息 |

### `mcc mod` - 模组管理

| 子命令 | 说明 |
|-------|------|
| `list` | 列出已加载的模组 |
| `load <模组ID>` | 加载模组配方 |
| `unload <模组ID>` | 卸载模组配方 |

---

## 项目结构

```
minecraft_calculator/
├── core/                      # 核心模块
│   ├── calculator.py          # 材料计算引擎
│   ├── inventory.py           # 库存管理
│   ├── recipe_manager.py      # 配方管理器
│   └── strategies.py         # 配方选择策略
├── data/                      # 数据目录
│   ├── recipes/
│   │   ├── vanilla.yaml       # 原版配方
│   │   └── mods/              # 模组配方目录
│   └── inventory.yaml         # 库存数据
├── exceptions/                # 自定义异常
│   └── __init__.py
├── utils/                     # 工具模块
│   ├── formatter.py           # 输出格式化
│   └── yaml_loader.py         # YAML 加载器
└── cli.py                     # 命令行接口
```

---

## 添加自定义配方

配方以 YAML 格式存储在 `data/recipes/` 目录下。

### 原版配方

编辑 `data/recipes/vanilla.yaml`：

```yaml
items:
  custom_item:
    name: 自定义物品
    stacks: 64
    recipes:
      - ingredients:
          diamond: 1
          iron_ingot: 3
        result: 1
```

### 模组配方

在 `data/recipes/mods/` 目录下创建新的 YAML 文件，例如 `mymod.yaml`：

```yaml
items:
  mod_item:
    name: 模组物品
    stacks: 64
    recipes:
      - ingredients:
          iron_ingot: 2
        result: 4
```

然后使用 `mcc mod load mymod` 加载。

---

## 配方选择策略

计算器支持多种配方选择策略：

| 策略 | 说明 |
|------|------|
| **SmartRecipeStrategy** (默认) | 选择产出效率最高的配方 |
| **FirstRecipeStrategy** | 选择第一个配方 |
| **MinIngredientStrategy** | 选择材料数量最少的配方 |
| **MinTotalCountStrategy** | 选择总材料数量最少的配方 |

---

## 开发

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=minecraft_calculator
```

### 代码检查

```bash
# 类型检查
uv run mypy minecraft_calculator

# 代码格式检查
uv run ruff check minecraft_calculator
```

---

## 技术栈

- **click** - 命令行界面框架
- **PyYAML** - YAML 数据解析
- **colorama** - 终端彩色输出
- **pytest** - 单元测试框架

---

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

---

## 贡献

欢迎提交 Issue 和 Pull Request！
