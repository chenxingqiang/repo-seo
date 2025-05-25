#!/usr/bin/env python3
"""
测试GitHub连接和核心功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_github_connection():
    """测试GitHub连接"""
    try:
        # 导入模块
        from github_client import GitHubCliClient
        from seo_generator import SEOGenerator
        
        # 创建GitHub客户端
        github = GitHubCliClient()
        
        # 测试获取用户仓库
        username = 'chenxingqiang'
        logger.info(f"正在获取用户 {username} 的仓库...")
        
        repos = github.get_user_repositories(username)
        logger.info(f"成功获取到 {len(repos)} 个仓库")
        
        # 显示前5个仓库
        print("\n前5个仓库:")
        for i, repo in enumerate(repos[:5]):
            print(f"{i+1}. {repo['name']}")
            print(f"   描述: {repo.get('description', '无描述')}")
            print(f"   语言: {repo.get('language', '未知')}")
            print(f"   是否为Fork: {repo.get('fork', False)}")
            print()
        
        # 测试获取单个仓库详细信息
        if repos:
            test_repo = repos[0]['name']
            logger.info(f"正在获取仓库 {test_repo} 的详细信息...")
            
            repo_details = github.get_repository(username, test_repo)
            if repo_details:
                print(f"\n仓库 {test_repo} 详细信息:")
                print(f"- 描述: {repo_details.get('description', '无描述')}")
                print(f"- 星标数: {repo_details.get('stargazers_count', 0)}")
                print(f"- Fork数: {repo_details.get('forks_count', 0)}")
                print(f"- 主要语言: {repo_details.get('language', '未知')}")
                
                # 获取语言统计
                languages = github.get_repository_languages(username, test_repo)
                print(f"- 语言统计: {list(languages.keys())}")
                
                # 获取主题
                topics = github.get_repository_topics(username, test_repo)
                print(f"- 主题: {topics}")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_providers():
    """测试LLM提供商"""
    try:
        from llm_providers import list_available_providers
        
        providers = list_available_providers()
        print("\n可用的LLM提供商:")
        for name, info in providers.items():
            status = "✓" if info['available'] else "✗"
            print(f"{status} {name}")
            if not info['available'] and 'error' in info:
                print(f"   错误: {info['error']}")
        
        return True
        
    except Exception as e:
        logger.error(f"LLM提供商测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_seo_generation():
    """测试SEO生成功能"""
    try:
        from seo_generator import SEOGenerator
        
        # 使用本地提供商测试
        generator = SEOGenerator(provider_name='local')
        
        # 测试描述生成
        description = generator.generate_description(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            topics=["web", "api"],
            readme="This is a test repository for web API development."
        )
        
        print(f"\n生成的描述: {description}")
        
        # 测试主题生成
        topics = generator.generate_topics(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            current_topics=["web"],
            readme="This is a test repository for web API development."
        )
        
        print(f"生成的主题: {topics}")
        
        return True
        
    except Exception as e:
        logger.error(f"SEO生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== GitHub Repository SEO Optimizer 功能测试 ===\n")
    
    # 测试GitHub连接
    print("1. 测试GitHub连接...")
    github_ok = test_github_connection()
    
    # 测试LLM提供商
    print("\n2. 测试LLM提供商...")
    llm_ok = test_llm_providers()
    
    # 测试SEO生成
    print("\n3. 测试SEO生成功能...")
    seo_ok = test_seo_generation()
    
    # 总结
    print("\n=== 测试结果 ===")
    print(f"GitHub连接: {'✓' if github_ok else '✗'}")
    print(f"LLM提供商: {'✓' if llm_ok else '✗'}")
    print(f"SEO生成: {'✓' if seo_ok else '✗'}")
    
    if all([github_ok, llm_ok, seo_ok]):
        print("\n🎉 所有核心功能测试通过！")
    else:
        print("\n⚠️ 部分功能存在问题，需要进一步检查。") 