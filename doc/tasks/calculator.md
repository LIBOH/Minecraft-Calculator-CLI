# MaterialCalculator 模块任务列表

## 数据结构定义

- [ ] 定义 `CalculationResult` 数据类

## 类定义与初始化

- [ ] `MaterialCalculator` 类定义
- [ ] 初始化方法（接收 RecipeManager、Inventory、Strategy）
- [ ] 缓存机制实现

## 核心方法

- [ ] `calculate(item_id: str, count: int)` 方法
- [ ] `_recursive_calc(item_id: str, count: int, visited)` 内部方法
- [ ] `_deduct_inventory(result)` 内部方法

## 参数校验

- [ ] 校验 item_id 非空
- [ ] 校验 count 为正整数

## 异常处理

- [ ] 物品无配方时抛出 `ItemNotFoundError`
- [ ] 循环依赖检测（防止无限递归）

## 测试用例

- [ ] `test_calculate_simple` - 简单物品计算
- [ ] `test_calculate_recursive` - 递归计算功能
- [ ] `test_calculate_with_inventory` - 库存扣除功能