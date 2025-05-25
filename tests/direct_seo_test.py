#!/usr/bin/env python3
"""
直接SEO优化测试脚本
绕过相对导入问题，直接使用GitHub CLI和API
"""

import subprocess
import json
import os
import re
from datetime import datetime

def get_repo_info(owner, repo):
    """获取仓库信息"""
    print(f"🔍 获取仓库 {owner}/{repo} 的信息...")
    
    try:
        # 获取基本信息
        result = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}'], 
                              capture_output=True, text=True, check=True)
        repo_data = json.loads(result.stdout)
        
        # 获取语言统计
        result = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}/languages'], 
                              capture_output=True, text=True, check=True)
        languages = json.loads(result.stdout)
        
        # 获取主题
        result = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}/topics'], 
                              capture_output=True, text=True, check=True)
        topics_data = json.loads(result.stdout)
        topics = topics_data.get('names', [])
        
        # 尝试获取README
        readme_content = ""
        try:
            result = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}/readme'], 
                                  capture_output=True, text=True, check=True)
            readme_data = json.loads(result.stdout)
            if readme_data.get('content'):
                import base64
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
        except:
            print("⚠️ 无法获取README内容")
        
        return {
            'name': repo_data['name'],
            'description': repo_data.get('description', ''),
            'languages': list(languages.keys()),
            'topics': topics,
            'readme': readme_content,
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0),
            'is_fork': repo_data.get('fork', False)
        }
    
    except Exception as e:
        print(f"❌ 获取仓库信息失败: {e}")
        return None

