#!/usr/bin/env python3
"""
Fork synchronization module for GitHub Repository SEO Optimizer
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional


class ForkSynchronizer:
    """Fork项目同步器"""
    
    def __init__(self):
        self.synced_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.results = []
    
    def get_user_forks(self) -> List[Dict[str, Any]]:
        """获取用户的所有fork项目"""
        print("🔍 获取用户的fork项目列表...")
        
        try:
            # 使用GitHub CLI获取所有仓库
            result = subprocess.run([
                'gh', 'repo', 'list', '--json', 
                'name,isFork,parent,defaultBranchRef,pushedAt,url'
            ], capture_output=True, text=True, check=True)
            
            all_repos = json.loads(result.stdout)
            
            # 筛选出fork项目
            forks = [repo for repo in all_repos if repo.get('isFork', False)]
            
            print(f"✅ 找到 {len(forks)} 个fork项目")
            return forks
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 获取fork列表失败: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ 解析JSON失败: {e}")
            return []
    
    def sync_fork(self, repo_name: str, default_branch: str = 'main', force: bool = False) -> Dict[str, Any]:
        """同步单个fork项目"""
        print(f"🔄 同步 {repo_name}...")
        
        result = {
            'repo': repo_name,
            'status': 'unknown',
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 构建同步命令
            sync_cmd = ['gh', 'repo', 'sync', repo_name]
            if force:
                sync_cmd.append('--force')
            
            # 方法1: 使用GitHub CLI的sync命令
            sync_result = subprocess.run(sync_cmd, capture_output=True, text=True)
            
            if sync_result.returncode == 0:
                result['status'] = 'success'
                result['message'] = 'Successfully synced with upstream'
                self.synced_count += 1
                print(f"  ✅ {repo_name} 同步成功")
                return result
            
            # 检查是否已经是最新的
            if 'already up to date' in sync_result.stderr.lower() or 'up-to-date' in sync_result.stderr.lower():
                result['status'] = 'up_to_date'
                result['message'] = 'Already up to date'
                self.skipped_count += 1
                print(f"  ℹ️  {repo_name} 已经是最新的")
                return result
            
            # 如果普通同步失败，尝试强制同步
            if not force and 'diverged' in sync_result.stderr.lower():
                print(f"  ⚠️  {repo_name} 存在分歧更改，尝试强制同步...")
                return self.sync_fork(repo_name, default_branch, force=True)
            
            # 其他失败情况
            result['status'] = 'failed'
            result['message'] = f'Sync failed: {sync_result.stderr}'
            self.failed_count += 1
            print(f"  ❌ {repo_name} 同步失败: {sync_result.stderr[:100]}...")
            
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)
            self.failed_count += 1
            print(f"  ❌ {repo_name} 同步出错: {e}")
        
        return result
    
    def sync_all_forks(self, max_repos: Optional[int] = None, delay: float = 1.0, 
                      force: bool = False) -> List[Dict[str, Any]]:
        """同步所有fork项目"""
        print("🚀 开始同步所有fork项目")
        print("="*60)
        
        # 获取fork列表
        forks = self.get_user_forks()
        
        if not forks:
            print("❌ 没有找到fork项目")
            return []
        
        # 限制处理数量（如果指定）
        if max_repos:
            forks = forks[:max_repos]
            print(f"ℹ️  限制处理前 {max_repos} 个项目")
        
        print(f"📊 准备同步 {len(forks)} 个fork项目")
        print()
        
        # 逐个同步
        for i, fork in enumerate(forks, 1):
            repo_name = fork['name']
            default_branch = fork.get('defaultBranchRef', {}).get('name', 'main')
            
            print(f"[{i}/{len(forks)}] 处理: {repo_name}")
            
            # 同步fork
            result = self.sync_fork(repo_name, default_branch, force)
            self.results.append(result)
            
            # 添加延迟避免API限制
            if i < len(forks):
                time.sleep(delay)
        
        return self.results
    
    def generate_report(self) -> None:
        """生成同步报告"""
        print("\n" + "="*60)
        print("📊 Fork同步报告")
        print("="*60)
        print(f"同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total = len(self.results)
        print(f"总计处理: {total} 个fork项目")
        print(f"✅ 同步成功: {self.synced_count}")
        print(f"ℹ️  已是最新: {self.skipped_count}")
        print(f"❌ 同步失败: {self.failed_count}")
        print()
        
        # 成功率
        if total > 0:
            success_rate = ((self.synced_count + self.skipped_count) / total) * 100
            print(f"🎯 成功率: {success_rate:.1f}%")
        
        # 详细结果
        if self.failed_count > 0:
            print("\n❌ 失败的项目:")
            for result in self.results:
                if result['status'] in ['failed', 'error']:
                    print(f"  - {result['repo']}: {result['message'][:100]}...")
        
        # 保存详细报告
        report_file = f"fork_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total': total,
                        'synced': self.synced_count,
                        'up_to_date': self.skipped_count,
                        'failed': self.failed_count,
                        'success_rate': success_rate if total > 0 else 0
                    },
                    'results': self.results,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"\n⚠️  保存报告失败: {e}")


def main():
    """主函数 - 用于直接运行同步"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Fork Synchronizer')
    parser.add_argument('--max-repos', '-m', type=int, help='Maximum forks to sync')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Delay between syncs')
    parser.add_argument('--force', '-f', action='store_true', help='Force sync even with conflicts')
    
    args = parser.parse_args()
    
    print("🔄 GitHub Fork项目同步工具")
    print("="*60)
    
    # 检查GitHub CLI
    try:
        result = subprocess.run(['gh', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ GitHub CLI: {result.stdout.strip().split()[2]}")
    except Exception:
        print("❌ GitHub CLI未安装或不可用")
        sys.exit(1)
    
    # 检查认证
    try:
        subprocess.run(['gh', 'auth', 'status'], 
                      capture_output=True, text=True, check=True)
        print("✅ GitHub认证: 已认证")
    except Exception:
        print("❌ GitHub未认证，请先运行: gh auth login")
        sys.exit(1)
    
    print()
    
    # 创建同步器
    synchronizer = ForkSynchronizer()
    
    try:
        # 开始同步
        synchronizer.sync_all_forks(
            max_repos=args.max_repos,
            delay=args.delay,
            force=args.force
        )
        
        # 生成报告
        synchronizer.generate_report()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        synchronizer.generate_report()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 