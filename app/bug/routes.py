import os
from flask import render_template, redirect, url_for, flash, request, current_app, send_file, abort
from flask_login import login_required, current_user
from app import db
from app.bug import bp
from app.models import Bug, Attachment, Project, Comment
from app.decorators import admin_required, creator_or_admin_required, active_required, reply_bug_permission_required, create_bug_permission_required
from app.utils.file_handler import process_upload, save_file


@bp.route('/')
@bp.route('/index')
@login_required
@active_required
def index():
    page = request.args.get('page', 1, type=int)
    query = Bug.query
    
    # 添加搜索条件
    category = request.args.get('category')
    if category:
        query = query.filter(Bug.category == category)
    
    project_id = request.args.get('project_id')
    if project_id:
        query = query.filter(Bug.project_id == project_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter(Bug.status == status)
    
    # 根据优先级筛选
    priority = request.args.get('priority')
    if priority:
        query = query.filter(Bug.priority == priority)
    
    # 根据创建者筛选
    creator_id = request.args.get('creator_id')
    if creator_id:
        query = query.filter(Bug.creator_id == creator_id)
    
    keyword = request.args.get('keyword')
    if keyword:
        query = query.filter(Bug.title.contains(keyword))
    
    # 管理员可以查看所有项目，普通用户只能查看自己创建的项目
    if current_user.is_admin:
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id).all()
    
    bugs = query.order_by(Bug.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('bug/index.html', bugs=bugs, projects=projects)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@active_required
@create_bug_permission_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        project_id = request.form['project_id']
        bug_type = request.form['type']
        category = request.form['category']
        
        bug = Bug(
            title=title,
            description=description,
            priority=priority,
            status='待处理',
            creator_id=current_user.id,
            project_id=project_id,
            type=bug_type,
            category=category
        )
        
        db.session.add(bug)
        db.session.commit()

        # 处理文件上传
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:  # 确保文件对象和文件名都存在
                try:
                    file_info, error = process_upload(file)
                    if error:
                        flash(f'文件 {file.filename} 上传失败: {error}')
                        continue
                    
                    # 使用安全处理后的文件名保存文件
                    file_path = save_file(file, file_info['safe_filename'])
                    
                    attachment = Attachment(
                        filename=file_info['original_filename'],  # 原始文件名(含中文)
                        stored_filename=file_info['safe_filename'],  # 安全处理后的文件名
                        file_path=file_path,
                        file_type=file_info['file_type'],
                        file_size=file_info['file_size'],
                        bug=bug,
                        uploader=current_user
                    )
                    db.session.add(attachment)
                except Exception as e:
                    current_app.logger.error(f'文件上传处理失败: {str(e)}')
                    flash(f'文件 {file.filename} 处理失败，请重试')
        
        db.session.commit()
        flash('Bug已创建')
        return redirect(url_for('bug.index'))
    
    # 管理员可以查看所有项目，普通用户只能查看自己创建的项目
    if current_user.is_admin:
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id).all()
    return render_template('bug/create.html', projects=projects)

@bp.route('/bug/<int:id>', methods=['GET', 'POST'])
@login_required
@active_required
@reply_bug_permission_required
def detail(id):
    from sqlalchemy.orm import joinedload, subqueryload
    bug = Bug.query.options(
        joinedload(Bug.project),
        joinedload(Bug.creator),
        subqueryload(Bug.comments).options(
            joinedload(Comment.author),
            joinedload(Comment.attachments)
        ),
        subqueryload(Bug.attachments).joinedload(Attachment.uploader)
    ).get_or_404(id)
    
    if request.method == 'POST':
        if bug.status == '已关闭':
            flash('已关闭的BUG不能修改')
            return redirect(url_for('bug.detail', id=id))
            
        # 处理状态更新
        new_status = request.form.get('status')
        if new_status and new_status != bug.status:
            bug.status = new_status
            flash('状态已更新')
            
        # 处理评论提交
        content = request.form.get('content', '').strip()
        comment = None
        if content:
            comment = Comment(
                content=content,
                bug=bug,
                author=current_user
            )
            db.session.add(comment)
            db.session.flush()  # 确保获取comment.id
            flash('评论已添加')
        
        # 处理文件上传
        files = request.files.getlist('files')
        if files:
            for file in files:
                # 检查文件是否有效
                if not file or not file.filename:
                    current_app.logger.debug('跳过无效文件')
                    continue
                    
                if bug.status == '已关闭':
                    flash('已关闭的BUG不能添加附件')
                    return redirect(url_for('bug.detail', id=id))
                    
                try:
                    current_app.logger.debug(f'开始处理文件: {file.filename}')
                    file_info, error = process_upload(file)
                    if error:
                        flash(f'文件 {file.filename} 上传失败: {error}')
                        current_app.logger.error(f'文件上传失败: {error}')
                        continue
                    
                    stored_filename = Attachment.generate_stored_filename(file_info['original_filename'])
                    current_app.logger.debug(f'生成存储文件名: {stored_filename}')
                    
                    file_path = save_file(file, stored_filename)
                    current_app.logger.debug(f'文件保存路径: {file_path}')
                    
                    attachment = Attachment(
                        filename=file_info['original_filename'],
                        stored_filename=stored_filename,
                        file_path=file_path,
                        file_type=file_info['file_type'],
                        file_size=file_info['file_size'],
                        bug=bug,
                        uploader=current_user,
                        comment=comment
                    )
                    db.session.add(attachment)
                    current_app.logger.debug(f'创建Attachment对象: {attachment}')
                    
                    # 立即提交以捕获可能的错误
                    db.session.commit()
                    current_app.logger.debug('文件上传成功')
                    flash(f'文件 {file.filename} 上传成功')
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'文件上传处理失败: {str(e)}', exc_info=True)
                    flash(f'文件 {file.filename} 处理失败: {str(e)}')
        
        db.session.commit()
        return redirect(url_for('bug.detail', id=id))
    
    return render_template('bug/detail.html', bug=bug)

