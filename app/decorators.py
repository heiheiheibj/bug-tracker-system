from functools import wraps
from flask import abort, flash
from flask_login import current_user

def admin_required(f):
    """要求管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            abort(403)
        if not current_user.is_admin:
            flash('只有管理员可以执行此操作')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def active_required(f):
    """要求用户账户处于启用状态的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            abort(403)
        if not current_user.is_active:
            flash('您的账户已被禁用')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def create_project_permission_required(f):
    """要求用户有创建项目权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            abort(403)
        if not current_user.is_active:
            flash('您的账户已被禁用')
            abort(403)
        if not current_user.is_admin and not current_user.can_create_project:
            flash('您没有创建项目的权限')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def create_bug_permission_required(f):
    """要求用户有创建Bug权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            abort(403)
        if not current_user.is_active:
            flash('您的账户已被禁用')
            abort(403)
        if not current_user.is_admin and not current_user.can_create_bug:
            flash('您没有创建Bug的权限')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def reply_bug_permission_required(f):
    """要求用户有回复Bug权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            abort(403)
        if not current_user.is_active:
            flash('您的账户已被禁用')
            abort(403)
        if not current_user.is_admin and not current_user.can_reply_bug:
            flash('您没有回复Bug的权限')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def creator_or_admin_required(model):
    """要求是创建者或管理员的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录')
                abort(403)
                
            # 获取资源实例
            instance = model.query.get_or_404(kwargs.get('id'))
            
            # 判断是否有 instance.creator_id 属性


            if not hasattr(instance, 'creator_id'):
                if not (current_user.is_admin):
                    flash('只有管理员可以执行此操作')
                    abort(403)                
            else:
                # 检查是否是创建者或管理员
                if not (current_user.id == instance.creator_id or current_user.is_admin):
                    flash('只有创建者或管理员可以执行此操作')
                    abort(403)
            
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator