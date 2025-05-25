#!/bin/bash

# Build documentation for GitHub Repository SEO Optimizer
# Supports both English and Chinese versions

echo "Building GitHub Repository SEO Optimizer Documentation..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the docs directory
if [ ! -f "conf.py" ]; then
    echo -e "${RED}Error: Must run this script from the docs directory${NC}"
    exit 1
fi

# Function to build documentation
build_docs() {
    local lang=$1
    local lang_name=$2
    
    echo -e "${BLUE}Building ${lang_name} documentation...${NC}"
    
    # Clean previous builds
    rm -rf _build/${lang}
    
    # Build HTML documentation
    if [ "$lang" = "en" ]; then
        make html
    else
        make -e SPHINXOPTS="-D language='${lang}'" html
        mv _build/html _build/${lang}
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${lang_name} documentation built successfully${NC}"
    else
        echo -e "${RED}✗ Failed to build ${lang_name} documentation${NC}"
        return 1
    fi
}

# Function to extract translatable strings
extract_strings() {
    echo -e "${BLUE}Extracting translatable strings...${NC}"
    
    # Extract strings to pot files
    make gettext
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Strings extracted successfully${NC}"
    else
        echo -e "${RED}✗ Failed to extract strings${NC}"
        return 1
    fi
}

# Function to update translations
update_translations() {
    local lang=$1
    
    echo -e "${BLUE}Updating ${lang} translations...${NC}"
    
    # Update po files
    sphinx-intl update -p _build/gettext -l ${lang}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${lang} translations updated${NC}"
    else
        echo -e "${RED}✗ Failed to update ${lang} translations${NC}"
        return 1
    fi
}

# Main build process
main() {
    # Parse command line arguments
    BUILD_LANG="all"
    EXTRACT_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --lang)
                BUILD_LANG="$2"
                shift 2
                ;;
            --extract-only)
                EXTRACT_ONLY=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --lang <lang>    Build specific language (en, zh_CN, or all)"
                echo "  --extract-only   Only extract translatable strings"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    # Extract translatable strings
    extract_strings
    
    if [ "$EXTRACT_ONLY" = true ]; then
        echo -e "${GREEN}String extraction complete${NC}"
        exit 0
    fi
    
    # Update translations for Chinese
    if [ "$BUILD_LANG" = "all" ] || [ "$BUILD_LANG" = "zh_CN" ]; then
        update_translations zh_CN
    fi
    
    # Build English documentation
    if [ "$BUILD_LANG" = "all" ] || [ "$BUILD_LANG" = "en" ]; then
        build_docs en "English"
    fi
    
    # Build Chinese documentation
    if [ "$BUILD_LANG" = "all" ] || [ "$BUILD_LANG" = "zh_CN" ]; then
        build_docs zh_CN "Chinese"
    fi
    
    # Create index page for language selection
    if [ "$BUILD_LANG" = "all" ]; then
        echo -e "${BLUE}Creating language selection page...${NC}"
        
        cat > _build/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GitHub Repository SEO Optimizer Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .lang-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
        }
        .lang-button {
            display: inline-block;
            padding: 15px 30px;
            background-color: #2b5797;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
            transition: background-color 0.3s;
        }
        .lang-button:hover {
            background-color: #1e3d6f;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>GitHub Repository SEO Optimizer</h1>
        <p>Select your preferred language / 选择您的语言</p>
        <div class="lang-buttons">
            <a href="html/index.html" class="lang-button">English</a>
            <a href="zh_CN/index.html" class="lang-button">中文</a>
        </div>
    </div>
</body>
</html>
EOF
        
        echo -e "${GREEN}✓ Language selection page created${NC}"
    fi
    
    echo -e "${GREEN}Documentation build complete!${NC}"
    echo -e "${YELLOW}View the documentation:${NC}"
    
    if [ "$BUILD_LANG" = "all" ]; then
        echo -e "  Open ${PWD}/_build/index.html in your browser"
    elif [ "$BUILD_LANG" = "en" ]; then
        echo -e "  Open ${PWD}/_build/html/index.html in your browser"
    else
        echo -e "  Open ${PWD}/_build/${BUILD_LANG}/index.html in your browser"
    fi
}

# Run main function
main "$@" 