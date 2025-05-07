from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.user import bp
from app.models import User
from app.decorators import admin_required
from werkzeug.security import generate_password_hash

@bp.route('/')
@login_required
@admin_required
def index():
    """用户列表页面"""
    users = User.query.all()
    return render_template('user/index.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """创建新用户"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form
        can_create_project = 'can_create_project' in request.form
        can_create_bug = 'can_create_bug' in request.form
        can_reply_bug = 'can_reply_bug' in request.form
        
        # 输入验证
        if not username or not email or not password:
            flash('请填写所有必填字段')
            return redirect(url_for('user.create'))
        
        # 用户名和邮箱格式验证
        if len(username) < 4 or len(username) > 20:
            flash('用户名长度需在4-20个字符之间')
            return redirect(url_for('user.create'))
            
        if '@' not in email or '.' not in email:
            flash('请输入有效的邮箱地址')
            return redirect(url_for('user.create'))
            
        # 密码强度检查
        if len(password) < 8:
            flash('密码长度至少为8个字符')
            return redirect(url_for('user.create'))
            
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('该用户名已被使用')
            return redirect(url_for('user.create'))
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册')
            return redirect(url_for('user.create'))
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        user.is_admin = is_admin
        user.is_active = is_active
        user.can_create_project = can_create_project
        user.can_create_bug = can_create_bug
        user.can_reply_bug = can_reply_bug
        
        db.session.add(user)
        db.session.commit()
        
        flash('用户创建成功')
        return redirect(url_for('user.index'))
    
    return render_template('user/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """编辑用户"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form
        can_create_project = 'can_create_project' in request.form
        can_create_bug = 'can_create_bug' in request.form
        can_reply_bug = 'can_reply_bug' in request.form
        
        # 输入验证
        if not username or not email:
            flash('请填写所有必填字段')
            return redirect(url_for('user.edit', id=id))
        
        # 用户名和邮箱格式验证
        if len(username) < 4 or len(username) > 20:
            flash('用户名长度需在4-20个字符之间')
            return redirect(url_for('user.edit', id=id))
            
        if '@' not in email or '.' not in email:
            flash('请输入有效的邮箱地址')
            return redirect(url_for('user.edit', id=id))
        
        # 检查用户名和邮箱是否已被其他用户使用
        username_user = User.query.filter_by(username=username).first()
        if username_user and username_user.id != id:
            flash('该用户名已被使用')
            return redirect(url_for('user.edit', id=id))
            
        email_user = User.query.filter_by(email=email).first()
        if email_user and email_user.id != id:
            flash('该邮箱已被注册')
            return redirect(url_for('user.edit', id=id))
        
        # 更新用户信息
        user.username = username
        user.email = email
        if password:
            if len(password) < 8:
                flash('密码长度至少为8个字符')
                return redirect(url_for('user.edit', id=id))
            user.set_password(password)
        
        user.is_admin = is_admin
        user.is_active = is_active
        user.can_create_project = can_create_project
        user.can_create_bug = can_create_bug
        user.can_reply_bug = can_reply_bug
        
        db.session.commit()
        
        flash('用户信息更新成功')
        return redirect(url_for('user.index'))
    
    return render_template('user/edit.html', user=user)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """删除用户"""
    user = User.query.get_or_404(id)
    
    # 不允许删除自己
    if user.id == current_user.id:
        flash('不能删除当前登录的用户')
        return redirect(url_for('user.index'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('用户已删除')
    return redirect(url_for('user.index'))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改自己的密码"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 验证当前密码
        if not current_user.check_password(current_password):
            flash('当前密码不正确')
            return redirect(url_for('user.change_password'))
        
        # 验证新密码
        if len(new_password) < 8:
            flash('新密码长度至少为8个字符')
            return redirect(url_for('user.change_password'))
        
        if new_password != confirm_password:
            flash('两次输入的新密码不一致')
            return redirect(url_for('user.change_password'))
        
        # 更新密码
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('密码修改成功')
        return redirect(url_for('bug.index'))
    
    return render_template('user/change_password.html')