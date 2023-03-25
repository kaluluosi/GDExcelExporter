
from excelexporter.generators import gds1
from excelexporter.generators import gds2
from excelexporter.generators import json
from excelexporter.generators import json2
from excelexporter.generators import resource

builtins = {
    "GDS1.0": gds1,
    "GDS2.0": gds2,
    "JSON1.0": json,
    "JSON2.0": json2,
    "RESOURCE": resource,
}
