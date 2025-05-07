import os
import pathlib

# 确保project目录存在
project_dir = pathlib.Path("app/project")
project_dir.mkdir(exist_ok=True)

# 创建空文件
files = ["__init__.py", "routes.py"]
for file in files:
    file_path = project_dir / file
    if not file_path.exists():
        file_path.touch()