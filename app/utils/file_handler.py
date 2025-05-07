import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {
    # 图片
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
    # 文档
    'txt', 'text', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
    'html', 'htm', 'md', 'csv', 'rtf', 'odt',
    # 压缩包
    'zip', 'rar', '7z', 'tar', 'gz',
    # 视频
    'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'mpeg', 'mpg',
    # 音频  
    'mp3', 'wav', 'ogg', 'aac', 'wma',
    # 其他
    'json', 'xml'
}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """获取文件类型"""
    try:
        if not filename or '.' not in filename:
            return 'application/octet-stream'
            
        ext = filename.rsplit('.', 1)[1].lower()
        # 简单的MIME类型映射
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'html': 'text/html',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed'
        }
        return mime_types.get(ext, 'application/octet-stream')
    except Exception:
        return 'application/octet-stream'

def create_upload_path():
    """创建基于日期的上传目录"""
    today = datetime.now()
    upload_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        str(today.year),
        f"{today.month:02d}"
    )
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    return upload_dir

def save_file(file, stored_filename):
    """保存上传的文件"""
    upload_dir = create_upload_path()
    file_path = os.path.join(upload_dir, stored_filename)
    file.save(file_path)
    
    # 返回相对于UPLOAD_FOLDER的路径
    return os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER'])

def get_file_size(file):
    """获取文件大小"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # 重置文件指针
    return size

def validate_file(file):
    """验证上传的文件"""
    if not file:
        return False, "没有选择文件"
    
    if not file.filename:
        return False, "文件名无效"
    
    if not allowed_file(file.filename):
        return False, "不支持的文件类型"
    
    file_size = get_file_size(file)
    if file_size > current_app.config['MAX_CONTENT_LENGTH']:
        return False, "文件大小超过限制"
    
    return True, None

def process_upload(file):
    """处理文件上传"""
    try:
        # 验证文件
        is_valid, error_message = validate_file(file)
        if not is_valid:
            return None, error_message
        
        # 获取原始文件名
        original_filename = file.filename
        
        # 安全处理文件名但保留中文
        safe_filename = secure_filename(original_filename)
        if not safe_filename:  # 如果secure_filename去掉了所有字符(如纯中文名)
            ext = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else ''
            safe_filename = f'file_{int(time.time())}.{ext}'
        
        # 获取文件信息
        file_type = get_file_type(original_filename)
        file_size = get_file_size(file)
        
        return {
            'original_filename': original_filename,  # 返回完整原始名
            'safe_filename': safe_filename,        # 安全处理后的文件名
            'file_type': file_type,
            'file_size': file_size
        }, None
    except Exception as e:
        return None, f'文件处理失败: {str(e)}'