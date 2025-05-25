#!/bin/bash
# Script to check if the required API keys are set in the environment

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Checking API keys for LLM providers..."
echo "======================================"

# Function to check if an API key is set
check_api_key() {
    local key_name=$1
    local key_value=${!key_name}
    
    if [ -n "$key_value" ]; then
        echo -e "${GREEN}✓${NC} $key_name is set"
        # Check if it looks like a valid key (basic check)
        if [[ ${#key_value} -lt 20 ]]; then
            echo -e "${YELLOW}  Warning: $key_name seems too short to be valid${NC}"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $key_name is not set"
        return 1
    fi
}

# Check OpenAI API key
echo "OpenAI Provider:"
check_api_key "OPENAI_API_KEY"
echo ""

# Check Anthropic API key
echo "Anthropic Provider:"
check_api_key "ANTHROPIC_API_KEY"
echo ""

# Check Google/Gemini API key
echo "Google Gemini Provider:"
if check_api_key "GEMINI_API_KEY" || check_api_key "GOOGLE_API_KEY"; then
    echo -e "${GREEN}  At least one of the required keys is set${NC}"
else
    echo -e "${RED}  Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set${NC}"
fi
echo ""

# Check Groq API key
echo "Groq Provider:"
check_api_key "GROQ_API_KEY"
echo ""

# Check DeepSeek API key
echo "DeepSeek Provider:"
check_api_key "DEEPSEEK_API_KEY"
echo ""

# Check Zhipu API key
echo "Zhipu Provider:"
check_api_key "ZHIPU_API_KEY"
echo ""

# Check Qianwen API key
echo "Qianwen Provider:"
check_api_key "QIANWEN_API_KEY"
echo ""

# Check Ollama
echo "Ollama Provider:"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama is running"
        
        # Check available models
        models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g')
        if [ -n "$models" ]; then
            echo -e "${GREEN}✓${NC} Available models: $models"
        else
            echo -e "${YELLOW}  Warning: No models found. You may need to pull a model:${NC}"
            echo "    ollama pull mistral:latest"
        fi
    else
        echo -e "${RED}✗${NC} Ollama is not running. Start it with: ollama serve"
    fi
else
    echo -e "${RED}✗${NC} Ollama is not installed"
    echo "  Install from: https://ollama.ai/"
fi
echo ""

echo "======================================"
echo "Local provider is always available and requires no API keys."
echo "You can use the local provider with: python repo-seo.py optimize <username> --provider local" 