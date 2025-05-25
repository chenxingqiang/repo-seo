# Sphinx Documentation for GitHub Repository SEO Optimizer

This directory contains the Sphinx-based documentation for the GitHub Repository SEO Optimizer project, supporting both English and Chinese languages.

## Features

- **Multi-language Support**: Documentation available in English and Chinese
- **Auto-generated API Documentation**: Automatically generates API docs from source code
- **Beautiful Theme**: Uses Read the Docs theme (when available) or Alabaster
- **Search Functionality**: Built-in search for easy navigation
- **Cross-references**: Intelligent linking between documentation sections

## Building Documentation

### Prerequisites

```bash
# Install Sphinx and dependencies
pip install sphinx sphinx-intl

# Optional: Install Read the Docs theme for better styling
pip install sphinx-rtd-theme
```

### Build Commands

```bash
# Build all languages
./build_docs.sh

# Build only English documentation
./build_docs.sh --lang en

# Build only Chinese documentation
./build_docs.sh --lang zh_CN

# Extract translatable strings only
./build_docs.sh --extract-only
```

### Manual Build

If you prefer to build manually:

```bash
# Build English version
make html

# Build Chinese version
make -e SPHINXOPTS="-D language='zh_CN'" html

# Clean build files
make clean
```

## Documentation Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── index.rst              # Main documentation index
├── installation.rst       # Installation guide
├── quickstart.rst         # Quick start guide
├── configuration.rst      # Configuration guide
├── guides/                # User guides
│   ├── basic_usage.rst
│   ├── llm_providers.rst
│   ├── batch_processing.rst
│   └── commit_fixer.rst
├── api/                   # API documentation
│   ├── modules.rst
│   ├── llm_providers.rst
│   ├── github_client.rst
│   └── seo_generator.rst
├── development/           # Development docs
│   ├── contributing.rst
│   ├── testing.rst
│   └── architecture.rst
├── locale/                # Translations
│   └── zh_CN/
│       └── LC_MESSAGES/
├── _static/               # Static files (CSS, JS)
│   └── custom.css
├── _templates/            # Custom templates
└── _build/                # Build output
    ├── html/              # English HTML
    └── zh_CN/             # Chinese HTML
```

## Adding New Documentation

### 1. Create a New Document

Create a new `.rst` file in the appropriate directory:

```rst
My New Feature
==============

This document describes my new feature.

Overview
--------

Feature description here...
```

### 2. Add to Table of Contents

Update the relevant `index.rst` or section index to include your new document:

```rst
.. toctree::
   :maxdepth: 2
   
   existing_doc
   my_new_feature
```

### 3. Build and Test

```bash
./build_docs.sh --lang en
# Open _build/html/index.html in browser
```

## Translating Documentation

### 1. Extract Strings

```bash
./build_docs.sh --extract-only
```

### 2. Update Translations

Edit the `.po` files in `locale/zh_CN/LC_MESSAGES/`:

```po
#: ../../index.rst:7
msgid "GitHub Repository SEO Optimizer Documentation"
msgstr "GitHub 仓库 SEO 优化器文档"
```

### 3. Build Translated Version

```bash
./build_docs.sh --lang zh_CN
```

## Writing Documentation

### ReStructuredText Basics

```rst
Title
=====

Subtitle
--------

**Bold text** and *italic text*

Code block::

    def hello():
        print("Hello, World!")

.. code-block:: python

   # Syntax highlighted code
   def hello():
       print("Hello, World!")

* Bullet list item 1
* Bullet list item 2

1. Numbered list item 1
2. Numbered list item 2

`Link text <https://example.com>`_

.. note::
   This is a note admonition.

.. warning::
   This is a warning admonition.
```

### Cross-references

```rst
# Reference another document
See :doc:`installation` for details.

# Reference a section
See :ref:`my-section-label`.

# Reference Python objects
:class:`MyClass`
:func:`my_function`
:mod:`my_module`
```

## Customization

### Theme Options

Edit `conf.py` to customize theme settings:

```python
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}
```

### Custom CSS

Add custom styles in `_static/custom.css`:

```css
/* Custom styles */
.my-custom-class {
    color: #007bff;
}
```

## Deployment

### GitHub Pages

1. Build documentation:
   ```bash
   ./build_docs.sh
   ```

2. Copy to `gh-pages` branch:
   ```bash
   git checkout gh-pages
   cp -r docs/_build/* .
   git add .
   git commit -m "Update documentation"
   git push
   ```

### Read the Docs

1. Connect your repository to Read the Docs
2. Configure `.readthedocs.yml`:
   ```yaml
   version: 2
   sphinx:
     configuration: docs/conf.py
   python:
     install:
       - requirements: docs/requirements.txt
   ```

## Troubleshooting

### Common Issues

**Module not found errors**
- Ensure all dependencies are installed
- Check Python path in `conf.py`

**Theme not loading**
- Install `sphinx-rtd-theme` or remove from `conf.py`

**Build warnings**
- Check for missing documents referenced in toctree
- Ensure all cross-references are valid

**Translation not working**
- Run `sphinx-intl update` after extracting strings
- Check locale directory structure

## Contributing

When contributing documentation:

1. Follow the existing structure and style
2. Use clear, concise language
3. Include code examples where appropriate
4. Test all cross-references
5. Build and review before submitting

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Sphinx Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html) 