@bp.route('/bug/<int:id>/edit', methods=['GET', 'POST'])
@creator_or_admin_required(Bug)
def edit(id):
    bug = Bug.query.get_or_404(id)
    
    if request.method == 'POST':
        bug.title = request.form['title']
        bug.description = request.form['description']
        bug.priority = request.form['priority']
        bug.status = request.form['status']
        bug.type = request.form['type']
        bug.category = request.form['category']
        bug.project_id = request.form['project_id']
        
        # 处理文件上传
        files = request.files.getlist('files')
        for file in files:
            if file.filename:
                file_info, error = process_upload(file)
                if error:
                    flash(f'文件 {file.filename} 上传失败: {error}')
                    continue
                
                stored_filename = Attachment.generate_stored_filename(file_info['original_filename'])
                file_path = save_file(file, stored_filename)
                
                attachment = Attachment(
                    filename=file_info['original_filename'],
                    stored_filename=stored_filename,
                    file_path=file_path,
                    file_type=file_info['file_type'],
                    file_size=file_info['file_size'],
                    bug=bug,
                    uploader=current_user
                )
                db.session.add(attachment)
        
        db.session.commit()
        flash('Bug已更新')
        return redirect(url_for('bug.detail', id=id))
    
    # 管理员可以查看所有项目，普通用户只能查看自己创建的项目
    if current_user.is_admin:
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(creator_id=current_user.id).all()
    return render_template('bug/edit.html', bug=bug, projects=projects)

@bp.route('/bug/attachment/<int:id>')
@login_required
def download_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
    
    if not os.path.exists(file_path):
        flash('文件不存在')
        return redirect(url_for('bug.detail', id=attachment.bug_id))
    
    # 获取文件扩展名
    file_ext = attachment.filename.rsplit('.', 1)[-1].lower() if '.' in attachment.filename else ''
    
    # 定义直接在浏览器中打开的文件类型
    preview_extensions = {'pdf', 'txt', 'md', 'jpg', 'jpeg', 'png', 'webp'}
    
    # 如果是可预览的文件类型，直接在浏览器中打开
    if file_ext in preview_extensions:
        return send_file(
            file_path,
            download_name=attachment.filename,
            as_attachment=False
        )
    
    # 其他类型的文件仍然作为附件下载
    return send_file(
        file_path,
        download_name=attachment.filename,
        as_attachment=True
    )

@bp.route('/bug/attachment/<int:id>/preview')
@login_required
def preview_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    
    if not attachment.is_previewable():
        flash('此文件类型不支持预览')
        return redirect(url_for('bug.detail', id=attachment.bug_id))
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
    
    if not os.path.exists(file_path):
        flash('文件不存在')
        return redirect(url_for('bug.detail', id=attachment.bug_id))
    
    return send_file(
        file_path,
        download_name=attachment.filename
    )

@bp.route('/bug/attachment/<int:id>/delete', methods=['POST'])
@creator_or_admin_required(Attachment)
def delete_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    bug_id = attachment.bug_id
    
    # 删除文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    db.session.delete(attachment)
    db.session.commit()
    
    flash('附件已删除')
    return redirect(url_for('bug.detail', id=bug_id))

@bp.route('/bug/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    bug = Bug.query.get_or_404(id)
    
    db.session.delete(bug)
    db.session.commit()
    flash('Bug已删除')
    return redirect(url_for('bug.index'))