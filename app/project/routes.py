from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Project
from app.project import bp
from app.decorators import active_required, create_project_permission_required
from app.project.forms import ProjectForm

@bp.route('/projects')
@login_required
@active_required
def index():
    # 管理员可以查看所有项目，普通用户只能查看自己创建的项目
    if current_user.is_admin:
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id).all()
    return render_template('project/index.html', projects=projects)

@bp.route('/project/create', methods=['GET', 'POST'])
@login_required
@active_required
@create_project_permission_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            creator_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('项目创建成功', 'success')
        return redirect(url_for('project.index'))
        
    return render_template('project/create.html', form=form)

@bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@active_required
def edit(id):
    project = Project.query.get_or_404(id)
    if project.creator_id != current_user.id and not current_user.is_admin:
        flash('无权编辑此项目', 'error')
        return redirect(url_for('project.index'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        db.session.commit()
        flash('项目更新成功', 'success')
        return redirect(url_for('project.index'))
    elif request.method == 'GET':
        form.name.data = project.name
        form.description.data = project.description
        
    return render_template('project/edit.html', form=form, project=project)

@bp.route('/project/<int:id>/delete', methods=['POST'])
@login_required
@active_required
def delete(id):
    project = Project.query.get_or_404(id)
    if project.creator_id != current_user.id and not current_user.is_admin:
        flash('无权删除此项目', 'error')
        return redirect(url_for('project.index'))
    
    try:
        # 获取关联的bug数量用于提示
        bug_count = len(project.bugs)
        
        # 在事务中执行删除操作
        db.session.delete(project)
        db.session.commit()
        
        # 提供更详细的成功信息
        if bug_count > 0:
            flash(f'项目"{project.name}"及其关联的{bug_count}个缺陷已被删除', 'success')
        else:
            flash(f'项目"{project.name}"已删除', 'success')
            
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        # 提供友好的错误信息
        flash(f'删除项目时发生错误：{str(e)}', 'error')
        
    return redirect(url_for('project.index'))