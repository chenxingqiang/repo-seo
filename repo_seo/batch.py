#!/usr/bin/env python3
"""
Batch processing module for GitHub Repository SEO Optimizer
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .main import RepositoryOptimizer


class BatchOptimizer:
    """批量仓库优化器"""
    
    def __init__(self, provider: str = 'local', max_repos: Optional[int] = None, 
                 delay: float = 1.0, api_key: Optional[str] = None):
        self.provider = provider
        self.max_repos = max_repos
        self.delay = delay
        self.api_key = api_key
        self.results = []
        self.success_count = 0
        self.failed_count = 0
    
    def get_user_repositories(self) -> List[Dict[str, Any]]:
        """获取用户的所有仓库"""
        try:
            result = subprocess.run([
                'gh', 'repo', 'list', '--json', 
                'name,description,topics,language,url,isPrivate'
            ], capture_output=True, text=True, check=True)
            
            repos = json.loads(result.stdout)
            
            # 过滤掉私有仓库（可选）
            public_repos = [repo for repo in repos if not repo.get('isPrivate', True)]
            
            return public_repos
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get repositories: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse repository data: {e}")
    
    def optimize_repository(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """优化单个仓库"""
        repo_name = repo_info['name']
        
        try:
            # 克隆或使用本地仓库
            repo_path = f"./{repo_name}"
            
            # 如果本地不存在，尝试克隆
            if not Path(repo_path).exists():
                clone_result = subprocess.run([
                    'gh', 'repo', 'clone', repo_name, repo_path
                ], capture_output=True, text=True)
                
                if clone_result.returncode != 0:
                    return {
                        'repo': repo_name,
                        'status': 'failed',
                        'error': f'Failed to clone repository: {clone_result.stderr}',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # 初始化优化器
            optimizer = RepositoryOptimizer(
                repo_path=repo_path,
                provider=self.provider,
                api_key=self.api_key
            )
            
            # 运行优化
            optimization_results = optimizer.optimize()
            
            self.success_count += 1
            
            return {
                'repo': repo_name,
                'status': 'success',
                'results': optimization_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.failed_count += 1
            return {
                'repo': repo_name,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_user_repos(self) -> List[Dict[str, Any]]:
        """批量优化用户的所有仓库"""
        print("🔍 获取用户仓库列表...")
        
        # 获取仓库列表
        repos = self.get_user_repositories()
        
        if self.max_repos:
            repos = repos[:self.max_repos]
        
        print(f"📊 准备优化 {len(repos)} 个仓库")
        
        # 逐个优化
        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']
            print(f"[{i}/{len(repos)}] 🔄 优化 {repo_name}...")
            
            result = self.optimize_repository(repo)
            self.results.append(result)
            
            if result['status'] == 'success':
                print(f"  ✅ {repo_name} 优化成功")
            else:
                print(f"  ❌ {repo_name} 优化失败: {result.get('error', 'Unknown error')}")
            
            # 添加延迟
            if i < len(repos):
                time.sleep(self.delay)
        
        self.generate_report()
        return self.results
    
    def run_from_file(self, repos_file: str) -> List[Dict[str, Any]]:
        """从文件读取仓库列表并批量优化"""
        try:
            with open(repos_file, 'r', encoding='utf-8') as f:
                if repos_file.endswith('.json'):
                    repos_data = json.load(f)
                else:
                    # 假设是文本文件，每行一个仓库名
                    repo_names = [line.strip() for line in f if line.strip()]
                    repos_data = [{'name': name} for name in repo_names]
            
            if self.max_repos:
                repos_data = repos_data[:self.max_repos]
            
            print(f"📊 从文件加载 {len(repos_data)} 个仓库")
            
            # 逐个优化
            for i, repo in enumerate(repos_data, 1):
                repo_name = repo['name']
                print(f"[{i}/{len(repos_data)}] 🔄 优化 {repo_name}...")
                
                result = self.optimize_repository(repo)
                self.results.append(result)
                
                if result['status'] == 'success':
                    print(f"  ✅ {repo_name} 优化成功")
                else:
                    print(f"  ❌ {repo_name} 优化失败: {result.get('error', 'Unknown error')}")
                
                # 添加延迟
                if i < len(repos_data):
                    time.sleep(self.delay)
            
            self.generate_report()
            return self.results
            
        except Exception as e:
            raise Exception(f"Failed to process repositories from file: {e}")
    
    def run_from_config(self, config_file: str) -> List[Dict[str, Any]]:
        """从配置文件运行批量优化"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新配置
            self.provider = config.get('provider', self.provider)
            self.max_repos = config.get('max_repos', self.max_repos)
            self.delay = config.get('delay', self.delay)
            self.api_key = config.get('api_key', self.api_key)
            
            # 获取仓库列表
            if 'repositories' in config:
                repos_data = config['repositories']
            elif 'repos_file' in config:
                return self.run_from_file(config['repos_file'])
            else:
                return self.run_user_repos()
            
            if self.max_repos:
                repos_data = repos_data[:self.max_repos]
            
            print(f"📊 从配置文件加载 {len(repos_data)} 个仓库")
            
            # 逐个优化
            for i, repo in enumerate(repos_data, 1):
                repo_name = repo['name']
                print(f"[{i}/{len(repos_data)}] 🔄 优化 {repo_name}...")
                
                result = self.optimize_repository(repo)
                self.results.append(result)
                
                if result['status'] == 'success':
                    print(f"  ✅ {repo_name} 优化成功")
                else:
                    print(f"  ❌ {repo_name} 优化失败: {result.get('error', 'Unknown error')}")
                
                # 添加延迟
                if i < len(repos_data):
                    time.sleep(self.delay)
            
            self.generate_report()
            return self.results
            
        except Exception as e:
            raise Exception(f"Failed to process config file: {e}")
    
    def generate_report(self) -> None:
        """生成批量优化报告"""
        total = len(self.results)
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 批量优化报告")
        print("="*60)
        print(f"优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总计处理: {total} 个仓库")
        print(f"✅ 优化成功: {self.success_count}")
        print(f"❌ 优化失败: {self.failed_count}")
        print(f"🎯 成功率: {success_rate:.1f}%")
        
        # 保存详细报告
        report_file = f"batch_seo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total': total,
                        'success': self.success_count,
                        'failed': self.failed_count,
                        'success_rate': success_rate,
                        'provider': self.provider
                    },
                    'results': self.results,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"\n⚠️  保存报告失败: {e}")


def main():
    """主函数 - 用于直接运行批处理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch GitHub Repository SEO Optimizer')
    parser.add_argument('--provider', '-p', default='local', help='LLM provider')
    parser.add_argument('--max-repos', '-m', type=int, help='Maximum repositories to process')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Delay between requests')
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--repos-file', '-f', help='File with repository list')
    parser.add_argument('--api-key', '-k', help='API key for LLM provider')
    
    args = parser.parse_args()
    
    batch_optimizer = BatchOptimizer(
        provider=args.provider,
        max_repos=args.max_repos,
        delay=args.delay,
        api_key=args.api_key
    )
    
    try:
        if args.config:
            batch_optimizer.run_from_config(args.config)
        elif args.repos_file:
            batch_optimizer.run_from_file(args.repos_file)
        else:
            batch_optimizer.run_user_repos()
    except Exception as e:
        print(f"❌ 批量优化失败: {e}")


if __name__ == '__main__':
    main() 