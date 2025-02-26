#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from repo_manager import RepoManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description='Git仓库管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建分支
    branch_parser = subparsers.add_parser('branch', help='分支操作')
    branch_parser.add_argument('name', help='分支名称')
    branch_parser.add_argument('--base', default='main', help='基础分支名称')

    # 提交更改
    commit_parser = subparsers.add_parser('commit', help='提交更改')
    commit_parser.add_argument('message', help='提交信息')
    commit_parser.add_argument('--files', nargs='*', help='要提交的文件列表')

    # 推送更改
    push_parser = subparsers.add_parser('push', help='推送更改')
    push_parser.add_argument('--branch', help='要推送的分支')
    push_parser.add_argument('--force', action='store_true', help='是否强制推送')

    # 同步仓库
    sync_parser = subparsers.add_parser('sync', help='同步仓库')
    sync_parser.add_argument('--branch', help='要同步的分支')

    # 创建标签
    tag_parser = subparsers.add_parser('tag', help='创建标签')
    tag_parser.add_argument('name', help='标签名称')
    tag_parser.add_argument('message', help='标签信息')

    # 查看历史
    history_parser = subparsers.add_parser('history', help='查看提交历史')
    history_parser.add_argument('--count', type=int, default=10, help='显示的提交数量')

    # 查看更改
    changes_parser = subparsers.add_parser('changes', help='查看文件更改')
    changes_parser.add_argument('--commit', help='提交哈希')

    # 合并分支
    merge_parser = subparsers.add_parser('merge', help='合并分支')
    merge_parser.add_argument('source', help='源分支')
    merge_parser.add_argument('--strategy', choices=['merge', 'rebase'], default='merge', help='合并策略')
    merge_parser.add_argument('--squash', action='store_true', help='是否压缩提交')
    merge_parser.add_argument('--abort', action='store_true', help='中止合并')
    merge_parser.add_argument('--resolve', choices=['ours', 'theirs'], help='解决冲突策略')

    # Cherry-pick
    cherry_pick_parser = subparsers.add_parser('cherry-pick', help='Cherry-pick提交')
    cherry_pick_parser.add_argument('commits', nargs='+', help='要cherry-pick的提交哈希列表')

    # 暂存管理
    stash_parser = subparsers.add_parser('stash', help='暂存管理')
    stash_subparsers = stash_parser.add_subparsers(dest='stash_command', help='暂存操作')

    # 创建暂存
    stash_push = stash_subparsers.add_parser('push', help='创建暂存')
    stash_push.add_argument('--name', help='暂存名称')

    # 恢复暂存
    stash_pop = stash_subparsers.add_parser('pop', help='恢复暂存')
    stash_pop.add_argument('--index', type=int, default=0, help='暂存索引')

    # 列出暂存
    stash_list = stash_subparsers.add_parser('list', help='列出暂存')

    # Hooks command
    hooks_parser = subparsers.add_parser('hooks', help='Git hooks management')
    hooks_subparsers = hooks_parser.add_subparsers(dest='hooks_command', help='Hooks commands')

    # List hooks
    hooks_list_parser = hooks_subparsers.add_parser('list', help='List all hooks')

    # Install hook
    hooks_install_parser = hooks_subparsers.add_parser('install', help='Install a hook')
    hooks_install_parser.add_argument('name', help='Hook name')
    hooks_install_parser.add_argument('file', help='Hook script file')

    # Remove hook
    hooks_remove_parser = hooks_subparsers.add_parser('remove', help='Remove a hook')
    hooks_remove_parser.add_argument('name', help='Hook name')

    # Enable hook
    hooks_enable_parser = hooks_subparsers.add_parser('enable', help='Enable a hook')
    hooks_enable_parser.add_argument('name', help='Hook name')

    # Disable hook
    hooks_disable_parser = hooks_subparsers.add_parser('disable', help='Disable a hook')
    hooks_disable_parser.add_argument('name', help='Hook name')

    return parser

def format_changes(changes: dict) -> str:
    """格式化文件更改信息"""
    output = []
    for status, files in changes.items():
        if files:
            output.append(f"\n{status.capitalize()}:")
            for file in files:
                output.append(f"  - {file}")
    return '\n'.join(output) if output else "No changes"

def format_commit_history(commits: List[dict]) -> str:
    """格式化提交历史信息"""
    output = []
    for commit in commits:
        output.append(f"\nCommit: {commit['hash'][:8]}")
        output.append(f"Author: {commit['author']}")
        output.append(f"Date: {commit['date']}")
        output.append(f"Message: {commit['message']}\n")
    return '\n'.join(output) if output else "No commits"

def format_stashes(stashes: List[dict]) -> str:
    """格式化暂存列表信息"""
    output = []
    for stash in stashes:
        output.append(f"\n{stash['ref']} ({stash['hash']})")
        output.append(f"Message: {stash['message']}")
    return '\n'.join(output) if output else "No stashes"

def format_hook_info(hook_name: str, hook_info: Dict[str, Any]) -> str:
    """格式化hook信息为字符串

    Args:
        hook_name: hook名称
        hook_info: hook信息字典

    Returns:
        格式化后的字符串
    """
    status = '✓' if hook_info['enabled'] else '✗'
    size = f"{hook_info['size']} bytes" if hook_info['size'] > 0 else 'N/A'
    modified = hook_info['last_modified'] or 'N/A'

    return (
        f"{status} {hook_name}:\n"
        f"  Exists: {'Yes' if hook_info['exists'] else 'No'}\n"
        f"  Enabled: {'Yes' if hook_info['enabled'] else 'No'}\n"
        f"  Executable: {'Yes' if hook_info['executable'] else 'No'}\n"
        f"  Size: {size}\n"
        f"  Last Modified: {modified}\n"
        f"  Is Sample: {'Yes' if hook_info['is_sample'] else 'No'}"
    )

def handle_hooks_command(args: argparse.Namespace, repo: RepoManager):
    """处理hooks相关命令

    Args:
        args: 命令行参数
        repo: RepoManager实例
    """
    if args.hooks_command == 'list':
        hooks = repo.list_hooks()
        for hook_name, hook_info in hooks.items():
            print(format_hook_info(hook_name, hook_info))
            print()

    elif args.hooks_command == 'install':
        with open(args.file, 'r') as f:
            content = f.read()
        if repo.install_hook(args.name, content):
            print(f"Successfully installed hook: {args.name}")
        else:
            print(f"Failed to install hook: {args.name}")

    elif args.hooks_command == 'remove':
        if repo.remove_hook(args.name):
            print(f"Successfully removed hook: {args.name}")
        else:
            print(f"Failed to remove hook: {args.name}")

    elif args.hooks_command == 'enable':
        if repo.enable_hook(args.name):
            print(f"Successfully enabled hook: {args.name}")
        else:
            print(f"Failed to enable hook: {args.name}")

    elif args.hooks_command == 'disable':
        if repo.disable_hook(args.name):
            print(f"Successfully disabled hook: {args.name}")
        else:
            print(f"Failed to disable hook: {args.name}")

def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        repo_path = os.getcwd()
        with RepoManager(repo_path) as repo:
            if args.command == 'branch':
                success = repo.create_branch(args.name, args.base)
                if not success:
                    sys.exit(1)

            elif args.command == 'commit':
                success = repo.commit_changes(args.message, args.files)
                if not success:
                    sys.exit(1)

            elif args.command == 'push':
                success = repo.push_changes(args.branch, args.force)
                if not success:
                    sys.exit(1)

            elif args.command == 'sync':
                success = repo.sync_with_remote(args.branch)
                if not success:
                    sys.exit(1)

            elif args.command == 'tag':
                success = repo.create_tag(args.name, args.message)
                if not success:
                    sys.exit(1)

            elif args.command == 'history':
                commits = repo.get_commit_history(args.count)
                print(format_commit_history(commits))

            elif args.command == 'changes':
                changes = repo.get_file_changes(args.commit)
                print(format_changes(changes))

            elif args.command == 'merge':
                if args.abort:
                    success = repo.abort_merge()
                elif args.resolve:
                    success = repo.resolve_conflicts(args.resolve)
                else:
                    success = repo.merge_branch(args.source, args.strategy, args.squash)
                if not success:
                    sys.exit(1)

            elif args.command == 'cherry-pick':
                success = repo.cherry_pick(args.commits)
                if not success:
                    sys.exit(1)

            elif args.command == 'stash':
                if args.stash_command == 'push':
                    success = repo.stash_changes(args.name)
                    if not success:
                        sys.exit(1)
                elif args.stash_command == 'pop':
                    success = repo.pop_stash(args.index)
                    if not success:
                        sys.exit(1)
                elif args.stash_command == 'list':
                    stashes = repo.list_stashes()
                    print(format_stashes(stashes))
                else:
                    parser.print_help()

            elif args.command == 'hooks':
                handle_hooks_command(args, repo)

    except Exception as e:
        logger.error(f"执行命令失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
