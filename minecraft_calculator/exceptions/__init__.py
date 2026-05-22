class CalculatorError(Exception):
    pass

class ItemNotFoundError(CalculatorError):
    def __init__(self, item_id: str):
        super().__init__(f"物品 '{item_id}' 未找到")
        self.item_id = item_id

class RecipeLoadError(CalculatorError):
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"加载配方文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason

class InvalidInputError(CalculatorError):
    def __init__(self, message: str):
        super().__init__(message)

class JsonParseError(CalculatorError):
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"解析 JSON 文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason

class JsonSaveError(CalculatorError):
    def __init__(self, file_path: str, reason: str):
        super().__init__(f"保存 JSON 文件失败 '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason
