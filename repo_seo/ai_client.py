"""
AI client module for repo-seo tool.
Handles interactions with various AI providers.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union
import re
import logging
from collections import Counter

# Try to import new analyzer framework
try:
    from src.utils.analyzers import AIRepositoryAnalyzer, AIReadmeAnalyzer, AITopicExtractor
    from src.llm_providers import get_provider, BaseProvider
    ANALYZER_FRAMEWORK_AVAILABLE = True
except ImportError:
    ANALYZER_FRAMEWORK_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIClient:
    """Client for interacting with AI providers."""
    
    PROVIDERS = {
        "openai": {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4",
            "env_var": "OPENAI_API_KEY"
        },
        "deepseek": {
            "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            "model": "deepseek-r1-250120",
            "env_var": "DEEPSEEK_API_KEY"
        },
        "claude": {
            "api_url": "https://api.anthropic.com/v1/messages",
            "model": "claude-3-sonnet-20240229",
            "env_var": "ANTHROPIC_API_KEY"
        }
    }
    
    def __init__(self, provider: str = "auto", token: Optional[str] = None):
        """
        Initialize the AI client.
        
        Args:
            provider: AI provider to use (openai, deepseek, claude, auto)
            token: API token for the provider
        """
        self.provider = provider
        
        # Auto-select provider based on available tokens
        if provider == "auto":
            for p, config in self.PROVIDERS.items():
                if token or os.environ.get(config["env_var"]):
                    self.provider = p
                    break
            else:
                # Default to deepseek if no tokens found
                self.provider = "deepseek"
        
        # Store token
        self.token = token or os.environ.get(self.PROVIDERS[self.provider]["env_var"])
        
        # Store API config
        self.api_url = self.PROVIDERS[self.provider]["api_url"]
        self.model = self.PROVIDERS[self.provider]["model"]
        
        # Initialize BaseProvider if framework is available
        self.llm_provider = None
        if ANALYZER_FRAMEWORK_AVAILABLE:
            try:
                self.llm_provider = get_provider(self.provider, api_key=self.token)
            except Exception:
                pass
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1000) -> str:
        """
        Generate text using the selected AI provider.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # 如果我们有框架提供商，优先使用它
        if self.llm_provider and hasattr(self.llm_provider, 'generate_text'):
            try:
                return self.llm_provider.generate_text(prompt, system_prompt, max_tokens)
            except Exception as e:
                logger.warning(f"Framework provider failed: {e}")
                # 继续尝试其他方法
        
        # 尝试可用的提供商
        providers_to_try = [self.provider]  # 首先尝试用户指定的提供商
        # 把其他可用的提供商加入候选列表（确保没有重复）
        for p in self.PROVIDERS.keys():
            if p != self.provider and (self.token or os.environ.get(self.PROVIDERS[p]["env_var"])):
                providers_to_try.append(p)
        
        # 用于记录错误信息，以便最后报告
        errors = {}
        
        # 依次尝试每个提供商
        for provider in providers_to_try:
            try:
                # 根据提供商选择生成方法
                if provider == "openai":
                    return self._generate_openai(prompt, system_prompt, max_tokens)
                elif provider == "deepseek":
                    return self._generate_deepseek(prompt, system_prompt, max_tokens)
                elif provider == "claude":
                    return self._generate_claude(prompt, system_prompt, max_tokens)
            except Exception as e:
                # 记录错误并继续尝试下一个提供商
                logger.warning(f"Provider {provider} failed: {e}")
                errors[provider] = str(e)
                continue  # 尝试下一个提供商
        
        # 如果所有提供商都失败，返回错误信息
        error_str = "; ".join([f"{p}: {e}" for p, e in errors.items()])
        return f"All AI providers failed. Using fallback rule-based analysis. Errors: {error_str}"
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1000) -> str:
        """Generate text using OpenAI API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _generate_deepseek(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1000) -> str:
        """Generate text using Deepseek API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _generate_claude(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1000) -> str:
        """Generate text using Claude API."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.token,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["content"][0]["text"]
    
    def analyze_repository(self, repo_data: Dict) -> Dict:
        """
        Analyze repository using AI.
        
        Args:
            repo_data: Repository data dictionary
            
        Returns:
            Analysis results
        """
        # 如果我们有分析器框架，优先使用它
        if ANALYZER_FRAMEWORK_AVAILABLE and self.llm_provider:
            try:
                analyzer = AIRepositoryAnalyzer(provider_name=self.provider, api_key=self.token)
                return analyzer.analyze(
                    repo_name=repo_data.get("name", ""),
                    description=repo_data.get("description", ""),
                    languages=repo_data.get("languages", []),
                    topics=repo_data.get("topics", []),
                    readme=repo_data.get("readme", "")
                )
            except Exception as e:
                logger.warning(f"Error using AIRepositoryAnalyzer: {e}")
                # 继续尝试其他方法
        
        # 将仓库数据转换为文本提示
        readme = repo_data.get("readme", "")
        description = repo_data.get("description", "")
        name = repo_data.get("name", "")
        topics = repo_data.get("topics", [])
        languages = repo_data.get("languages", [])
        
        # 构建提示
        prompt = f"""
Analyze the following GitHub repository for SEO improvement opportunities:

Repository Name: {name}
Description: {description}
Primary Languages: {', '.join(languages[:3]) if languages else 'Not specified'}
Topics: {', '.join(topics) if topics else 'Not specified'}

README Content:
{readme[:5000] if len(readme) > 5000 else readme}
{'' if len(readme) <= 5000 else '... [README truncated due to length]'}

Provide a comprehensive analysis focusing on:
1. README quality and suggestions
2. Topic recommendations
3. Description improvements
4. Overall SEO score (0-100)

Format your response as JSON with the following structure:
{{
  "readme": {{
    "summary": "Brief summary of README content",
    "issues": ["List of issues with README"],
    "suggestions": ["List of improvement suggestions"],
    "score": 0-100
  }},
  "topics": {{
    "current": ["List of current topics"],
    "suggested": ["List of suggested topics"],
    "score": 0-100
  }},
  "description": {{
    "content": "Current description",
    "suggestions": ["List of improvement suggestions"],
    "score": 0-100
  }},
  "score": 0-100
}}
"""
        
        system_prompt = "You are an expert in GitHub repository SEO optimization. Analyze the repository and provide actionable recommendations."
        
        try:
            # 生成分析
            raw_response = self.generate_text(prompt, system_prompt, max_tokens=2000)
            
            # 检查是否AI生成失败
            if raw_response.startswith("All AI providers failed"):
                # 如果AI失败，降级为基于规则的分析
                return self._fallback_analyze_repository(repo_data)
            
            # 提取JSON
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # 如果JSON解析失败，降级为基于规则的分析
                    return self._fallback_analyze_repository(repo_data)
            
            # 如果未找到有效的JSON，降级为基于规则的分析
            return self._fallback_analyze_repository(repo_data)
            
        except Exception as e:
            logger.warning(f"Error in AI repository analysis: {e}")
            # 降级为基于规则的分析
            return self._fallback_analyze_repository(repo_data)
    
    def _fallback_analyze_repository(self, repo_data: Dict) -> Dict:
        """基于规则的仓库分析备用方法"""
        # 尝试使用规则型分析器
        try:
            if ANALYZER_FRAMEWORK_AVAILABLE:
                from src.utils.analyzers_impl import RuleBasedRepositoryAnalyzer
                analyzer = RuleBasedRepositoryAnalyzer()
                return analyzer.analyze(
                    repo_name=repo_data.get("name", ""),
                    description=repo_data.get("description", ""),
                    languages=repo_data.get("languages", []),
                    topics=repo_data.get("topics", []),
                    readme=repo_data.get("readme", "")
                )
        except (ImportError, Exception) as e:
            logger.warning(f"Error using RuleBasedRepositoryAnalyzer: {e}")
            # 如果使用框架中的分析器失败，回退到基本分析
        
        # 执行基本分析
        readme = repo_data.get("readme", "")
        description = repo_data.get("description", "")
        topics = repo_data.get("topics", [])
        
        # README分析
        readme_analysis = {
            "summary": readme[:200] + "..." if len(readme) > 200 else readme,
            "issues": [],
            "suggestions": [],
            "score": 0
        }
        
        if not readme:
            readme_analysis["issues"].append("README file is missing or empty")
            readme_analysis["suggestions"].append("Create a README file with essential project information")
        else:
            # 简单分析README
            if len(readme) < 500:
                readme_analysis["issues"].append("README is too short")
                readme_analysis["suggestions"].append("Expand your README with more detailed information")
            
            # 寻找标题
            headings = re.findall(r'^(#+)\s+(.+)$', readme, re.MULTILINE)
            if not headings:
                readme_analysis["issues"].append("No headings found in README")
                readme_analysis["suggestions"].append("Add headings (## Heading) to structure your README")
            
            # 计算分数
            readme_analysis["score"] = 100 - (len(readme_analysis["issues"]) * 25)
            readme_analysis["score"] = max(0, min(100, readme_analysis["score"]))
        
        # 主题分析
        topics_analysis = {
            "current": topics,
            "suggested": self._fallback_extract_topics(repo_data, count=5),
            "issues": [],
            "suggestions": [],
            "score": 0
        }
        
        if not topics:
            topics_analysis["issues"].append("No topics defined")
            topics_analysis["suggestions"].append("Add relevant topics to improve discoverability")
        elif len(topics) < 5:
            topics_analysis["issues"].append("Few topics defined (recommended: 5+)")
            topics_analysis["suggestions"].append("Add more relevant topics to improve discoverability")
        
        # 计算分数
        topics_analysis["score"] = 100 - (len(topics_analysis["issues"]) * 25)
        topics_analysis["score"] = max(0, min(100, topics_analysis["score"]))
        
        # 描述分析
        description_analysis = {
            "content": description,
            "suggestions": [],
            "score": 0
        }
        
        if not description:
            description_analysis["suggestions"].append("Add a concise description explaining the purpose of your project")
        elif len(description) < 20:
            description_analysis["suggestions"].append("Expand your description to better explain your project")
        elif len(description) > 250:
            description_analysis["suggestions"].append("Shorten your description to be more concise (< 250 chars)")
        
        # 计算分数
        description_analysis["score"] = 100 - (len(description_analysis["suggestions"]) * 25)
        description_analysis["score"] = max(0, min(100, description_analysis["score"]))
        
        # 整体分析
        result = {
            "readme": readme_analysis,
            "topics": topics_analysis,
            "description": description_analysis,
            "score": (readme_analysis["score"] + topics_analysis["score"] + description_analysis["score"]) / 3
        }
        
        return result
    
    def generate_readme(self, repo_data: Dict) -> str:
        """
        Generate a README for a repository.
        
        Args:
            repo_data: Repository data dictionary
            
        Returns:
            Generated README content
        """
        # 如果我们有框架中的LLM提供商，优先使用它
        if self.llm_provider and hasattr(self.llm_provider, 'generate_readme'):
            try:
                return self.llm_provider.generate_readme(
                    repo_name=repo_data.get("name", ""),
                    languages=repo_data.get("languages", []),
                    topics=repo_data.get("topics", []),
                    description=repo_data.get("description", ""),
                    existing_readme=repo_data.get("readme", "")
                )
            except Exception as e:
                logger.warning(f"Error using LLM provider for README generation: {e}")
                # 继续尝试其他方法
        
        # 构建提示
        name = repo_data.get("name", "")
        description = repo_data.get("description", "")
        topics = repo_data.get("topics", [])
        languages = repo_data.get("languages", [])
        existing_readme = repo_data.get("readme", "")
        
        prompt = f"""
