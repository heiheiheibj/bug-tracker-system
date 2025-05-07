import os
import io
from app.models import Bug, Attachment
from app import db
from tests.base import BaseTestCase

class FileUploadTestCase(BaseTestCase):
    def setUp(self):
        """测试前设置"""
        super().setUp()
        self.login(self.user.username, 'user123')
        self.bug = self.create_bug('Test Bug', 'Test description')
        
        # 创建测试文件数据
        self.test_txt = (io.BytesIO(b'Hello World'), 'test.txt')
        self.test_img = (io.BytesIO(b'Fake image content'), 'test.jpg')
        self.test_doc = (io.BytesIO(b'Fake document content'), 'test.doc')

    def test_file_upload_with_bug_creation(self):
        """测试创建Bug时上传文件"""
        files = [('files', self.test_txt)]
        response = self.client.post('/create', 
            data={
                'title': 'Bug with File',
                'description': 'Bug description',
                'priority': '中',
                'category': '功能',
                'files': (io.BytesIO(b'Hello World'), 'test.txt')
            },
            content_type='multipart/form-data',
            follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug已创建'.encode('utf-8'), response.data)
        
        # 验证文件已上传
        bug = Bug.query.filter_by(title='Bug with File').first()
        self.assertIsNotNone(bug)
        self.assertEqual(len(bug.attachments), 1)
        self.assertEqual(bug.attachments[0].filename, 'test.txt')

    def test_multiple_file_upload(self):
        """测试多文件上传"""
        files = [
            ('files', self.test_txt),
            ('files', self.test_img),
            ('files', self.test_doc)
        ]
        
        response = self.client.post(f'/bug/{self.bug.id}/edit',
            data={
                'title': self.bug.title,
                'description': self.bug.description,
                'priority': self.bug.priority,
                'status': self.bug.status,
                'category': self.bug.category,
                'files': [
                    (io.BytesIO(b'Hello World'), 'test.txt'),
                    (io.BytesIO(b'Fake image content'), 'test.jpg'),
                    (io.BytesIO(b'Fake document content'), 'test.doc')
                ]
            },
            follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证所有文件都已上传
        bug = Bug.query.get(self.bug.id)
        self.assertEqual(len(bug.attachments), 3)
        filenames = [a.filename for a in bug.attachments]
        self.assertIn('test.txt', filenames)
        self.assertIn('test.jpg', filenames)
        self.assertIn('test.doc', filenames)

    def test_invalid_file_type(self):
        """测试上传无效文件类型"""
        response = self.client.post(f'/bug/{self.bug.id}/edit',
            data={
                'title': self.bug.title,
                'description': self.bug.description,
                'priority': self.bug.priority,
                'status': self.bug.status,
                'category': self.bug.category,
                'files': (io.BytesIO(b'Invalid file content'), 'test.invalid')
            },
            follow_redirects=True)
        
        self.assertIn(r'不支持的文件类型'.encode('utf-8'), response.data)

    def test_file_download(self):
        """测试文件下载"""
        # 创建测试附件
        test_content = b'Test file content'
        filepath = self.create_test_file('test.txt', test_content)
        
        attachment = Attachment(
            filename='test.txt',
            stored_filename=os.path.basename(filepath),
            file_path=os.path.relpath(filepath, self.app.config['UPLOAD_FOLDER']),
            file_type='text/plain',
            file_size=len(test_content),
            bug=self.bug,
            uploader=self.user
        )
        db.session.add(attachment)
        db.session.commit()
        
        # 测试下载
        response = self.client.get(f'/attachment/{attachment.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, test_content)
        self.assertEqual(
            response.headers['Content-Disposition'],
            'attachment; filename=test.txt'
        )

    def test_file_preview(self):
        """测试文件预览"""
        # 创建测试图片附件
        test_content = b'Fake image content'
        filepath = self.create_test_file('test.jpg', test_content)
        
        attachment = Attachment(
            filename='test.jpg',
            stored_filename=os.path.basename(filepath),
            file_path=os.path.relpath(filepath, self.app.config['UPLOAD_FOLDER']),
            file_type='image/jpeg',
            file_size=len(test_content),
            bug=self.bug,
            uploader=self.user
        )
        db.session.add(attachment)
        db.session.commit()
        
        # 测试预览
        response = self.client.get(f'/attachment/{attachment.id}/preview')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, test_content)

    def test_file_deletion(self):
        """测试文件删除"""
        # 创建测试附件
        filepath = self.create_test_file()
        
        attachment = Attachment(
            filename='test.txt',
            stored_filename=os.path.basename(filepath),
            file_path=os.path.relpath(filepath, self.app.config['UPLOAD_FOLDER']),
            file_type='text/plain',
            file_size=0,
            bug=self.bug,
            uploader=self.user
        )
        db.session.add(attachment)
        db.session.commit()
        
        # 测试删除
        response = self.client.post(f'/attachment/{attachment.id}/delete', 
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'附件已删除'.encode('utf-8'), response.data)
        
        # 验证文件和数据库记录都已删除
        self.assertFalse(os.path.exists(filepath))
        self.assertIsNone(Attachment.query.get(attachment.id))

if __name__ == '__main__':
    unittest.main()