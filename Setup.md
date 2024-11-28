# Setup

Here are the commands to create the basic structure:

```bash
mkdir -p mdtk/src/mdtk mdtk/tests
touch mdtk/src/mdtk/__init__.py
touch mdtk/src/mdtk/bookmarks.py
touch mdtk/tests/__init__.py
touch mdtk/pyproject.toml
touch mdtk/README.md
touch mdtk/.gitignore
```

Set GitHub username as environment variable

```sh
export GITHUB_USER=tommcd
```

Move to project directory if not already there

```sh
cd mdtk
```

Initialize git and create repo

```sh
git init
gh repo create $GITHUB_USER/mdtk --public --description "Markdown Toolkit - Tools for working with markdown files"
```

First, let's create a Python-specific `.gitignore`:

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.idea/
.vscode/
EOF
```

Now let's commit and tag:

```bash
git add .
git commit -m "Initial commit: Basic project structure"
git tag -a v0.1.0 -m "Initial release"
git push origin main --tags
```

Would you like me to explain any of these commands before we proceed with the rest of the project setup?