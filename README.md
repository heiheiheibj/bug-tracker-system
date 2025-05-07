# Bug管理系统

一个基于Flask和Layui的轻量级Bug管理系统，支持文件附件上传和需求管理功能。

## 功能特点

- 用户认证和权限管理
- Bug提交和跟踪
- 文件附件上传和预览
- 响应式界面设计
- SQLite数据库支持

## 系统要求

- Python 3.8+
- pip包管理器

## 安装步骤

1. 克隆代码库：
```bash
git clone [repository-url]
cd buglist
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
python migrations.py init-db
```

5. 创建管理员账号：
```bash
python migrations.py create-admin
```

## 运行应用

```bash
python run.py
```

访问 http://localhost:5000 即可使用系统。

## 文件上传说明

- 支持的文件类型：
  - 图片：jpg、jpeg、png、webp
  - 文档：doc、docx、pdf、txt
  - 压缩包：zip、rar、7z
  - 其他：html
- 单个文件大小限制：100MB
- 文件存储路径：uploads/YYYY/MM/

## 管理命令

- 初始化数据库：`python migrations.py init-db`
- 创建管理员：`python migrations.py create-admin`
- 查看用户列表：`python migrations.py list-users`
- 清理未使用的上传文件：`python migrations.py clean-uploads`

## 目录结构

```
buglist/
├── app/                    # 应用主目录
│   ├── auth/              # 认证模块
│   ├── bug/               # Bug管理模块
│   ├── errors/            # 错误处理模块
│   └── utils/             # 工具函数
├── instance/              # 实例配置和数据库
├── migrations/            # 数据库迁移文件
├── static/               # 静态文件
├── templates/            # 模板文件
├── uploads/              # 上传文件存储
├── config.py            # 配置文件
├── migrations.py        # 数据库管理命令
├── requirements.txt     # 项目依赖
└── run.py              # 应用入口
```

## 注意事项

1. 首次注册的用户将自动成为管理员
2. 定期清理未使用的上传文件
3. 建议定期备份数据库文件

## 许可证

MIT License