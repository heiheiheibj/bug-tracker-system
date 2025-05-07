from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.auth import bp
from app.models import User
from datetime import datetime
from werkzeug.security import check_password_hash

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bug.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # 基本输入验证
        if not username or not password:
            flash('请输入用户名和密码')
            return redirect(url_for('auth.login'))
        
        # 检查登录尝试次数
        login_attempts = session.get('login_attempts', 0)
        if login_attempts >= 5:
            flash('登录尝试次数过多，请稍后再试')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not check_password_hash(user.password_hash, password):
            session['login_attempts'] = login_attempts + 1
            flash('用户名或密码错误')
            return redirect(url_for('auth.login'))
        
        # 重置登录尝试计数
        session.pop('login_attempts', None)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 安全登录
        login_user(user, remember=True)
        
        # 安全重定向
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('bug.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    # 清理会话数据
    session.clear()
    logout_user()
    flash('您已成功登出')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('bug.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # 输入验证
        if not username or not email or not password:
            flash('请填写所有必填字段')
            return redirect(url_for('auth.register'))
        
        # 用户名和邮箱格式验证
        if len(username) < 4 or len(username) > 20:
            flash('用户名长度需在4-20个字符之间')
            return redirect(url_for('auth.register'))
            
        if '@' not in email or '.' not in email:
            flash('请输入有效的邮箱地址')
            return redirect(url_for('auth.register'))
            
        # 密码强度检查
        if len(password) < 8:
            flash('密码长度至少为8个字符')
            return redirect(url_for('auth.register'))
            
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('该用户名已被使用')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册')
            return redirect(url_for('auth.register'))
        
        try:
            # 创建新用户
            user = User(username=username, email=email)
            user.set_password(password)
            
            # 如果是第一个注册的用户，设置为管理员
            if User.query.count() == 0:
                user.is_admin = True
            
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功，请登录')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后再试')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')