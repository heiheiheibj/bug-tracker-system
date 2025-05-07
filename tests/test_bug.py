import unittest
from app.models import Bug
from app import db
from tests.base import BaseTestCase

class BugTestCase(BaseTestCase):
    def setUp(self):
        """测试前设置"""
        super().setUp()
        self.login(self.user.username, 'user123')  # 默认以普通用户登录

    def test_bug_list_page(self):
        """测试Bug列表页面"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug列表'.encode('utf-8'), response.data)

    def test_create_bug_page(self):
        """测试创建Bug页面"""
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'提交Bug'.encode('utf-8'), response.data)

    def test_create_bug(self):
        """测试创建Bug"""
        response = self.client.post('/create', data={
            'title': 'Test Bug',
            'description': 'This is a test bug',
            'priority': '高',
            'category': '功能'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug已创建'.encode('utf-8'), response.data)
        
        # 验证Bug已创建
        bug = Bug.query.filter_by(title='Test Bug').first()
        self.assertIsNotNone(bug)
        self.assertEqual(bug.description, 'This is a test bug')
        self.assertEqual(bug.priority, '高')
        self.assertEqual(bug.category, '功能')
        self.assertEqual(bug.creator, self.user)

    def test_edit_bug(self):
        """测试编辑Bug"""
        # 创建一个Bug
        bug = self.create_bug('Original Bug', 'Original description')
        
        # 编辑Bug
        response = self.client.post(f'/bug/{bug.id}/edit', data={
            'title': 'Updated Bug',
            'description': 'Updated description',
            'priority': '低',
            'status': '处理中',
            'category': '界面'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug已更新'.encode('utf-8'), response.data)
        
        # 验证更新
        updated_bug = Bug.query.get(bug.id)
        self.assertEqual(updated_bug.title, 'Updated Bug')
        self.assertEqual(updated_bug.description, 'Updated description')
        self.assertEqual(updated_bug.priority, '低')
        self.assertEqual(updated_bug.status, '处理中')
        self.assertEqual(updated_bug.category, '界面')

    def test_bug_detail(self):
        """测试Bug详情页面"""
        bug = self.create_bug('Test Bug', 'Test description')
        
        response = self.client.get(f'/bug/{bug.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Test Bug'.encode('utf-8'), response.data)
        self.assertIn(r'Test description'.encode('utf-8'), response.data)

    def test_delete_bug(self):
        """测试删除Bug"""
        # 切换到管理员账号
        self.logout()
        self.login(self.admin.username, 'admin123')
        
        # 创建Bug
        bug = self.create_bug('Test Bug', 'Test description')
        
        # 删除Bug
        response = self.client.post(f'/bug/{bug.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug已删除'.encode('utf-8'), response.data)
        
        # 验证Bug已删除
        deleted_bug = Bug.query.get(bug.id)
        self.assertIsNone(deleted_bug)

    def test_unauthorized_bug_edit(self):
        """测试未授权的Bug编辑"""
        # 创建一个由管理员创建的Bug
        self.logout()
        self.login(self.admin.username, 'admin123')
        bug = self.create_bug('Admin Bug', 'Admin description')
        
        # 切换到普通用户
        self.logout()
        self.login(self.user.username, 'user123')
        
        # 尝试编辑管理员的Bug
        response = self.client.post(f'/bug/{bug.id}/edit', data={
            'title': 'Hacked Bug',
            'description': 'Hacked description',
            'priority': '低',
            'status': '已关闭',
            'category': '功能'
        }, follow_redirects=True)
        
        # 应该返回403错误
        self.assertEqual(response.status_code, 403)
        
        # 验证Bug未被修改
        unchanged_bug = Bug.query.get(bug.id)
        self.assertEqual(unchanged_bug.title, 'Admin Bug')
        self.assertEqual(unchanged_bug.description, 'Admin description')

    def test_admin_delete_bug(self):
        """测试管理员删除Bug权限"""
        # 创建一个普通用户的Bug
        bug = self.create_bug('Test Bug', 'Test description')
        
        # 切换到管理员账号
        self.logout()
        self.login(self.admin.username, 'admin123')
        
        # 管理员应该能删除任何Bug
        response = self.client.post(f'/bug/{bug.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug已删除'.encode('utf-8'), response.data)
        
        # 验证Bug已被删除
        self.assertIsNone(Bug.query.get(bug.id))

    def test_user_delete_bug_forbidden(self):
        """测试普通用户删除Bug权限限制"""
        # 创建一个由管理员创建的Bug
        self.logout()
        self.login(self.admin.username, 'admin123')
        bug = self.create_bug('Admin Bug', 'Admin description')
        
        # 切换到普通用户
        self.logout()
        self.login(self.user.username, 'user123')
        
        # 普通用户不应该能删除Bug
        response = self.client.post(f'/bug/{bug.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        
        # 验证Bug未被删除
        self.assertIsNotNone(Bug.query.get(bug.id))

    def test_bug_status_workflow(self):
        """测试Bug状态流转"""
        bug = self.create_bug('Workflow Bug', 'Test workflow')
        
        # 验证初始状态
        self.assertEqual(bug.status, '待处理')
        
        # 更新状态为处理中
        response = self.client.post(f'/bug/{bug.id}/edit', data={
            'title': bug.title,
            'description': bug.description,
            'priority': bug.priority,
            'status': '处理中',
            'category': bug.category
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        updated_bug = Bug.query.get(bug.id)
        self.assertEqual(updated_bug.status, '处理中')

if __name__ == '__main__':
    unittest.main()