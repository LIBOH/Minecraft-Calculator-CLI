# Inventory 模块任务列表

## 类定义与初始化

- [ ] `Inventory` 类定义
- [ ] 初始化方法实现（支持自定义文件路径）

## 核心方法

- [ ] `load()` 方法 - 从文件加载库存
- [ ] `save()` 方法 - 保存库存到文件
- [ ] `add_item(item_id: str, count: int)` 方法
- [ ] `remove_item(item_id: str, count: int)` 方法
- [ ] `get_count(item_id: str)` 方法
- [ ] `clear()` 方法
- [ ] `list_items()` 方法

## 参数校验

- [ ] 校验 item_id 非空
- [ ] 校验 count 为正整数

## 异常处理

- [ ] 文件不存在处理（使用空库存）
- [ ] 文件格式错误处理（记录警告）

## 测试用例

- [ ] `test_add_item`
- [ ] `test_remove_item`
- [ ] `test_get_count`
- [ ] `test_clear`