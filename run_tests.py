#!/usr/bin/env python3
import unittest
import coverage
import sys
import os

def run_tests_with_coverage():
    """运行所有测试并生成覆盖率报告"""
    # 启动覆盖率收集
    cov = coverage.Coverage(
        branch=True,
        source=['src'],
        omit=['*/__pycache__/*', 'tests/*']
    )
    cov.start()

    # 发现并运行测试
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 停止覆盖率收集
    cov.stop()
    cov.save()

    # 打印覆盖率报告
    print('\nCoverage Summary:')
    cov.report()

    # 生成HTML报告
    cov.html_report(directory='coverage_html')
    print('\nDetailed coverage report generated in coverage_html/index.html')

    return result.wasSuccessful()

if __name__ == '__main__':
    # 确保在正确的目录中运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("运行提交信息修复工具的测试套件...")
    success = run_tests_with_coverage()

    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