Generate a comprehensive README for the following GitHub repository:

Repository Name: {name}
Description: {description}
Primary Languages: {', '.join(languages[:3]) if languages else 'Not specified'}
Topics: {', '.join(topics) if topics else 'Not specified'}

{'Existing README Content (for reference):' if existing_readme else ''}
{existing_readme[:2000] if existing_readme else ''}
{'' if not existing_readme or len(existing_readme) <= 2000 else '... [existing README truncated due to length]'}

The README should include:
1. Clear title and description
2. Installation instructions
3. Usage examples with code snippets
4. Features list
5. API documentation (if applicable)
6. Contributing guidelines
7. License information
8. Badges for build status, version, etc.

Format the README in Markdown syntax.
"""
        
        system_prompt = "You are an expert in creating excellent documentation for GitHub repositories. Generate a comprehensive, well-structured README that will help users understand and use the repository effectively."
        
        try:
            response = self.generate_text(prompt, system_prompt, max_tokens=4000)
            
            # 检查是否AI生成失败
            if response.startswith("All AI providers failed"):
                # 如果AI失败，降级为基于模板的生成
                return self._fallback_generate_readme(repo_data)
            
            return response
        except Exception as e:
            logger.warning(f"Error generating README: {e}")
            # 降级为基于模板的生成
            return self._fallback_generate_readme(repo_data)
    
    def _fallback_generate_readme(self, repo_data: Dict) -> str:
        """基于模板的README生成备用方法"""
        # 提取基础信息
        name = repo_data.get("name", "Unknown Project")
        description = repo_data.get("description", "No description provided.")
        topics = repo_data.get("topics", [])
        languages = repo_data.get("languages", [])
        
        # 生成基于模板的README
        template = f"""# {name}

{description}

## Features

- [Add key features here]
- Supports {', '.join(languages) if languages else 'multiple languages'}

## Installation

```bash
# Add installation instructions here
```

## Usage

```python
# Add usage example here
```

## API Documentation

[Add API documentation here if applicable]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Keywords

