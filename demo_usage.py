#!/usr/bin/env python3
"""
GitHub Repository SEO Optimizer 实际使用示例
"""

import os
import sys
import subprocess

def demo_cli_usage():
    """演示命令行使用"""
    print("🚀 GitHub Repository SEO Optimizer 使用演示\n")
    print("="*60)
    
    # 设置PATH
    os.environ['PATH'] = f"{os.environ['PATH']}:/Users/xingqiangchen/Library/Python/3.11/bin"
    
    demos = [
        ("查看版本", "github-repo-seo --version"),
        ("查看帮助", "github-repo-seo --help"),
        ("列出LLM提供商", "github-repo-seo providers"),
        ("查看优化命令帮助", "github-repo-seo optimize --help"),
        ("查看批处理命令帮助", "github-repo-seo batch --help"),
        ("查看同步命令帮助", "github-repo-seo sync --help"),
    ]
    
    for title, cmd in demos:
        print(f"\n📌 {title}")
        print(f"命令: {cmd}")
        print("-" * 60)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"错误: {result.stderr}")

def demo_python_usage():
    """演示Python API使用"""
    print("\n\n🐍 Python API 使用示例")
    print("="*60)
    
    # 1. 使用本地Provider生成描述
    print("\n1️⃣ 使用本地Provider生成仓库描述:")
    print("-" * 60)
    code = '''
from repo_seo.ai_client import AIClient

# 创建本地AI客户端（不需要API密钥）
client = AIClient(provider="local")

# 生成仓库描述
description = client.generate_description(
    language="Python",
    files=["main.py", "utils.py", "config.py"],
    readme_content="A Python utility library for data processing"
)

print(f"生成的描述: {description}")
'''
    print(f"代码:\n{code}")
    print("\n输出:")
    exec(code)
    
    # 2. 生成主题标签
    print("\n\n2️⃣ 生成仓库主题标签:")
    print("-" * 60)
    code = '''
# 生成主题标签
topics = client.generate_topics(
    language="Python",
    files=["main.py", "utils.py", "config.py"],
    readme_content="A Python utility library for data processing"
)

print(f"生成的主题: {topics}")
'''
    print(f"代码:\n{code}")
    print("\n输出:")
    exec(code)
    
    # 3. 批处理示例
    print("\n\n3️⃣ 批处理优化器示例:")
    print("-" * 60)
    code = '''
from repo_seo.batch import BatchOptimizer

# 创建批处理优化器
optimizer = BatchOptimizer(
    provider="local",
    max_repos=5,
    delay=1.0
)

print(f"批处理优化器已创建")
print(f"- Provider: {optimizer.provider}")
print(f"- 最大仓库数: {optimizer.max_repos}")
print(f"- 请求延迟: {optimizer.delay}秒")
'''
    print(f"代码:\n{code}")
    print("\n输出:")
    exec(code)
    
    # 4. Fork同步器示例
    print("\n\n4️⃣ Fork同步器示例:")
    print("-" * 60)
    code = '''
from repo_seo.sync import ForkSynchronizer

# 创建Fork同步器
syncer = ForkSynchronizer()

print(f"Fork同步器已创建")
print(f"- 已同步: {syncer.synced_count}")
print(f"- 失败: {syncer.failed_count}")
print(f"- 跳过: {syncer.skipped_count}")
'''
    print(f"代码:\n{code}")
    print("\n输出:")
    exec(code)

def main():
    """主函数"""
    # 演示CLI使用
    demo_cli_usage()
    
    # 演示Python API使用
    demo_python_usage()
    
    print("\n\n✅ 演示完成！")
    print("\n📚 更多信息:")
    print("- PyPI: https://pypi.org/project/github-repo-seo-optimizer/")
    print("- GitHub: https://github.com/chenxingqiang/repo-seo")
    print("- 文档: https://github.com/chenxingqiang/repo-seo#readme")

if __name__ == "__main__":
    main() 