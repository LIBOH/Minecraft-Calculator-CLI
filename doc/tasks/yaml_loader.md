# YamlLoader 模块任务列表

## 类定义

- [ ] `YamlLoader` 类定义（静态方法）

## 核心方法

- [ ] `load(file_path: str)` - 加载 YAML 文件
- [ ] `save(file_path: str, data: dict)` - 保存数据到 YAML 文件

## 安全处理

- [ ] 路径安全验证（防止路径遍历攻击）
- [ ] 文件大小限制
- [ ] 文件内容格式验证

## 异常处理

- [ ] 文件不存在处理（返回空字典）
- [ ] 文件格式错误处理（抛出 `YamlParseError`）
- [ ] 权限错误处理（抛出 `YamlSaveError`）

## 测试用例

- [ ] `test_load_yaml_file`
- [ ] `test_save_yaml_file`
- [ ] `test_path_traversal_security`