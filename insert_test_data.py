from app import create_app, db
from app.models import Project, Bug, User
from datetime import datetime

app = create_app()

with app.app_context():
    # 创建测试用户
    user1 = User(username='testuser1', email='test1@example.com')
    user1.set_password('password')
    db.session.add(user1)
    
    user2 = User(username='testuser2', email='test2@example.com')
    user2.set_password('password')
    db.session.add(user2)
    
    # 创建测试项目
    project1 = Project(
        name='电商平台开发',
        description='开发新一代电商平台',
        creator=user1
    )
    db.session.add(project1)
    
    project2 = Project(
        name='移动App优化',
        description='优化现有移动应用性能',
        creator=user2
    )
    db.session.add(project2)
    
    # 创建测试需求/BUG
    bug1 = Bug(
        title='购物车无法结算',
        description='点击结算按钮无反应',
        priority='高',
        status='待处理',
        type='BUG',
        project=project1,
        creator=user1
    )
    db.session.add(bug1)
    
    requirement1 = Bug(
        title='新增支付方式',
        description='需要添加支付宝支付功能',
        priority='中',
        status='处理中',
        type='REQUIREMENT',
        project=project1,
        creator=user2
    )
    db.session.add(requirement1)
    
    # 提交所有更改
    db.session.commit()
    print('测试数据插入成功')