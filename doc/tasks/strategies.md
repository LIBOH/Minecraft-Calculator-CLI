# Strategies 模块任务列表

## 接口定义

- [ ] 定义 `RecipeSelectionStrategy` 抽象基类
- [ ] 定义 `select()` 抽象方法

## 策略实现

- [ ] `FirstRecipeStrategy` - 默认选择第一个配方
- [ ] `MinIngredientStrategy` - 选择材料种类最少的配方
- [ ] `MinTotalCountStrategy` - 选择材料总数量最少的配方

## 测试用例

- [ ] `test_first_recipe_strategy`
- [ ] `test_min_ingredient_strategy`
- [ ] `test_min_total_count_strategy`