{', '.join(topics) if topics else 'No topics specified yet.'}
"""
        return template
    
    def suggest_topics(self, repo_data: Dict, count: int = 10) -> List[str]:
        """
        Suggest topics for a repository.
        
        Args:
            repo_data: Repository data dictionary
            count: Number of topics to suggest
            
        Returns:
            List of suggested topics
        """
        # 如果我们有LLM提供商，优先使用它
        if self.llm_provider and hasattr(self.llm_provider, 'generate_topics'):
            try:
                return self.llm_provider.generate_topics(
                    repo_name=repo_data.get("name", ""),
                    languages=repo_data.get("languages", []),
                    current_topics=repo_data.get("topics", []),
                    readme=repo_data.get("readme", "")
                )
            except Exception as e:
                logger.warning(f"Error using LLM provider for topic generation: {e}")
                # 继续尝试其他方法
        
        # 如果有主题提取器，尝试使用
        if ANALYZER_FRAMEWORK_AVAILABLE:
            try:
                extractor = AITopicExtractor(provider_name=self.provider, api_key=self.token)
                readme = repo_data.get("readme", "")
                description = repo_data.get("description", "")
                content = f"{description}\n\n{readme}" if description else readme
                return extractor.extract(content)
            except Exception as e:
                logger.warning(f"Error using AITopicExtractor: {e}")
                # 继续尝试其他方法
        
        # 构建提示
        name = repo_data.get("name", "")
        description = repo_data.get("description", "")
        current_topics = repo_data.get("topics", [])
        readme = repo_data.get("readme", "")
        languages = repo_data.get("languages", [])
        
        prompt = f"""
Suggest GitHub topics for the following repository:

Repository Name: {name}
Description: {description}
Primary Languages: {', '.join(languages[:3]) if languages else 'Not specified'}
Current Topics: {', '.join(current_topics) if current_topics else 'None'}

README Content:
{readme[:3000] if len(readme) > 3000 else readme}
{'' if len(readme) <= 3000 else '... [README truncated due to length]'}

Suggest {count} relevant topics for this repository that will improve its discoverability.
Provide only the topic names in a comma-separated list.
Topics should be short (1-3 words), lowercase, and use hyphens instead of spaces (e.g., machine-learning).
"""
        
        system_prompt = "You are an expert in GitHub repository discoverability and SEO. Suggest relevant topics that align with the repository content and will help users find it."
        
        try:
            # 尝试使用AI生成分析
            response = self.generate_text(prompt, system_prompt, max_tokens=500)
            
            # 检查是否AI生成失败
            if response.startswith("All AI providers failed"):
                # 如果AI失败，降级为基于规则的分析
                return self._fallback_extract_topics(repo_data)
            
            # 解析响应
            topics = []
            for line in response.split('\n'):
                # 跳过解释性文本
                if ':' in line or 'topic' in line.lower() or 'suggest' in line.lower():
                    continue
                
                # 从逗号或换行分隔的列表中提取主题
                for topic in re.split(r',|\n', line):
                    topic = topic.strip().lower()
                    
                    # 清理主题
                    topic = re.sub(r'[^\w\s-]', '', topic)  # 移除除连字符外的特殊字符
                    topic = re.sub(r'\s+', '-', topic)      # 将空格替换为连字符
                    
                    if topic and topic not in topics:
                        topics.append(topic)
            
            # 如果成功提取到主题，返回它们
            if topics:
                return topics[:count]
                
            # 如果没有提取到主题，降级到基于规则的分析
            return self._fallback_extract_topics(repo_data)
            
        except Exception as e:
            logger.warning(f"Error generating topics: {e}")
            # 降级到基于规则的分析
            return self._fallback_extract_topics(repo_data)
    
    def _fallback_extract_topics(self, repo_data: Dict, count: int = 10) -> List[str]:
        """基于规则的主题提取备用方法"""
        # 提取基础信息
        readme = repo_data.get("readme", "")
        description = repo_data.get("description", "")
        name = repo_data.get("name", "")
        
        # 合并内容
        content = f"{name}\n{description}\n\n{readme}"
        
        # 创建一个基于规则的主题提取器
        try:
            from src.utils.analyzers_impl import RuleBasedTopicExtractor
            extractor = RuleBasedTopicExtractor()
            return extractor.extract(content)[:count]
        except ImportError:
            # 如果无法导入，使用最基本的提取方法
            topics = []
            
            # 提取单词
            words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', content.lower())
            word_counter = Counter(words)
            
            # 过滤短词和停用词
            stopwords = ["this", "that", "with", "from", "your", "will", "have", "that", "what", "they"]
            relevant_words = [word for word, count in word_counter.most_common(30) 
                            if len(word) > 3 and word not in stopwords]
            
            # 转换为主题格式
            topics = relevant_words[:count]
            
            return topics 