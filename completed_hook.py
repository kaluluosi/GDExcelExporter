
from glob import glob
import os
import textwrap
output_path = CFG['settings']['output']
output_dirname = os.path.basename(output_path)

absouput_path = os.path.abspath(output_path)

settings_file_path = os.path.abspath(f'{output_dirname}/Settings.gd')


lines = []

for full_path in glob(f'{output_path}/**/*.*', recursive=True):
    full_path = os.path.abspath(full_path)
    if full_path == settings_file_path:
        continue

    basename = os.path.basename(full_path)
    setting_name = os.path.split(basename)[0]
    os.path.sep = '/'
    relpath:str = os.path.relpath(full_path, output_path)
    relpath = relpath.replace('\\','/')
    res_path = f'res://{output_dirname}/{relpath}'
    lines.append(f"const var {setting_name} = preload(f'{res_path}')")

# 去掉缩进
code = textwrap.dedent("""
class_name Settings
extends Object

{refs_code}
""")
refs_code = '\n'.join(lines) 

code = code.format(refs_code=refs_code)

with open(f'{output_dirname}/Settings.gd', 'w') as f:
    f.write(code)

