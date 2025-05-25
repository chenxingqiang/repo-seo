import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import io
import tempfile
import logging

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.commit_message_fixer import (
    parse_commit_message,
    suggest_commit_type,
    fix_commit_message,
    check_branch_name,
    get_changed_files,
    print_commit_guide,
    main,
    COMMIT_TYPES
)

class TestCommitMessageFixer(unittest.TestCase):
    """测试提交信息修复工具的各个组件"""

    def test_parse_commit_message_valid(self):
        """测试解析有效的提交信息"""
        test_cases = [
            {
                'message': 'feat(auth): add user authentication',
                'expected': {
                    'type': 'feat',
                    'scope': 'auth',
                    'description': 'add user authentication'
                }
            },
            {
                'message': 'fix: resolve memory leak',
                'expected': {
                    'type': 'fix',
                    'scope': None,
                    'description': 'resolve memory leak'
                }
            },
            {
                'message': 'docs(readme): update installation guide',
                'expected': {
                    'type': 'docs',
                    'scope': 'readme',
                    'description': 'update installation guide'
                }
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case['message']):
                result = parse_commit_message(case['message'])
                self.assertEqual(result, case['expected'])

    def test_parse_commit_message_invalid(self):
        """测试解析无效的提交信息"""
        invalid_messages = [
            'add new feature',
            'fix something',
            'feat:missing space',
            'invalid(scope): message',
            ': empty type',
            'feat(): empty scope'
        ]

        for message in invalid_messages:
            with self.subTest(msg=message):
                result = parse_commit_message(message)
                self.assertIsNone(result)

    def test_suggest_commit_type(self):
        """测试提交类型建议功能"""
        test_cases = [
            {
                'files': ['README.md', 'docs/guide.rst'],
                'expected': 'docs'
            },
            {
                'files': ['src/test_api.py', 'tests/unit_test.js'],
                'expected': 'test'
            },
            {
                'files': ['package.json', 'requirements.txt'],
                'expected': 'build'
            },
            {
                'files': ['.github/workflows/ci.yml'],
                'expected': 'ci'
            },
            {
                'files': ['src/main.py', 'lib/utils.js'],
                'expected': 'feat'
            }
        ]

        for case in test_cases:
            with self.subTest(msg=str(case['files'])):
                result = suggest_commit_type(case['files'])
                self.assertEqual(result, case['expected'])

    @patch('src.commit_message_fixer.get_changed_files')
    def test_fix_commit_message(self, mock_get_files):
        """测试提交信息修复功能"""
        # 模拟更改的文件
        mock_get_files.return_value = ['src/main.py']

        test_cases = [
            {
                'message': 'add new feature',
                'expected': 'feat: add new feature'
            },
            {
                'message': 'fix bug',
                'expected': 'feat: fix bug'
            },
            {
                'message': 'feat(auth): add login',  # 已经符合规范
                'expected': 'feat(auth): add login'
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case['message']):
                result = fix_commit_message(case['message'])
                self.assertEqual(result, case['expected'])

    @patch('subprocess.run')
    def test_check_branch_name(self, mock_run):
        """测试分支名称检查功能"""
        test_cases = [
            {
                'branch': 'main',
                'expected': True
            },
            {
                'branch': '123-feat-new-feature',
                'expected': True
            },
            {
                'branch': '456-fix-memory-leak',
                'expected': True
            },
            {
                'branch': 'invalid-branch',
                'expected': False
            },
            {
                'branch': '123-invalid-type',
                'expected': False
            }
        ]

        for case in test_cases:
            with self.subTest(msg=case['branch']):
                # 模拟 git branch 命令的输出
                mock_run.return_value = MagicMock(
                    stdout=case['branch'],
                    returncode=0
                )
                result = check_branch_name()
                self.assertEqual(result, case['expected'])

    @patch('subprocess.run')
    def test_get_changed_files(self, mock_run):
        """测试获取更改的文件功能"""
        # 模拟 git diff 命令的输出
        mock_process = MagicMock()
        mock_process.stdout = "src/main.py\ntests/test_main.py\nREADME.md"
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # 测试获取更改的文件
        files = get_changed_files()
        self.assertEqual(files, ["src/main.py", "tests/test_main.py", "README.md"])

        # 测试命令执行失败的情况
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_run.return_value = mock_process
        files = get_changed_files()
        self.assertEqual(files, [])

    def test_commit_types_completeness(self):
        """测试提交类型的完整性"""
        expected_types = {
            'feat', 'fix', 'docs', 'style', 'refactor',
            'perf', 'test', 'build', 'ci', 'chore'
        }
        self.assertEqual(set(COMMIT_TYPES.keys()), expected_types)

    def test_print_commit_guide(self):
        """测试打印提交指南功能"""
        # 设置一个临时的日志处理器来捕获日志输出
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('src.commit_message_fixer')

        # Save the original level and handlers
        original_level = logger.level
        original_handlers = logger.handlers.copy()

        # Set the logger level to INFO to ensure messages are captured
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        try:
            # 调用函数
            print_commit_guide()

            # 获取捕获的日志
            log_text = log_capture.getvalue()

            # 验证日志调用包含所有提交类型
            for commit_type, description in COMMIT_TYPES.items():
                self.assertIn(commit_type, log_text, f"提交类型 {commit_type} 未在日志中找到")
        finally:
            # Restore the original logger configuration
            logger.setLevel(original_level)
            logger.handlers = original_handlers

    @patch('src.commit_message_fixer.fix_commit_message')
    def test_main_with_commit_file(self, mock_fix):
        """测试主函数处理提交文件的功能"""
        # 模拟修复提交信息
        mock_fix.return_value = "feat: fixed commit message"

        # 创建临时提交信息文件
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write("original commit message")
            temp_path = temp.name

        try:
            # 测试主函数
            with patch.object(sys, 'argv', ['commit_message_fixer.py', temp_path]):
                main()

            # 验证文件内容被修改
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "feat: fixed commit message")

            # 验证fix_commit_message被调用
            mock_fix.assert_called_once_with("original commit message")
        finally:
            # 清理临时文件
            os.unlink(temp_path)

    @patch('src.commit_message_fixer.print_commit_guide')
    def test_main_without_args(self, mock_print_guide):
        """测试主函数无参数时的功能"""
        # 测试无参数调用主函数
        with patch.object(sys, 'argv', ['commit_message_fixer.py']):
            try:
                main()
                self.fail("Expected SystemExit exception was not raised")
            except SystemExit as e:
                self.assertEqual(e.code, 1)

        # 验证打印提交指南被调用
        mock_print_guide.assert_not_called()

if __name__ == '__main__':
    unittest.main()
