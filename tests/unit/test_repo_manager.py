import unittest
import os
import tempfile
import shutil
import subprocess
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.repo_manager import RepoManager

class TestRepoManager(unittest.TestCase):
    """测试仓库管理器"""

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

        # 创建仓库管理器实例
        self.repo = RepoManager(self.test_dir)

    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_get_current_branch(self):
        """测试获取当前分支"""
        branch = self.repo.get_current_branch()
        self.assertEqual(branch, 'main')

    def test_create_branch(self):
        """测试创建分支"""
        # 创建新分支
        success = self.repo.create_branch('feature-test')
        self.assertTrue(success)

        # 验证分支已创建
        result = subprocess.run(['git', 'branch'], capture_output=True, text=True, check=True)
        self.assertIn('feature-test', result.stdout)

    def test_commit_changes(self):
        """测试提交更改"""
        # 创建测试文件
        with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
            f.write('Test content')

        # 提交更改
        success = self.repo.commit_changes('test: add test file')
        self.assertTrue(success)

        # 验证提交
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), 'test: add test file')

    def test_get_commit_history(self):
        """测试获取提交历史"""
        # 创建多个提交
        for i in range(3):
            with open(os.path.join(self.test_dir, f'test{i}.txt'), 'w') as f:
                f.write(f'Test content {i}')
            self.repo.commit_changes(f'test: add test file {i}')

        # 获取提交历史
        commits = self.repo.get_commit_history(max_count=3)
        self.assertEqual(len(commits), 3)
        self.assertEqual(commits[0]['message'], 'test: add test file 2')

    def test_get_file_changes(self):
        """测试获取文件更改"""
        # 创建新文件
        with open(os.path.join(self.test_dir, 'new.txt'), 'w') as f:
            f.write('New content')

        # 修改现有文件
        with open(os.path.join(self.test_dir, 'initial.txt'), 'a') as f:
            f.write('\nModified content')

        # 添加文件到Git
        subprocess.run(['git', 'add', 'initial.txt'], check=True, capture_output=True)

        # 获取更改
        changes = self.repo.get_file_changes()
        self.assertIn('new.txt', changes['added'])
        self.assertIn('initial.txt', changes['modified'])

    def test_create_tag(self):
        """测试创建标签"""
        # 模拟远程仓库操作
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            success = self.repo.create_tag('v1.0.0', 'First release')
            self.assertTrue(success)

            # 验证标签创建命令
            create_tag_call = mock_run.call_args_list[0]
            self.assertEqual(create_tag_call[0][0][:3], ['git', 'tag', '-a'])

    def test_sync_with_remote(self):
        """测试同步远程仓库"""
        # 模拟远程仓库操作
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            success = self.repo.sync_with_remote('main')
            self.assertTrue(success)

            # 验证同步命令
            self.assertEqual(len(mock_run.call_args_list), 3)  # fetch, checkout, pull
            pull_call = mock_run.call_args_list[2]
            self.assertEqual(pull_call[0][0][:2], ['git', 'pull'])

    def test_merge_branch(self):
        """测试合并分支"""
        # 创建并切换到新分支
        self.repo.create_branch('feature-test')

        # 在新分支上创建提交
        with open(os.path.join(self.test_dir, 'feature.txt'), 'w') as f:
            f.write('Feature content')
        self.repo.commit_changes('feat: add feature')

        # 切换回main分支
        subprocess.run(['git', 'checkout', 'main'], check=True, capture_output=True)

        # 测试merge策略
        success = self.repo.merge_branch('feature-test')
        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'feature.txt')))

    def test_merge_with_conflict(self):
        """测试处理合并冲突"""
        # 创建并切换到新分支
        self.repo.create_branch('conflict-test')

        # 在新分支上修改文件
        with open(os.path.join(self.test_dir, 'initial.txt'), 'w') as f:
            f.write('Feature content')
        self.repo.commit_changes('feat: modify file in feature')

        # 切换回main分支并修改同一个文件
        subprocess.run(['git', 'checkout', 'main'], check=True, capture_output=True)
        with open(os.path.join(self.test_dir, 'initial.txt'), 'w') as f:
            f.write('Main content')
        self.repo.commit_changes('feat: modify file in main')

        # 尝试合并，应该会有冲突
        try:
            self.repo.merge_branch('conflict-test')
        except subprocess.CalledProcessError:
            pass

        # 解决冲突
        success = self.repo.resolve_conflicts('ours')
        self.assertTrue(success)

        # 验证文件内容
        with open(os.path.join(self.test_dir, 'initial.txt'), 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Main content')

    def test_cherry_pick(self):
        """测试Cherry-pick操作"""
        # 创建并切换到新分支
        self.repo.create_branch('feature-test')

        # 创建多个提交
        commits = []
        for i in range(3):
            with open(os.path.join(self.test_dir, f'feature{i}.txt'), 'w') as f:
                f.write(f'Feature content {i}')
            self.repo.commit_changes(f'feat: add feature {i}')
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True)
            commits.append(result.stdout.strip())

        # 切换回main分支
        subprocess.run(['git', 'checkout', 'main'], check=True, capture_output=True)

        # Cherry-pick提交
        success = self.repo.cherry_pick(commits)
        self.assertTrue(success)

        # 验证文件是否存在
        for i in range(3):
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, f'feature{i}.txt')))

    def test_stash_operations(self):
        """测试暂存操作"""
        # 创建未提交的更改
        with open(os.path.join(self.test_dir, 'stash.txt'), 'w') as f:
            f.write('Stash content')

        # 创建暂存
        success = self.repo.stash_changes('test stash')
        self.assertTrue(success)

        # 等待文件系统更新
        time.sleep(0.1)

        # 验证文件已被暂存
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'stash.txt')))

        # 获取暂存列表
        stashes = self.repo.list_stashes()
        self.assertEqual(len(stashes), 1)
        self.assertIn('test stash', stashes[0]['message'])

        # 恢复暂存
        success = self.repo.pop_stash()
        self.assertTrue(success)

        # 等待文件系统更新
        time.sleep(0.1)

        # 验证文件已恢复
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'stash.txt')))
        with open(os.path.join(self.test_dir, 'stash.txt'), 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Stash content')

    def test_list_hooks(self):
        """测试列出Git hooks"""
        hooks = self.repo.list_hooks()
        self.assertIsInstance(hooks, dict)
        self.assertTrue(len(hooks) > 0)

        # 验证hook信息结构
        for hook_name, hook_info in hooks.items():
            self.assertIsInstance(hook_name, str)
            self.assertIsInstance(hook_info, dict)
            self.assertIn('exists', hook_info)
            self.assertIn('enabled', hook_info)
            self.assertIn('executable', hook_info)
            self.assertIn('size', hook_info)
            self.assertIn('last_modified', hook_info)
            self.assertIn('is_sample', hook_info)

    def test_install_and_remove_hook(self):
        """测试安装和移除Git hook"""
        hook_name = 'pre-commit'
        hook_content = '#!/bin/sh\necho "Running pre-commit hook"\nexit 0'

        # 测试安装hook
        success = self.repo.install_hook(hook_name, hook_content)
        self.assertTrue(success)

        # 验证hook已安装
        hooks = self.repo.list_hooks()
        self.assertIn(hook_name, hooks)
        self.assertTrue(hooks[hook_name]['exists'])
        self.assertTrue(hooks[hook_name]['executable'])

        # 测试移除hook
        success = self.repo.remove_hook(hook_name)
        self.assertTrue(success)

        # 验证hook已移除
        hooks = self.repo.list_hooks()
        self.assertIn(hook_name, hooks)
        self.assertFalse(hooks[hook_name]['exists'])

    def test_enable_and_disable_hook(self):
        """测试启用和禁用Git hook"""
        hook_name = 'pre-commit'
        hook_content = '#!/bin/sh\necho "Running pre-commit hook"\nexit 0'

        # 先安装hook
        self.repo.install_hook(hook_name, hook_content)

        # 测试禁用hook
        success = self.repo.disable_hook(hook_name)
        self.assertTrue(success)

        # 验证hook已禁用
        hooks = self.repo.list_hooks()
        self.assertIn(hook_name, hooks)
        self.assertFalse(hooks[hook_name]['enabled'])

        # 测试启用hook
        success = self.repo.enable_hook(hook_name)
        self.assertTrue(success)

        # 验证hook已启用
        hooks = self.repo.list_hooks()
        self.assertIn(hook_name, hooks)
        self.assertTrue(hooks[hook_name]['enabled'])

        # 清理
        self.repo.remove_hook(hook_name)

    def test_nonexistent_hook(self):
        """测试操作不存在的hook"""
        hook_name = 'nonexistent-hook'

        # 测试移除不存在的hook
        success = self.repo.remove_hook(hook_name)
        self.assertFalse(success)

        # 测试启用不存在的hook
        success = self.repo.enable_hook(hook_name)
        self.assertFalse(success)

        # 测试禁用不存在的hook
        success = self.repo.disable_hook(hook_name)
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
