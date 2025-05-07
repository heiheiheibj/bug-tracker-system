import unittest
from app.models import User
from app import db
from tests.base import BaseTestCase

class AuthTestCase(BaseTestCase):
    def test_login_page(self):
        """测试登录页面访问"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'用户登录'.encode('utf-8'), response.data)

    def test_register_page(self):
        """测试注册页面访问"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'用户注册'.encode('utf-8'), response.data)

    def test_valid_login(self):
        """测试有效登录"""
        response = self.login(self.user.username, 'user123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'Bug列表'.encode('utf-8'), response.data)

    def test_invalid_login(self):
        """测试无效登录"""
        response = self.login('user', 'wrongpassword')
        self.assertIn(r'用户名或密码错误'.encode('utf-8'), response.data)

    def test_logout(self):
        """测试注销"""
        self.login(self.user.username, 'user123')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'用户登录'.encode('utf-8'), response.data)

    def test_valid_registration(self):
        """测试有效注册"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(r'注册成功'.encode('utf-8'), response.data)
        
        # 验证用户已创建
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')

    def test_duplicate_username_registration(self):
        """测试重复用户名注册"""
        response = self.client.post('/register', data={
            'username': self.user.username,  # 已存在的用户名
            'email': 'another@example.com',
            'password': 'pass123'
        }, follow_redirects=True)
        self.assertIn(r'该用户名已被使用'.encode('utf-8'), response.data)

    def test_duplicate_email_registration(self):
        """测试重复邮箱注册"""
        response = self.client.post('/register', data={
            'username': 'another',
            'email': self.user.email,  # 已存在的邮箱
            'password': 'pass123'
        }, follow_redirects=True)
        self.assertIn(r'该邮箱已被注册'.encode('utf-8'), response.data)

    def test_admin_access(self):
        """测试管理员访问权限"""
        # 管理员登录
        self.login(self.admin.username, 'admin123')
        
        # 测试访问管理功能
        response = self.client.get('/bug/1/delete')
        self.assertNotEqual(response.status_code, 403)  # 不应该返回禁止访问

    def test_user_access_restriction(self):
        """测试普通用户访问限制"""
        # 普通用户登录
        self.login(self.user.username, 'user123')
        
        # 创建一个由管理员创建的Bug
        admin_bug = self.create_bug('Admin Bug', 'Test bug', user=self.admin)
        
        # 测试删除其他用户的Bug
        response = self.client.post(f'/bug/{admin_bug.id}/delete', follow_redirects=True)
        self.assertIn(r'只有管理员可以删除Bug'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()