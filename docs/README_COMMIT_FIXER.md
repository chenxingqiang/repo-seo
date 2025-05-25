# Conventional Commit Message Fixer

This tool automatically formats your Git commit messages to follow the [Conventional Commits](https://www.conventionalcommits.org/) standard. It helps maintain a consistent commit history and makes it easier to generate change logs.

## Features

- Automatically formats commit messages to follow the conventional format
- Suggests appropriate commit types based on changed files
- Validates branch names to ensure they follow conventions
- Provides helpful guidance when commit messages don't meet standards

## Installation

1. Run the setup script to install the commit message hook:

```bash
python src/setup_commit_hook.py
```

This will:
- Make the commit message fixer script executable
- Install it as a Git commit-msg hook
- Configure it to run automatically when you make commits

## Usage

After installation, simply make commits as usual. The hook will automatically format your commit messages.

### Commit Message Format

Commit messages should follow this format:

```
<type>(<scope>): <description>
```

Where:
- `<type>` is one of the following:
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation changes
  - `style`: Changes that don't affect code meaning (whitespace, formatting)
  - `refactor`: Code changes that neither fix bugs nor add features
  - `perf`: Code changes that improve performance
  - `test`: Adding or correcting tests
  - `build`: Changes to build system or dependencies
  - `ci`: Changes to CI configuration
  - `chore`: Other changes that don't modify src or test files
- `<scope>` is optional and indicates the section of the codebase affected
- `<description>` is a brief description of the change

### Examples

```bash
git commit -m "feat(auth): Add user authentication"
git commit -m "fix: Resolve memory leak"
git commit -m "docs: Update README"
```

### Branch Naming Convention

Branch names should follow this format:

```
<number>-<type>-<description>
```

For example:
```
123-feat-add-new-feature
456-fix-memory-leak
```

## Troubleshooting

If you encounter issues with the commit message fixer:

1. Make sure the script is executable:
   ```bash
   chmod +x src/commit_message_fixer.py
   ```

2. Check that the hook is properly installed:
   ```bash
   ls -la .git/hooks/commit-msg
   ```

3. Run the setup script again:
   ```bash
   python src/setup_commit_hook.py
   ```

4. If you need to bypass the hook temporarily:
   ```bash
   git commit -m "your message" --no-verify
   ``` 