from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from datetime import datetime

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    # 获取模板目录绝对路径
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # 配置加载
    app.config.from_object('config.Config')
    
    # 确保必要的目录存在
    for directory in [app.instance_path, app.config['UPLOAD_FOLDER']]:
        try:
            os.makedirs(directory)
        except OSError:
            pass
            
    # 创建上传目录的年月子目录
    current_year = str(datetime.utcnow().year)
    current_month = f"{datetime.utcnow().month:02d}"
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], current_year, current_month)
    try:
        os.makedirs(upload_path)
    except OSError:
        pass
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.bug import bp as bug_bp
    app.register_blueprint(bug_bp)
    
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    from app.project import bp as project_bp
    app.register_blueprint(project_bp)
    
    # 添加自定义过滤器
    def nl2br(value):
        if not value:
            return ""
        return value.replace('\n', '<br>')
    
    app.jinja_env.filters['nl2br'] = nl2br
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app