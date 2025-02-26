#!/usr/bin/env python3
import os
import subprocess
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import shutil

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RepoManager:
    """仓库管理类，处理Git仓库的各种操作"""

    def __init__(self, repo_path: str):
        """初始化仓库管理器

        Args:
            repo_path: 仓库的本地路径
        """
        self.repo_path = os.path.abspath(repo_path)
        self.original_dir = os.getcwd()
        os.chdir(self.repo_path)

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        os.chdir(self.original_dir)

    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """运行Git命令

        Args:
            command: 要运行的命令列表
            check: 是否检查命令执行状态

        Returns:
            命令执行结果
        """
        try:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {' '.join(command)}")
            logger.error(f"错误信息: {e.stderr}")
            raise

    def get_current_branch(self) -> str:
        """获取当前分支名称"""
        result = self.run_command(['git', 'branch', '--show-current'])
        return result.stdout.strip()

    def create_branch(self, branch_name: str, base_branch: str = 'main') -> bool:
        """创建新分支

        Args:
            branch_name: 新分支名称
            base_branch: 基础分支名称

        Returns:
            是否成功创建分支
        """
        try:
            # 切换到基础分支
            self.run_command(['git', 'checkout', base_branch])

            # 如果有远程仓库，尝试同步
            try:
                self.run_command(['git', 'fetch'])
                self.run_command(['git', 'pull'], check=False)  # 忽略pull错误
            except subprocess.CalledProcessError:
                pass  # 忽略远程仓库相关的错误

            # 创建并切换到新分支
            self.run_command(['git', 'checkout', '-b', branch_name])
            logger.info(f"成功创建分支: {branch_name}")
            return True
        except subprocess.CalledProcessError:
            logger.error(f"创建分支失败: {branch_name}")
            return False

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """提交更改

        Args:
            message: 提交信息
            files: 要提交的文件列表，None表示提交所有更改

        Returns:
            是否成功提交
        """
        try:
            if files:
                for file in files:
                    self.run_command(['git', 'add', file])
            else:
                self.run_command(['git', 'add', '.'])

            self.run_command(['git', 'commit', '-m', message])
            logger.info(f"成功提交更改: {message}")
            return True
        except subprocess.CalledProcessError:
            logger.error("提交更改失败")
            return False

    def push_changes(self, branch: Optional[str] = None, force: bool = False) -> bool:
        """推送更改到远程仓库

        Args:
            branch: 要推送的分支，None表示当前分支
            force: 是否强制推送

        Returns:
            是否成功推送
        """
        try:
            current_branch = branch or self.get_current_branch()
            command = ['git', 'push', 'origin', current_branch]
            if force:
                command.append('--force')

            self.run_command(command)
            logger.info(f"成功推送更改到分支: {current_branch}")
            return True
        except subprocess.CalledProcessError:
            logger.error("推送更改失败")
            return False

    def sync_with_remote(self, branch: Optional[str] = None) -> bool:
        """与远程仓库同步

        Args:
            branch: 要同步的分支，None表示当前分支

        Returns:
            是否成功同步
        """
        try:
            current_branch = branch or self.get_current_branch()
            self.run_command(['git', 'fetch'])
            self.run_command(['git', 'checkout', current_branch])
            self.run_command(['git', 'pull', 'origin', current_branch])
            logger.info(f"成功同步分支: {current_branch}")
            return True
        except subprocess.CalledProcessError:
            logger.error("同步失败")
            return False

    def create_tag(self, tag_name: str, message: str) -> bool:
        """创建标签

        Args:
            tag_name: 标签名称
            message: 标签信息

        Returns:
            是否成功创建标签
        """
        try:
            self.run_command(['git', 'tag', '-a', tag_name, '-m', message])
            self.run_command(['git', 'push', 'origin', tag_name])
            logger.info(f"成功创建标签: {tag_name}")
            return True
        except subprocess.CalledProcessError:
            logger.error(f"创建标签失败: {tag_name}")
            return False

    def get_commit_history(self, max_count: int = 10) -> List[Dict[str, str]]:
        """获取提交历史

        Args:
            max_count: 最大提交数量

        Returns:
            提交历史列表
        """
        try:
            format_str = '--format={"hash":"%H","author":"%an","date":"%ad","message":"%s"}'
            result = self.run_command([
                'git', 'log', f'-{max_count}', format_str, '--date=iso'
            ])

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    commits.append(eval(line))  # 安全的字典评估
            return commits
        except subprocess.CalledProcessError:
            logger.error("获取提交历史失败")
            return []

    def get_file_changes(self, commit_hash: Optional[str] = None) -> Dict[str, List[str]]:
        """获取文件更改

        Args:
            commit_hash: 提交哈希，None表示工作区更改

        Returns:
            更改的文件列表，按状态分类
        """
        try:
            changes = {
                'added': [],
                'modified': [],
                'deleted': [],
                'renamed': []
            }

            if commit_hash:
                # 获取特定提交的更改
                result = self.run_command(['git', 'show', '--name-status', commit_hash])
                for line in result.stdout.strip().split('\n'):
                    if not line or '\t' not in line:
                        continue
                    status, *files = line.split('\t')
                    if status.startswith('A'):
                        changes['added'].extend(files)
                    elif status.startswith('M'):
                        changes['modified'].extend(files)
                    elif status.startswith('D'):
                        changes['deleted'].extend(files)
                    elif status.startswith('R'):
                        changes['renamed'].extend(files)
            else:
                # 获取工作区和暂存区的更改
                # 首先获取未跟踪的文件
                result = self.run_command(['git', 'ls-files', '--others', '--exclude-standard'])
                changes['added'].extend(line.strip() for line in result.stdout.strip().split('\n') if line)

                # 然后获取已跟踪文件的更改
                result = self.run_command(['git', 'status', '--porcelain'])
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    status = line[:2].strip()
                    file_path = line[3:].strip()

                    if status.startswith('??'):  # 未跟踪文件已经在上面处理过了
                        continue
                    elif status.startswith('A'):
                        changes['added'].append(file_path)
                    elif status.startswith('M'):
                        changes['modified'].append(file_path)
                    elif status.startswith('D'):
                        changes['deleted'].append(file_path)
                    elif status.startswith('R'):
                        old_path, new_path = file_path.split(' -> ')
                        changes['renamed'].extend([old_path, new_path])

            return changes
        except subprocess.CalledProcessError:
            logger.error("获取文件更改失败")
            return {'added': [], 'modified': [], 'deleted': [], 'renamed': []}

    def merge_branch(self, source_branch: str, strategy: str = 'merge', squash: bool = False) -> bool:
        """合并分支

        Args:
            source_branch: 要合并的源分支
            strategy: 合并策略，可选 'merge' 或 'rebase'
            squash: 是否压缩提交

        Returns:
            是否成功合并
        """
        try:
            current_branch = self.get_current_branch()
            logger.info(f"正在将 {source_branch} 合并到 {current_branch}")

            if strategy == 'rebase':
                # 使用rebase策略
                self.run_command(['git', 'rebase', source_branch])
            else:
                # 使用merge策略
                command = ['git', 'merge', source_branch]
                if squash:
                    command.append('--squash')
                self.run_command(command)

            logger.info(f"成功合并分支: {source_branch}")
            return True
        except subprocess.CalledProcessError:
            logger.error(f"合并分支失败: {source_branch}")
            return False

    def resolve_conflicts(self, strategy: str = 'ours') -> bool:
        """解决合并冲突

        Args:
            strategy: 冲突解决策略，可选 'ours' 或 'theirs'

        Returns:
            是否成功解决冲突
        """
        try:
            # 获取有冲突的文件
            result = self.run_command(['git', 'diff', '--name-only', '--diff-filter=U'])
            conflict_files = result.stdout.strip().split('\n')

            if not conflict_files or conflict_files == ['']:
                logger.info("没有发现冲突")
                return True

            # 解决每个冲突文件
            for file in conflict_files:
                if strategy == 'ours':
                    self.run_command(['git', 'checkout', '--ours', file])
                else:
                    self.run_command(['git', 'checkout', '--theirs', file])
                self.run_command(['git', 'add', file])

            logger.info(f"已使用 {strategy} 策略解决冲突")
            return True
        except subprocess.CalledProcessError:
            logger.error("解决冲突失败")
            return False

    def abort_merge(self) -> bool:
        """中止合并操作

        Returns:
            是否成功中止合并
        """
        try:
            # 检查是否在合并状态
            merge_head = os.path.join(self.repo_path, '.git', 'MERGE_HEAD')
            rebase_dir = os.path.join(self.repo_path, '.git', 'rebase-apply')

            if os.path.exists(merge_head):
                self.run_command(['git', 'merge', '--abort'])
                logger.info("已中止合并操作")
            elif os.path.exists(rebase_dir):
                self.run_command(['git', 'rebase', '--abort'])
                logger.info("已中止变基操作")
            else:
                logger.info("没有正在进行的合并或变基操作")

            return True
        except subprocess.CalledProcessError:
            logger.error("中止操作失败")
            return False

    def cherry_pick(self, commits: List[str]) -> bool:
        """Cherry-pick提交

        Args:
            commits: 要cherry-pick的提交哈希列表

        Returns:
            是否成功cherry-pick
        """
        try:
            for commit in commits:
                self.run_command(['git', 'cherry-pick', commit])
                logger.info(f"成功cherry-pick提交: {commit[:8]}")
            return True
        except subprocess.CalledProcessError:
            logger.error("Cherry-pick失败")
            self.run_command(['git', 'cherry-pick', '--abort'], check=False)
            return False

    def stash_changes(self, name: Optional[str] = None) -> bool:
        """暂存更改

        Args:
            name: 暂存的名称

        Returns:
            是否成功暂存
        """
        try:
            command = ['git', 'stash', 'push', '--include-untracked']
            if name:
                command.extend(['-m', name])
            self.run_command(command)
            logger.info("成功暂存更改")
            return True
        except subprocess.CalledProcessError:
            logger.error("暂存更改失败")
            return False

    def pop_stash(self, index: int = 0) -> bool:
        """恢复暂存的更改

        Args:
            index: 暂存索引

        Returns:
            是否成功恢复暂存
        """
        try:
            self.run_command(['git', 'stash', 'pop', f'stash@{{{index}}}'])
            logger.info("成功恢复暂存的更改")
            return True
        except subprocess.CalledProcessError:
            logger.error("恢复暂存失败")
            return False

    def list_stashes(self) -> List[Dict[str, str]]:
        """列出所有暂存

        Returns:
            暂存列表
        """
        try:
            result = self.run_command(['git', 'stash', 'list', '--format=%gd|%h|%s'])
            stashes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    ref, hash_, message = line.split('|')
                    stashes.append({
                        'ref': ref,
                        'hash': hash_,
                        'message': message
                    })
            return stashes
        except subprocess.CalledProcessError:
            logger.error("获取暂存列表失败")
            return []

    def get_commit_stats(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """获取提交统计信息

        Args:
            since: 起始时间（ISO格式）
            until: 结束时间（ISO格式）

        Returns:
            统计信息字典
        """
        try:
            command = ['git', 'log', '--numstat', '--format="%H|%an|%ae|%ad|%s"']
            if since:
                command.extend(['--since', since])
            if until:
                command.extend(['--until', until])

            result = self.run_command(command)

            stats = {
                'total_commits': 0,
                'total_files': 0,
                'total_additions': 0,
                'total_deletions': 0,
                'authors': {},
                'file_types': {},
                'commit_activity': {}
            }

            current_commit = None
            for line in result.stdout.strip().split('\n'):
                if line.startswith('"'):
                    # 这是一个提交信息行
                    hash_, author, email, date, message = line.strip('"').split('|')
                    current_commit = {
                        'hash': hash_,
                        'author': author,
                        'email': email,
                        'date': date,
                        'message': message
                    }

                    # 更新作者统计
                    if author not in stats['authors']:
                        stats['authors'][author] = {
                            'commits': 0,
                            'additions': 0,
                            'deletions': 0,
                            'files': 0
                        }
                    stats['authors'][author]['commits'] += 1

                    # 更新提交活动统计
                    date_key = date.split()[0]  # 只取日期部分
                    if date_key not in stats['commit_activity']:
                        stats['commit_activity'][date_key] = 0
                    stats['commit_activity'][date_key] += 1

                    stats['total_commits'] += 1

                elif line.strip() and current_commit:
                    # 这是一个文件统计行
                    if line.count('\t') == 2:
                        additions, deletions, file_path = line.split('\t')
                        if additions != '-' and deletions != '-':
                            additions = int(additions)
                            deletions = int(deletions)

                            # 更新总体统计
                            stats['total_files'] += 1
                            stats['total_additions'] += additions
                            stats['total_deletions'] += deletions

                            # 更新作者统计
                            author = current_commit['author']
                            stats['authors'][author]['additions'] += additions
                            stats['authors'][author]['deletions'] += deletions
                            stats['authors'][author]['files'] += 1

                            # 更新文件类型统计
                            file_ext = os.path.splitext(file_path)[1] or 'no_ext'
                            if file_ext not in stats['file_types']:
                                stats['file_types'][file_ext] = {
                                    'files': 0,
                                    'additions': 0,
                                    'deletions': 0
                                }
                            stats['file_types'][file_ext]['files'] += 1
                            stats['file_types'][file_ext]['additions'] += additions
                            stats['file_types'][file_ext]['deletions'] += deletions

            return stats
        except subprocess.CalledProcessError:
            logger.error("获取提交统计失败")
            return {}

    def get_branch_stats(self) -> Dict[str, Any]:
        """获取分支统计信息

        Returns:
            分支统计信息字典
        """
        try:
            stats = {
                'total_branches': 0,
                'active_branches': 0,
                'merged_branches': 0,
                'stale_branches': 0,
                'branches': []
            }

            # 获取所有分支信息
            result = self.run_command([
                'git', 'for-each-ref',
                '--format=%(refname:short)|%(committerdate:iso)|%(authorname)|%(upstream:short)|%(upstream:track)',
                'refs/heads'
            ])

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                branch, date, author, upstream, track = line.split('|')
                branch_info = {
                    'name': branch,
                    'last_commit_date': date,
                    'last_author': author,
                    'upstream': upstream or None,
                    'track_status': track or None,
                    'status': 'active'
                }

                # 检查分支是否已合并
                try:
                    self.run_command(['git', 'merge-base', '--is-ancestor', branch, 'main'])
                    branch_info['merged'] = True
                    stats['merged_branches'] += 1
                except subprocess.CalledProcessError:
                    branch_info['merged'] = False

                # 检查分支是否过时（超过3个月未更新）
                commit_date = datetime.strptime(date.split()[0], '%Y-%m-%d')
                if (datetime.now() - commit_date).days > 90:
                    branch_info['status'] = 'stale'
                    stats['stale_branches'] += 1
                else:
                    stats['active_branches'] += 1

                stats['branches'].append(branch_info)
                stats['total_branches'] += 1

            return stats
        except subprocess.CalledProcessError:
            logger.error("获取分支统计失败")
            return {}

    def get_file_stats(self) -> Dict[str, Any]:
        """获取文件统计信息

        Returns:
            文件统计信息字典
        """
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'largest_files': [],
                'recently_modified': []
            }

            # 获取所有文件列表
            result = self.run_command(['git', 'ls-files'])
            all_files = result.stdout.strip().split('\n')

            # 获取文件大小和修改时间
            for file_path in all_files:
                if not file_path:
                    continue

                full_path = os.path.join(self.repo_path, file_path)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    file_ext = os.path.splitext(file_path)[1] or 'no_ext'

                    # 更新总体统计
                    stats['total_files'] += 1
                    stats['total_size'] += file_size

                    # 更新文件类型统计
                    if file_ext not in stats['file_types']:
                        stats['file_types'][file_ext] = {
                            'count': 0,
                            'total_size': 0
                        }
                    stats['file_types'][file_ext]['count'] += 1
                    stats['file_types'][file_ext]['total_size'] += file_size

                    # 更新最大文件列表
                    stats['largest_files'].append({
                        'path': file_path,
                        'size': file_size
                    })

                    # 获取最后修改时间
                    result = self.run_command(['git', 'log', '-1', '--format=%ad', '--', file_path])
                    last_modified = result.stdout.strip()

                    stats['recently_modified'].append({
                        'path': file_path,
                        'last_modified': last_modified
                    })

            # 排序最大文件列表
            stats['largest_files'].sort(key=lambda x: x['size'], reverse=True)
            stats['largest_files'] = stats['largest_files'][:10]  # 只保留前10个

            # 排序最近修改文件列表
            stats['recently_modified'].sort(key=lambda x: x['last_modified'], reverse=True)
            stats['recently_modified'] = stats['recently_modified'][:10]  # 只保留前10个

            return stats
        except subprocess.CalledProcessError:
            logger.error("获取文件统计失败")
            return {}

    def get_hooks_dir(self) -> str:
        """获取Git hooks目录路径"""
        return os.path.join(self.repo_path, '.git', 'hooks')

    def list_hooks(self) -> Dict[str, Dict[str, Any]]:
        """列出所有Git hooks

        Returns:
            hooks信息字典
        """
        try:
            hooks_dir = self.get_hooks_dir()
            available_hooks = [
                'applypatch-msg', 'pre-applypatch', 'post-applypatch',
                'pre-commit', 'pre-merge-commit', 'prepare-commit-msg',
                'commit-msg', 'post-commit', 'pre-rebase', 'post-checkout',
                'post-merge', 'pre-push', 'pre-receive', 'update',
                'post-receive', 'post-update', 'push-to-checkout',
                'pre-auto-gc', 'post-rewrite', 'sendemail-validate'
            ]

            hooks = {}
            for hook_name in available_hooks:
                hook_path = os.path.join(hooks_dir, hook_name)
                hook_info = {
                    'exists': os.path.exists(hook_path),
                    'enabled': False,
                    'executable': False,
                    'size': 0,
                    'last_modified': None,
                    'is_sample': hook_path.endswith('.sample')
                }

                if hook_info['exists']:
                    hook_info['executable'] = os.access(hook_path, os.X_OK)
                    hook_info['enabled'] = hook_info['executable'] and not hook_info['is_sample']
                    hook_info['size'] = os.path.getsize(hook_path)
                    hook_info['last_modified'] = datetime.fromtimestamp(
                        os.path.getmtime(hook_path)
                    ).isoformat()

                hooks[hook_name] = hook_info

            return hooks
        except Exception as e:
            logger.error(f"获取hooks列表失败: {str(e)}")
            return {}

    def install_hook(self, hook_name: str, content: str) -> bool:
        """安装Git hook

        Args:
            hook_name: hook名称
            content: hook脚本内容

        Returns:
            是否成功安装
        """
        try:
            hooks_dir = self.get_hooks_dir()
            hook_path = os.path.join(hooks_dir, hook_name)

            # 写入hook脚本
            with open(hook_path, 'w') as f:
                f.write(content)

            # 设置可执行权限
            os.chmod(hook_path, 0o755)

            logger.info(f"成功安装hook: {hook_name}")
            return True
        except Exception as e:
            logger.error(f"安装hook失败: {str(e)}")
            return False

    def remove_hook(self, hook_name: str) -> bool:
        """移除Git hook

        Args:
            hook_name: hook名称

        Returns:
            是否成功移除
        """
        try:
            hooks_dir = self.get_hooks_dir()
            hook_path = os.path.join(hooks_dir, hook_name)

            if os.path.exists(hook_path):
                os.remove(hook_path)
                logger.info(f"成功移除hook: {hook_name}")
                return True
            else:
                logger.warning(f"Hook不存在: {hook_name}")
                return False
        except Exception as e:
            logger.error(f"移除hook失败: {str(e)}")
            return False

    def enable_hook(self, hook_name: str) -> bool:
        """启用Git hook

        Args:
            hook_name: hook名称

        Returns:
            是否成功启用
        """
        try:
            hooks_dir = self.get_hooks_dir()
            hook_path = os.path.join(hooks_dir, hook_name)
            sample_path = f"{hook_path}.sample"

            if os.path.exists(sample_path):
                # 如果存在示例hook，复制并启用它
                shutil.copy2(sample_path, hook_path)
                os.chmod(hook_path, 0o755)
                logger.info(f"成功启用hook: {hook_name}")
                return True
            elif os.path.exists(hook_path):
                # 如果hook已存在，只设置可执行权限
                os.chmod(hook_path, 0o755)
                logger.info(f"成功启用hook: {hook_name}")
                return True
            else:
                logger.warning(f"Hook不存在: {hook_name}")
                return False
        except Exception as e:
            logger.error(f"启用hook失败: {str(e)}")
            return False

    def disable_hook(self, hook_name: str) -> bool:
        """禁用Git hook

        Args:
            hook_name: hook名称

        Returns:
            是否成功禁用
        """
        try:
            hooks_dir = self.get_hooks_dir()
            hook_path = os.path.join(hooks_dir, hook_name)

            if os.path.exists(hook_path):
                # 移除可执行权限
                os.chmod(hook_path, 0o644)
                logger.info(f"成功禁用hook: {hook_name}")
                return True
            else:
                logger.warning(f"Hook不存在: {hook_name}")
                return False
        except Exception as e:
            logger.error(f"禁用hook失败: {str(e)}")
            return False
