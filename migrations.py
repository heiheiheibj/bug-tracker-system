from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Bug, Attachment

cli = FlaskGroup(create_app=create_app)

@cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库表已创建。')

@cli.command('create-admin')
def create_admin():
    """创建管理员账号"""
    username = input('请输入管理员用户名: ')
    email = input('请输入管理员邮箱: ')
    password = input('请输入管理员密码: ')
    
    if User.query.filter_by(username=username).first():
        print('错误：用户名已存在')
        return
    
    if User.query.filter_by(email=email).first():
        print('错误：邮箱已被注册')
        return
    
    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print('管理员账号已创建')

@cli.command('list-users')
def list_users():
    """列出所有用户"""
    users = User.query.all()
    print('\n当前用户列表:')
    print('ID\t用户名\t邮箱\t\t管理员\t注册时间')
    print('-' * 60)
    for user in users:
        print(f'{user.id}\t{user.username}\t{user.email}\t{"是" if user.is_admin else "否"}\t{user.created_at}')

@cli.command('clean-uploads')
def clean_uploads():
    """清理没有关联的上传文件"""
    import os
    from datetime import datetime, timedelta
    
    # 获取所有附件记录的文件路径
    db_files = set(a.file_path for a in Attachment.query.all())
    
    # 遍历上传目录
    upload_dir = create_app().config['UPLOAD_FOLDER']
    removed = 0
    
    for root, dirs, files in os.walk(upload_dir):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), upload_dir)
            if file_path not in db_files:
                try:
                    os.remove(os.path.join(root, file))
                    removed += 1
                except OSError as e:
                    print(f'删除文件失败 {file}: {e}')
    
    print(f'已清理 {removed} 个未使用的文件')

if __name__ == '__main__':
    cli()