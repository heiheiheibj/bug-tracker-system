from app import db, login_manager
from app.constants import BugStatus, BUG_STATUS_DISPLAY
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from hashlib import md5

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    can_create_project = db.Column(db.Boolean, default=True)
    can_create_bug = db.Column(db.Boolean, default=True)
    can_reply_bug = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f'<Project {self.name}>'

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), nullable=False)  # 高/中/低
    status = db.Column(db.String(20), nullable=False, default=BugStatus.PENDING.value)  # 使用BugStatus枚举值
    type = db.Column(db.String(20), nullable=False)      # BUG/REQUIREMENT
    category = db.Column(db.String(20), nullable=False, default='功能')  # 功能/界面/性能/兼容性/其他
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('bugs', lazy=True))
    project = db.relationship('Project', backref=db.backref('bugs', lazy=True))

    def __repr__(self):
        return f'<Bug {self.title}>'

class Comment(db.Model):
    """BUG评论/回复模型"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    bug = db.relationship('Bug', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    attachments = db.relationship('Attachment', backref=db.backref('comment', lazy=True), lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Comment {self.id} by {self.author_id}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储的文件名
    file_path = db.Column(db.String(512), nullable=False)  # 文件存储路径
    file_type = db.Column(db.String(50))  # 文件类型
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    upload_time = db.Column(db.DateTime, default=datetime.now)
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    bug = db.relationship('Bug', backref=db.backref('attachments', lazy=True))
    uploader = db.relationship('User', backref=db.backref('uploads', lazy=True))

    @staticmethod
    def generate_stored_filename(filename):
        """生成唯一的存储文件名"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_hash = md5(os.urandom(8)).hexdigest()[:8]
        ext = os.path.splitext(filename)[1]
        return f"{timestamp}_{random_hash}{ext}"

    def get_file_size_display(self):
        """返回人类可读的文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f} TB"

    def is_image(self):
        """检查是否为图片文件"""
        return self.file_type.lower() in {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

    def is_previewable(self):
        """检查文件是否可预览"""
        previewable_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf',
            'text/plain',
            'text/html'
        }
        return self.file_type.lower() in previewable_types

    def __repr__(self):
        return f'<Attachment {self.filename}>'