#!/usr/bin/env python3
"""
全面测试 github-repo-seo-optimizer 包的所有功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 设置环境变量以避免 protobuf 问题
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_cli_commands():
    """测试所有CLI命令"""
    print("🧪 开始测试 github-repo-seo-optimizer 功能...\n")
    
    tests = []
    
    # 1. 测试版本
    print("1️⃣ 测试版本信息...")
    success, stdout, stderr = run_command("python -m repo_seo.cli --version")
    tests.append({
        "name": "版本信息",
        "success": success,
        "output": stdout.strip() if success else stderr
    })
    
    # 2. 测试 providers 命令
    print("2️⃣ 测试 providers 命令...")
    success, stdout, stderr = run_command("python -m repo_seo.cli providers")
    tests.append({
        "name": "列出LLM提供商",
        "success": success,
        "output": stdout[:100] + "..." if success and len(stdout) > 100 else stdout
    })
    
    # 3. 测试帮助信息
    print("3️⃣ 测试帮助信息...")
    success, stdout, stderr = run_command("python -m repo_seo.cli --help")
    tests.append({
        "name": "主帮助信息",
        "success": success,
        "output": "显示了所有可用命令" if success else stderr
    })
    
    # 4. 测试各个命令的帮助
    commands = ["analyze", "optimize", "batch", "sync"]
    for cmd in commands:
        print(f"4️⃣ 测试 {cmd} --help...")
        success, stdout, stderr = run_command(f"python -m repo_seo.cli {cmd} --help")
        tests.append({
            "name": f"{cmd} 帮助信息",
            "success": success,
            "output": f"显示了 {cmd} 命令的选项" if success else stderr
        })
    
    # 5. 测试模块导入
    print("5️⃣ 测试模块导入...")
    try:
        from repo_seo import __version__, RepoAnalyzer, AIClient
        from repo_seo.batch import BatchOptimizer
        from repo_seo.sync import ForkSynchronizer
        tests.append({
            "name": "模块导入",
            "success": True,
            "output": f"成功导入所有模块，版本: {__version__}"
        })
    except Exception as e:
        tests.append({
            "name": "模块导入",
            "success": False,
            "output": str(e)
        })
    
    # 6. 测试基本功能
    print("6️⃣ 测试基本功能...")
    try:
        from repo_seo.ai_client import AIClient
        # 测试本地provider
        client = AIClient(provider="local")
        result = client.generate_description("Python", ["test.py"], "Test project")
        tests.append({
            "name": "Local Provider 功能",
            "success": True,
            "output": f"生成的描述: {result[:50]}..."
        })
    except Exception as e:
        tests.append({
            "name": "Local Provider 功能",
            "success": False,
            "output": str(e)
        })
    
    return tests

def generate_report(tests):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 测试报告")
    print("="*60 + "\n")
    
    total = len(tests)
    passed = sum(1 for t in tests if t["success"])
    failed = total - passed
    
    # 详细结果
    for i, test in enumerate(tests, 1):
        status = "✅" if test["success"] else "❌"
        print(f"{i}. {status} {test['name']}")
        if not test["success"] or test["name"] == "版本信息":
            print(f"   输出: {test['output']}")
        print()
    
    # 总结
    print("="*60)
    print(f"📈 总结:")
    print(f"   总测试数: {total}")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   成功率: {passed/total*100:.1f}%")
    print("="*60)
    
    # 保存报告
    report = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{passed/total*100:.1f}%",
        "details": tests
    }
    
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n💾 详细报告已保存到 test_report.json")
    
    return passed == total

def main():
    """主函数"""
    print("🚀 GitHub Repository SEO Optimizer 功能验证")
    print("="*60 + "\n")
    
    # 运行测试
    tests = test_cli_commands()
    
    # 生成报告
    all_passed = generate_report(tests)
    
    if all_passed:
        print("\n🎉 所有功能测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分功能测试失败，请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main() 