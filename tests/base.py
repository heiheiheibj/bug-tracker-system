import os
import tempfile
import unittest
import shutil
from datetime import datetime
from app import create_app, db
from app.models import User, Bug, Attachment
from config import Config

class TestConfig(Config):
    """测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # 使用内存数据库
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = tempfile.mkdtemp()  # 使用临时目录存储上传文件

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """测试前设置"""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        # 确保模板路径正确
        self.app.template_folder = os.path.join(os.path.dirname(__file__), '../templates')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 确保每次测试都有干净的数据库
        db.drop_all()
        db.create_all()
        
        # 创建测试用户
        self.create_test_users()

    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # 清理上传的文件
        if os.path.exists(self.app.config['UPLOAD_FOLDER']):
            shutil.rmtree(self.app.config['UPLOAD_FOLDER'])
        
        # 清理上传的测试文件
        if os.path.exists(self.app.config['UPLOAD_FOLDER']):
            for root, dirs, files in os.walk(self.app.config['UPLOAD_FOLDER']):
                for file in files:
                    os.unlink(os.path.join(root, file))
            os.rmdir(self.app.config['UPLOAD_FOLDER'])

    def create_test_users(self):
        """创建测试用户"""
        # 使用时间戳确保email唯一
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 创建管理员用户
        admin = User(
            username=f'admin_{timestamp}',
            email=f'admin_{timestamp}@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 创建普通用户
        user = User(
            username=f'user_{timestamp}',
            email=f'user_{timestamp}@example.com'
        )
        user.set_password('user123')
        db.session.add(user)
        
        db.session.commit()
        
        self.admin = admin
        self.user = user

    def login(self, username, password):
        """登录辅助方法"""
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """注销辅助方法"""
        return self.client.get('/logout', follow_redirects=True)

    def create_bug(self, title, description, priority='中', category='功能', user=None):
        """创建Bug辅助方法"""
        if user is None:
            user = self.user
            
        bug = Bug(
            title=title,
            description=description,
            priority=priority,
            status='待处理',
            category=category,
            creator=user
        )
        db.session.add(bug)
        db.session.commit()
        return bug

    def create_test_file(self, filename='test.txt', content=b'Test file content'):
        """创建测试文件辅助方法"""
        filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath