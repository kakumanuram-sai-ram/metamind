# Using UV for Dependency Management

This project uses `uv` - a fast Python package installer and resolver written in Rust.

## Quick Setup with UV

### Single-line setup:
```bash
cd /home/devuser/sai_dev/metamind && curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH" && uv venv meta_env && source meta_env/bin/activate && uv pip install -r requirements.txt
```

### Step-by-step:

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

2. **Create virtual environment**:
```bash
cd /home/devuser/sai_dev/metamind
uv venv meta_env
```

3. **Activate virtual environment**:
```bash
source meta_env/bin/activate
```

4. **Install dependencies**:
```bash
uv pip install -r requirements.txt
```

## Using UV Commands

### Install a new package:
```bash
uv pip install package-name
```

### Install from requirements.txt:
```bash
uv pip install -r requirements.txt
```

### Update all packages:
```bash
uv pip install --upgrade -r requirements.txt
```

### List installed packages:
```bash
uv pip list
```

### Run Python scripts:
```bash
uv run python api_server.py
```

## Benefits of UV

- ⚡ **Fast**: 10-100x faster than pip
- 🔒 **Reliable**: Better dependency resolution
- 📦 **Modern**: Built with Rust for performance
- 🎯 **Simple**: Drop-in replacement for pip

## Virtual Environment Management

### Create new venv:
```bash
uv venv meta_env
```

### Activate:
```bash
source meta_env/bin/activate
```

### Deactivate:
```bash
deactivate
```

## Project Structure

- `pyproject.toml` - Project metadata and dependencies (optional, for future use)
- `requirements.txt` - Current dependency list
- `meta_env/` - Virtual environment directory

## Troubleshooting

If `uv` command not found:
```bash
export PATH="$HOME/.local/bin:$PATH"
# Or add to ~/.bashrc:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

