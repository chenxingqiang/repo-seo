#!/usr/bin/env python3
import os

def fix_file(filepath):
    """Fix trailing whitespace and ensure single newline at EOF."""
    try:
        # Try UTF-8 first
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            # Try with latin-1 if UTF-8 fails
            with open(filepath, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return

    # Remove trailing whitespace from each line
    lines = [line.rstrip() + '\n' for line in lines]

    # Ensure single newline at EOF
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        lines.append('')

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
    except Exception as e:
        print(f"Error writing {filepath}: {e}")

def main():
    """Fix whitespace issues in all Python and Markdown files."""
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith(('.py', '.md')):
                filepath = os.path.join(root, file)
                fix_file(filepath)
                print(f"Fixed {filepath}")

if __name__ == '__main__':
    main()
