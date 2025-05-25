# Documentation for GitHub Repository SEO Optimizer

This directory contains documentation for the GitHub Repository SEO Optimizer project.

## Documentation Systems

We provide two documentation systems:

1. **Markdown Documentation** - Simple, readable documentation files
2. **Sphinx Documentation** - Professional documentation with multi-language support (English and Chinese)

## Sphinx Documentation

### Features

- Professional HTML documentation with search functionality
- Multi-language support (English and Chinese)
- Auto-generated API documentation
- Beautiful themes and responsive design
- Cross-references and intelligent linking

### Building Sphinx Documentation

```bash
# Install dependencies
pip install sphinx sphinx-intl

# Build all languages
cd docs
./build_docs.sh

# Build English only
./build_docs.sh --lang en

# Build Chinese only
./build_docs.sh --lang zh_CN
```

### Viewing Documentation

After building, open `docs/_build/html/index.html` in your browser.

For detailed Sphinx documentation instructions, see [README_SPHINX.md](./README_SPHINX.md).

## Markdown Documentation

### Core Documentation

- [**index.md**](./index.md): Main documentation index and API overview
- [**main_script.md**](./main_script.md): Documentation for the main script functionality
- [**llm_providers.md**](./llm_providers.md): Information about supported LLM providers and their configuration

### Feature Documentation

- [**README_COMMIT_FIXER.md**](./README_COMMIT_FIXER.md): Documentation for the commit message fixer tool
- [**topic_validation.md**](./topic_validation.md): Information about topic validation and best practices
- [**target.md**](./target.md): Documentation about targeting specific repositories

### Development Documentation

- [**commit-timeline-info.md**](./commit-timeline-info.md): Information about commit history and timeline

## Contributing to Documentation

When adding new documentation:

1. Create a new Markdown file in this directory
2. Add a link to the new file in this README
3. Follow the existing documentation style and format
4. Include examples where appropriate
5. Update the main README.md if necessary
6. For Sphinx docs, create corresponding `.rst` files

## Documentation Style Guide

### For Markdown

- Use Markdown for all documentation
- Use H1 (`#`) for the document title
- Use H2 (`##`) for major sections
- Use H3 (`###`) for subsections
- Use code blocks with language specifiers for code examples
- Include a table of contents for longer documents
- Use relative links to reference other documentation files

### For Sphinx (reStructuredText)

- Use `.rst` extension for files
- Follow reStructuredText syntax
- Use proper heading hierarchy with underlines
- Include cross-references using `:doc:` and `:ref:`
- Add files to appropriate `toctree` directives

## Documentation TODOs

- [x] Add Sphinx documentation support
- [x] Add multi-language support (English and Chinese)
- [ ] Complete API documentation
- [ ] Add more examples and use cases
- [ ] Create comprehensive troubleshooting guide
- [ ] Add architecture diagrams
- [ ] Set up automatic documentation deployment 