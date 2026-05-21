# RecipeManager 模块任务列表

## 数据结构定义

- [ ] 定义 `Recipe` 数据类
- [ ] 定义 `ItemRecipe` 数据类

## 核心方法

- [ ] 初始化方法实现
- [ ] `load_vanilla_recipes()` 方法
- [ ] `load_mod_recipes(mod_id: str)` 方法
- [ ] `unload_mod_recipes(mod_id: str)` 方法
- [ ] `get_recipes(item_id: str)` 方法
- [ ] `get_item_name(item_id: str)` 方法
- [ ] `is_loaded(mod_id: str)` 方法
- [ ] `list_loaded_mods()` 方法

## 异常处理

- [ ] 处理文件不存在异常
- [ ] 处理文件格式错误异常

## 测试用例

- [ ] `test_load_vanilla_recipes`
- [ ] `test_load_mod_recipes`
- [ ] `test_get_recipes`
- [ ] `test_get_item_name`