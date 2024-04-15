from gd_excelexporter.generators import gds1
from gd_excelexporter.generators import gds2
from gd_excelexporter.generators import json1
from gd_excelexporter.generators import json2
from gd_excelexporter.generators import resource

builtins = {
    "GDS1.0": gds1.GDS1Generator,
    "GDS2.0": gds2.GDS2Generator,
    "JSON1.0": json1.JSON1Generator,
    "JSON2.0": json2.JSON2Generator,
    "RESOURCE": resource.ResourceGenerator,
}
