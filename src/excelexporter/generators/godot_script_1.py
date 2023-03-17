from excelexporter.config import Configuration
from excelexporter.sheetdata import SheetData

# 导出格式
extension = "gd"


def generator(sheetdata: SheetData, config: Configuration):
    print(sheetdata)
    return "shit1"


def completed_hook(config: Configuration):
    return "shit2"
