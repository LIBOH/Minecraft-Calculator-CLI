# Minecraft 材料计算器

一个强大的 Minecraft 物品材料计算器，帮助你计算制作任意物品所需的所有材料，支持库存管理和模组扩展。

## 功能特性

- 🧮 **智能材料计算** - 递归计算制作物品所需的所有基础材料
- 📦 **库存管理** - 记录你现有的物品，自动扣除库存中的材料
- 🧩 **模组支持** - 轻松添加自定义模组配方
- 🌈 **彩色输出** - 美观的彩色终端输出
- 🔄 **多配方选择** - 智能选择最优配方
- 📊 **堆叠显示** - 自动计算材料的堆叠数量

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install minecraft-material-calculator
```

### 从源码安装

```bash
git clone https://github.com/yourusername/minecraft-material-calculator.git
cd minecraft-material-calculator
pip install .
```

## 快速开始

### 计算材料

计算制作 1 个红石比较器所需的材料：

```bash
mcc calc "红石比较器" 1
```

或者使用物品 ID：

```bash
mcc calc redstone_comparator 1
```

### 使用库存

1. 添加物品到库存：

```bash
mcc inventory add "石英" 10
```

2. 查看库存：

```bash
mcc inventory list
```

3. 使用库存计算材料：

```bash
mcc calc "红石比较器" 1 --inventory
```

### 查看配方

查看物品的配方：

```bash
mcc recipe show "红石中继器"
```

查看所有可用物品：

```bash
mcc recipe list
```

### 模组支持

加载自定义模组配方：

```bash
mcc mod load my_mod
```

## 完整命令参考

### `calc` - 计算材料

```bash
mcc calc <物品名称/ID> <数量> [选项]
```

选项：
- `-i, --inventory FILE` - 指定库存文件路径
- `-m, --mods MODS` - 指定加载的模组（逗号分隔）

### `inventory` - 库存管理

```bash
mcc inventory add <物品名称/ID> <数量> [--file FILE]  # 添加物品
mcc inventory remove <物品名称/ID> <数量> [--file FILE]  # 移除物品
mcc inventory list [--file FILE]                        # 查看库存
mcc inventory clear [--file FILE]                       # 清空库存
```

### `recipe` - 配方管理

```bash
mcc recipe list [--mod MOD]  # 列出所有可用物品
mcc recipe show <物品>        # 显示物品配方
```

### `mod` - 模组管理

```bash
mcc mod list              # 列出已加载的模组
mcc mod load <模组ID>    # 加载模组
mcc mod unload <模组ID>  # 卸载模组
```

## 添加自定义配方

在 `data/recipes/` 目录下创建 YAML 文件，格式如下：

```yaml
items:
  my_item:
    name: 我的物品
    stacks: 64
    recipes:
      - ingredients:
          planks: 4
          redstone: 2
        result: 1
```

对于模组配方，将文件放在 `data/recipes/mods/` 目录下。

## 配置

默认配置：
- 库存文件：`data/inventory.yaml`
- 配方目录：`data/recipes/`

## 开发

安装开发依赖：

```bash
pip install -e ".[dev]"
```

运行测试：

```bash
pytest
```

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

感谢 Minecraft 社区的支持！
