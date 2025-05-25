#!/usr/bin/env python3
"""
Command Line Interface for GitHub Repository SEO Optimizer
"""

import click
import sys
import os
from pathlib import Path
from typing import Optional

from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="repo-seo")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """GitHub Repository SEO Optimizer - Improve repository discoverability"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--repo-path', '-r', default='.', 
              help='Path to the repository (default: current directory)')
@click.option('--provider', '-p', default='local',
              help='LLM provider to use (local, openai, anthropic, gemini, etc.)')
@click.option('--api-key', '-k', 
              help='API key for the LLM provider')
@click.option('--output', '-o', 
              help='Output file for the optimization results')
@click.option('--dry-run', is_flag=True,
              help='Show what would be done without making changes')
@click.pass_context
def optimize(ctx, repo_path, provider, api_key, output, dry_run):
    """Optimize a single repository for better SEO"""
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"🔍 Analyzing repository: {repo_path}")
        click.echo(f"🤖 Using provider: {provider}")
    
    try:
        # Import here to avoid circular imports
        from .analyzer import RepoAnalyzer
        from .ai_client import AIClient
        
        # Initialize analyzer
        analyzer = RepoAnalyzer(repo_path)
        
        # Initialize AI client if not local provider
        ai_client = None
        if provider != 'local':
            ai_client = AIClient(provider=provider, api_key=api_key)
        
        # Run analysis
        if dry_run:
            click.echo("🧪 Dry run mode - no changes will be made")
            results = analyzer.analyze()
        else:
            results = analyzer.analyze()
            # TODO: Apply optimizations
        
        # Display results
        if verbose:
            click.echo("✅ Analysis completed!")
            click.echo(f"📊 Results: {results}")
        
        # Save output if specified
        if output:
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            click.echo(f"💾 Results saved to: {output}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', 
              help='Configuration file for batch processing')
@click.option('--repos-file', '-f',
              help='File containing list of repositories to process')
@click.option('--provider', '-p', default='local',
              help='LLM provider to use')
@click.option('--max-repos', '-m', type=int,
              help='Maximum number of repositories to process')
@click.option('--delay', '-d', type=float, default=1.0,
              help='Delay between requests (seconds)')
@click.pass_context
def batch(ctx, config, repos_file, provider, max_repos, delay):
    """Batch optimize multiple repositories"""
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo("🚀 Starting batch optimization")
    
    try:
        from .batch import BatchOptimizer
        
        batch_optimizer = BatchOptimizer(
            provider=provider,
            max_repos=max_repos,
            delay=delay
        )
        
        if config:
            results = batch_optimizer.run_from_config(config)
        elif repos_file:
            results = batch_optimizer.run_from_file(repos_file)
        else:
            # Use current user's repositories
            results = batch_optimizer.run_user_repos()
        
        click.echo(f"✅ Batch optimization completed: {len(results)} repositories processed")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--max-repos', '-m', type=int,
              help='Maximum number of forks to sync')
@click.option('--delay', '-d', type=float, default=1.0,
              help='Delay between sync operations (seconds)')
@click.option('--force', is_flag=True,
              help='Force sync even if there are conflicts')
@click.pass_context
def sync(ctx, max_repos, delay, force):
    """Sync all forked repositories with upstream"""
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo("🔄 Starting fork synchronization")
    
    try:
        from .sync import ForkSynchronizer
        
        synchronizer = ForkSynchronizer()
        results = synchronizer.sync_all_forks(
            max_repos=max_repos,
            delay=delay,
            force=force
        )
        
        click.echo(f"✅ Fork synchronization completed: {len(results)} repositories processed")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--repo-path', '-r', default='.',
              help='Path to the repository')
@click.pass_context
def analyze(ctx, repo_path):
    """Analyze repository content and structure"""
    try:
        from .analyzer import RepoAnalyzer
        
        analyzer = RepoAnalyzer(repo_path)
        results = analyzer.analyze()
        
        click.echo("📊 Repository Analysis Results:")
        click.echo(f"Language: {results.get('language', 'Unknown')}")
        click.echo(f"Topics: {', '.join(results.get('topics', []))}")
        click.echo(f"Description: {results.get('description', 'No description')}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def providers():
    """List available LLM providers"""
    providers_info = {
        'local': 'Local rule-based provider (no API key required)',
        'openai': 'OpenAI GPT models (requires API key)',
        'anthropic': 'Anthropic Claude models (requires API key)',
        'gemini': 'Google Gemini models (requires API key)',
        'ollama': 'Local Ollama models (requires Ollama installation)',
        'deepseek': 'DeepSeek models (requires API key)',
        'zhipu': 'ZhiPu models (requires API key)',
        'qianwen': 'QianWen models (requires API key)',
    }
    
    click.echo("🤖 Available LLM Providers:")
    for provider, description in providers_info.items():
        click.echo(f"  • {provider}: {description}")


def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main() 