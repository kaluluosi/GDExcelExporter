
from glob import glob
import os
import textwrap
output_path = CFG['settings']['output']
output_dirname = os.path.basename(output_path)
settings_file_path = 'Settings.gd'


lines = []

for path in glob(f'{output_path}/**/*.*', recursive=True):
    basename = os.path.basename(path)
    setting_name = os.path.splitext(basename)[0]
    path = path.replace("\\","/")
    lines.append(f"const var {setting_name} = preload(f'res://{path}')")

# 去掉缩进
code = textwrap.dedent("""
class_name Settings
extends Object

{refs_code}
""")
refs_code = '\n'.join(lines) 

code = code.format(refs_code=refs_code)

with open(settings_file_path, 'w') as f:
    f.write(code)