def call_deepseek_api(prompt, api_key):
    """调用DeepSeek API"""
    import requests
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post('https://api.deepseek.com/chat/completions', 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {e}")
        return None

def generate_local_seo_suggestions(repo_info):
    """生成本地SEO建议（基于规则）"""
    name = repo_info['name']
    description = repo_info['description']
    languages = repo_info['languages']
    topics = repo_info['topics']
    readme = repo_info['readme']
    
    # 生成描述
    if not description or len(description) < 20:
        # 基于仓库名和语言生成描述
        lang_str = ', '.join(languages[:3]) if languages else 'Multi-language'
        new_description = f"A {lang_str} project focusing on {name.replace('_', ' ').replace('-', ' ')}"
        
        # 从README中提取关键信息
        if readme:
            readme_lower = readme.lower()
            if 'deep learning' in readme_lower or 'neural network' in readme_lower:
                new_description += " with deep learning capabilities"
            elif 'machine learning' in readme_lower or 'ml' in readme_lower:
                new_description += " with machine learning features"
            elif 'data analysis' in readme_lower or 'analysis' in readme_lower:
                new_description += " for data analysis and processing"
            elif 'web' in readme_lower and 'api' in readme_lower:
                new_description += " for web API development"
    else:
        new_description = description
    
    # 生成主题
    suggested_topics = set(topics)
    
    # 基于语言添加主题
    for lang in languages:
        suggested_topics.add(lang.lower())
    
    # 基于仓库名添加主题
    name_parts = re.split(r'[_\-\s]+', name.lower())
    for part in name_parts:
        if len(part) > 2:
            suggested_topics.add(part)
    
    # 基于描述和README添加主题
    text_content = (description + ' ' + readme).lower()
    
    keywords = [
        'machine-learning', 'deep-learning', 'neural-network', 'ai', 'artificial-intelligence',
        'data-science', 'data-analysis', 'visualization', 'web', 'api', 'framework',
        'library', 'tool', 'cli', 'automation', 'research', 'scientific-computing',
        'materials-science', 'dft', 'quantum', 'chemistry', 'physics'
    ]
    
    for keyword in keywords:
        if keyword.replace('-', ' ') in text_content or keyword.replace('-', '') in text_content:
            suggested_topics.add(keyword)
    
    # 限制主题数量
    final_topics = list(suggested_topics)[:20]
    
    return {
        'new_description': new_description,
        'new_topics': final_topics,
        'reasoning': f"基于仓库名称、语言（{', '.join(languages)}）和内容分析生成"
    }

def generate_deepseek_seo_suggestions(repo_info, api_key):
    """使用DeepSeek生成SEO建议"""
    prompt = f"""
作为GitHub仓库SEO专家，请为以下仓库生成优化建议：

仓库名称: {repo_info['name']}
当前描述: {repo_info['description'] or '无描述'}
编程语言: {', '.join(repo_info['languages']) or '未知'}
当前主题: {', '.join(repo_info['topics']) or '无主题'}
星标数: {repo_info['stars']}
Fork数: {repo_info['forks']}
README内容(前500字符): {repo_info['readme'][:500] if repo_info['readme'] else '无README'}

请提供：
1. 一个简洁且具有吸引力的描述（50-160字符）
2. 5-10个相关的主题标签
3. 简要说明优化理由

请以JSON格式返回：
{{
  "new_description": "优化后的描述",
  "new_topics": ["主题1", "主题2", "主题3"],
  "reasoning": "优化理由说明"
}}
"""
    
    response = call_deepseek_api(prompt, api_key)
    if response:
        try:
            # 提取JSON部分
            import json
            import re
            
            # 查找JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print("⚠️ 无法解析DeepSeek响应中的JSON")
                return None
        except Exception as e:
            print(f"⚠️ 解析DeepSeek响应失败: {e}")
            return None
    return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="直接SEO优化测试")
    parser.add_argument("owner", help="GitHub用户名")
    parser.add_argument("repo", help="仓库名称")
    parser.add_argument("--provider", default="local", choices=["local", "deepseek"], 
                       help="SEO生成提供商")
    parser.add_argument("--apply", action="store_true", help="应用更改到仓库")
    
    args = parser.parse_args()
    
    print(f"🚀 开始SEO优化: {args.owner}/{args.repo}")
    print(f"🔧 使用提供商: {args.provider}")
    print(f"📝 模式: {'应用更改' if args.apply else '预览模式'}")
    print()
    
    # 获取仓库信息
    repo_info = get_repo_info(args.owner, args.repo)
    if not repo_info:
        return
    
    print("📊 当前仓库状态:")
    print(f"  名称: {repo_info['name']}")
    print(f"  描述: {repo_info['description'] or '无描述'}")
    print(f"  语言: {', '.join(repo_info['languages']) or '无'}")
    print(f"  主题: {', '.join(repo_info['topics']) or '无'}")
    print(f"  README: {len(repo_info['readme'])} 字符")
    print(f"  星标: {repo_info['stars']}, Fork: {repo_info['forks']}")
    print()
    
    # 生成SEO建议
    if args.provider == "deepseek":
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            print("❌ 请设置DEEPSEEK_API_KEY环境变量")
            return
        
        print("🤖 使用DeepSeek生成SEO建议...")
        suggestions = generate_deepseek_seo_suggestions(repo_info, api_key)
    else:
        print("🔧 使用本地规则生成SEO建议...")
        suggestions = generate_local_seo_suggestions(repo_info)
    
    if not suggestions:
        print("❌ 无法生成SEO建议")
        return
    
    print("💡 SEO优化建议:")
    print(f"  新描述: {suggestions['new_description']}")
    print(f"  新主题: {', '.join(suggestions['new_topics'])}")
    print(f"  理由: {suggestions['reasoning']}")
    print()
    
    # 分析变化
    changes = {}
    if suggestions['new_description'] != repo_info['description']:
        changes['description'] = True
    if set(suggestions['new_topics']) != set(repo_info['topics']):
        changes['topics'] = True
    
    if changes:
        print("🔄 检测到的变化:")
        if changes.get('description'):
            print(f"  描述: '{repo_info['description']}' → '{suggestions['new_description']}'")
        if changes.get('topics'):
            print(f"  主题: {repo_info['topics']} → {suggestions['new_topics']}")
        
        if args.apply:
            print("\n🚀 正在应用更改...")
            
            # 构建API调用
            update_data = {}
            if changes.get('description'):
                update_data['description'] = suggestions['new_description']
            
            try:
                # 更新仓库基本信息
                if update_data:
                    cmd = ['gh', 'api', f'repos/{args.owner}/{args.repo}', '--method', 'PATCH']
                    for key, value in update_data.items():
                        cmd.extend(['-f', f'{key}={value}'])
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    print("✅ 成功更新仓库描述")
                
                # 更新主题
                if changes.get('topics'):
                    topics_data = {'names': suggestions['new_topics']}
                    cmd = ['gh', 'api', f'repos/{args.owner}/{args.repo}/topics', '--method', 'PUT',
                           '--input', '-']
                    
                    result = subprocess.run(cmd, input=json.dumps(topics_data), 
                                          capture_output=True, text=True, check=True)
                    print("✅ 成功更新仓库主题")
                
                print("\n🎉 SEO优化完成！")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ 应用更改失败: {e}")
                print(f"错误输出: {e.stderr}")
        else:
            print("\n💭 这是预览模式，使用 --apply 参数来应用更改")
    else:
        print("✨ 当前配置已经很好，无需更改！")
    
    # 保存结果
    result = {
        'repository': f"{args.owner}/{args.repo}",
        'timestamp': datetime.now().isoformat(),
        'provider': args.provider,
        'current_info': repo_info,
        'suggestions': suggestions,
        'changes_detected': changes,
        'applied': args.apply if changes else False
    }
    
    output_file = f"seo_result_{args.owner}_{args.repo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 结果已保存到: {output_file}")

if __name__ == "__main__":
    main() 