import unittest
import os
import subprocess
import tempfile
import shutil
from unittest.mock import patch
import sys
# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.commit_message_fixer import fix_commit_message, check_branch_name

class TestGitIntegration(unittest.TestCase):
    """测试Git集成功能"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # 初始化Git仓库
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True, capture_output=True)

        # 创建并切换到main分支
        subprocess.run(['git', 'checkout', '-b', 'main'], check=True, capture_output=True)

        # 创建测试文件并进行初始提交
        with open(os.path.join(self.test_dir, 'initial.txt'), 'w') as f:
            f.write('Initial commit')
        subprocess.run(['git', 'add', 'initial.txt'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True, capture_output=True)

        # 设置Git hooks
        hooks_dir = os.path.join(self.test_dir, '.git', 'hooks')
        os.makedirs(hooks_dir, exist_ok=True)
        self.hook_path = os.path.join(hooks_dir, 'commit-msg')

        # 创建commit-msg hook
        with open(self.hook_path, 'w') as f:
            f.write('#!/bin/sh\n')
            f.write('python3 -m src.commit_message_fixer "$1"\n')

        os.chmod(self.hook_path, 0o755)

    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def create_test_files(self):
        """创建测试用的文件"""
        # 创建Python文件
        with open(os.path.join(self.test_dir, 'test.py'), 'w') as f:
            f.write('print("Hello, World!")')

        # 创建文档文件
        with open(os.path.join(self.test_dir, 'README.md'), 'w') as f:
            f.write('# Test Repository')

    def commit_changes(self, message):
        """提交更改"""
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        try:
            result = subprocess.run(['git', 'commit', '-m', message],
                                  capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return e.returncode

    def test_valid_commit_messages(self):
        """测试有效的提交信息"""
        valid_messages = [
            'feat(auth): add user authentication',
            'fix: resolve memory leak',
            'docs(readme): update documentation',
            'style: format code',
            'refactor: restructure database layer',
            'test: add unit tests'
        ]

        for message in valid_messages:
            with self.subTest(msg=message):
                # 直接使用fix_commit_message函数
                fixed_message = fix_commit_message(message)
                self.assertEqual(message, fixed_message,
                               f"Message '{message}' should not be modified")

    def test_invalid_commit_messages(self):
        """测试无效的提交信息"""
        invalid_messages = [
            'add new feature',
            'fix something',
            'update docs',
            'invalid(scope): message'
        ]

        for message in invalid_messages:
            with self.subTest(msg=message):
                # 直接使用fix_commit_message函数
                fixed_message = fix_commit_message(message)
                self.assertTrue(fixed_message.startswith(('feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore')),
                              f"Fixed message '{fixed_message}' should start with a valid type")

    def test_commit_with_different_file_types(self):
        """测试不同类型文件的提交"""
        test_cases = [
            {
                'file': 'test_api.py',
                'content': 'def test_function(): pass',
                'message': 'add test function',
                'expected_type': 'test'
            },
            {
                'file': 'README.md',
                'content': '# Documentation',
                'message': 'update readme',
                'expected_type': 'docs'
            },
            {
                'file': 'requirements.txt',
                'content': 'pytest==6.2.4',
                'message': 'update dependencies',
                'expected_type': 'build'
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case['file']):
                # 清理之前的文件
                for f in os.listdir(self.test_dir):
                    if f != '.git' and f != 'initial.txt':
                        path = os.path.join(self.test_dir, f)
                        if os.path.isfile(path):
                            os.unlink(path)

                # 创建文件
                with open(os.path.join(self.test_dir, case['file']), 'w') as f:
                    f.write(case['content'])

                # 添加文件到Git
                subprocess.run(['git', 'add', case['file']], check=True, capture_output=True)

                # 直接使用fix_commit_message函数
                fixed_message = fix_commit_message(case['message'])
                self.assertTrue(fixed_message.startswith(case['expected_type']),
                              f"Fixed message should start with {case['expected_type']}, got {fixed_message}")

    def test_branch_name_validation(self):
        """测试分支名称验证"""
        test_cases = [
            {
                'branch': '123-feat-new-feature',
                'should_succeed': True
            },
            {
                'branch': 'invalid-branch',
                'should_succeed': False
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case['branch']):
                # 创建并切换到测试分支
                subprocess.run(['git', 'checkout', '-b', case['branch']],
                             check=True, capture_output=True)

                # 直接使用check_branch_name函数
                result = check_branch_name()
                self.assertEqual(result, case['should_succeed'],
                               f"Branch name validation for '{case['branch']}' failed")

                # 切回main分支
                subprocess.run(['git', 'checkout', 'main'], check=True, capture_output=True)

                # 删除测试分支
                subprocess.run(['git', 'branch', '-D', case['branch']],
                             check=True, capture_output=True)

if __name__ == '__main__':
    unittest.main()
