# Dependency Installation Guide: OpenAI Agents SDK Migration

**Feature**: 001-openai-agents-migration
**Date**: 2025-12-25
**Target Environment**: Development and Production
**Python Version**: 3.11+

---

## Overview

This guide provides step-by-step instructions for installing all dependencies required for the OpenAI Agents SDK migration. Follow these steps before modifying any code.

**New Dependencies**:
- `openai-agents>=0.1.0` (OpenAI Agents SDK)

**Existing Dependencies** (unchanged):
- FastAPI, Uvicorn
- Qdrant client
- Sentence-transformers
- Neon Postgres drivers
- All other existing packages

---

## Prerequisites

### System Requirements

**Python Version**: 3.11 or higher (REQUIRED)

```bash
# Check Python version
python --version
# Expected: Python 3.11.x or 3.12.x

# If using pyenv
pyenv install 3.11.7
pyenv local 3.11.7
```

**Pip Version**: 23.0+ recommended

```bash
# Check pip version
pip --version

# Upgrade pip if needed
python -m pip install --upgrade pip
```

**Operating Systems**:
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ macOS (12.0+)
- ✅ Windows 10+ (with WSL2 recommended)

### Environment Setup

**Virtual Environment** (HIGHLY RECOMMENDED):

```bash
# Navigate to project directory
cd backend/rag-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt):
.\venv\Scripts\activate.bat

# Verify activation
which python  # Should point to venv/bin/python
```

---

## Installation Steps

### Step 1: Update requirements.txt

Before installing, ensure `requirements.txt` includes the new dependency:

```bash
cd backend/rag-chatbot

# Check if openai-agents is in requirements.txt
grep "openai-agents" requirements.txt
```

**Expected output**:
```
openai-agents>=0.1.0
```

**If missing**, add it manually:

```bash
# Add to requirements.txt
echo "openai-agents>=0.1.0" >> requirements.txt
```

---

### Step 2: Install All Dependencies

**Standard Installation**:

```bash
# Install all packages from requirements.txt
pip install -r requirements.txt

# Expected output:
# Collecting openai-agents>=0.1.0
#   Downloading openai_agents-0.1.x-py3-none-any.whl
# ...
# Successfully installed openai-agents-0.1.x ...
```

**Development Installation** (includes testing tools):

```bash
# If you have requirements-dev.txt
pip install -r requirements-dev.txt
```

**Installation Time**: ~2-5 minutes (depending on network speed and existing cache)

---

### Step 3: Verify OpenAI Agents SDK Installation

**Quick Verification**:

```bash
# Test import
python -c "from agents import Agent, Runner, set_default_openai_client; print('✅ Agents SDK installed successfully')"
```

**Expected output**:
```
✅ Agents SDK installed successfully
```

**Detailed Verification**:

```python
# Create test file: test_agents_install.py
from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI

# Check version
import agents
print(f"OpenAI Agents SDK version: {agents.__version__}")

# Test agent creation (no API key needed for this test)
test_agent = Agent(
    name="TestAgent",
    model="gpt-4o-mini",  # Dummy model name for testing
    instructions="Test agent",
    tools=[]
)
print(f"✅ Agent created: {test_agent.name}")
print(f"✅ Model: {test_agent.model}")
print("✅ All imports working correctly")
```

```bash
# Run verification script
python test_agents_install.py

# Expected output:
# OpenAI Agents SDK version: 0.1.x
# ✅ Agent created: TestAgent
# ✅ Model: gpt-4o-mini
# ✅ All imports working correctly

# Clean up
rm test_agents_install.py
```

---

### Step 4: Verify Existing Dependencies

Ensure no existing dependencies were broken:

```bash
# Test FastAPI
python -c "from fastapi import FastAPI; print('✅ FastAPI OK')"

# Test Qdrant client
python -c "from qdrant_client import QdrantClient; print('✅ Qdrant OK')"

# Test sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; print('✅ Sentence-transformers OK')"

# Test OpenAI client (used by Agents SDK)
python -c "from openai import AsyncOpenAI; print('✅ OpenAI client OK')"

# Test async support
python -c "import asyncio; print('✅ Asyncio OK')"
```

**Expected**: All checks should print "✅ ... OK"

---

### Step 5: Freeze Dependencies (Optional)

Generate a complete dependency snapshot for reproducibility:

```bash
# Generate frozen requirements
pip freeze > requirements-frozen.txt

# Verify openai-agents is included
grep "openai-agents" requirements-frozen.txt
```

**Expected**:
```
openai-agents==0.1.x
openai==1.x.x
...
```

---

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

**Additional system packages** (if needed for sentence-transformers):

```bash
sudo apt-get update
sudo apt-get install -y python3-dev build-essential

# For GPU support (optional, only if using CUDA)
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### macOS

**Homebrew prerequisites**:

```bash
# Install Python 3.11 if not already installed
brew install python@3.11

# Link Python
brew link python@3.11
```

**Apple Silicon (M1/M2/M3)** considerations:

```bash
# May need to install Rosetta 2 for some packages
# softwareupdate --install-rosetta

# Use native ARM64 builds when available
pip install --upgrade pip setuptools wheel
```

### Windows (WSL2 Recommended)

**Using WSL2 (Ubuntu)**:

```bash
# Inside WSL2 Ubuntu terminal
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Follow Linux instructions above
```

**Native Windows** (not recommended):

```powershell
# Install Python 3.11 from python.org
# Use PowerShell as Administrator

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

---

## Dependency Tree

Understanding the key dependency relationships:

```
openai-agents (0.1.0+)
├── openai (>=1.51.0)  # AsyncOpenAI client used by Agents SDK
│   ├── httpx
│   ├── pydantic
│   └── typing-extensions
├── pydantic (>=2.0.0)  # Data validation
└── typing-extensions

fastapi (existing)
├── starlette
├── pydantic
└── uvicorn (server)

qdrant-client (existing)
├── httpx
├── grpcio (optional)
└── pydantic

sentence-transformers (existing)
├── torch
├── transformers
├── huggingface-hub
└── numpy
```

**Key Compatibility Notes**:
- `openai-agents` requires `openai>=1.51.0` (handles AsyncOpenAI client)
- Pydantic v2+ is shared across FastAPI, Qdrant, and Agents SDK
- No version conflicts expected

---

## Environment Variables

After installing dependencies, configure environment variables:

**Required for Migration**:

```bash
# backend/rag-chatbot/.env

# OpenRouter Configuration (NEW - required)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1

# Existing variables (keep unchanged)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
GOOGLE_API_KEY=your-gemini-api-key  # Kept for rollback
```

**Obtain OpenRouter API Key**:

1. Visit https://openrouter.ai
2. Sign up / Log in
3. Navigate to "Keys" section
4. Create new API key
5. Copy key starting with `sk-or-v1-...`

**Validate Environment Variables**:

```bash
# Check .env file exists
ls -la .env

# Validate required variables are set (without exposing values)
grep -q "OPENROUTER_API_KEY" .env && echo "✅ OPENROUTER_API_KEY set" || echo "❌ Missing"
grep -q "OPENROUTER_MODEL" .env && echo "✅ OPENROUTER_MODEL set" || echo "❌ Missing"
grep -q "BASE_URL" .env && echo "✅ BASE_URL set" || echo "❌ Missing"
```

---

## Testing Installation

### Quick Smoke Test

```bash
# Start server (should not crash on import)
cd backend/rag-chatbot
uvicorn app.main:app --reload --port 8000

# Expected log output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     startup - Starting RAG Chatbot API
# INFO:     agents_sdk_configured - model=mistralai/devstral-2512:free ...
# INFO:     Application startup complete.
```

**If server starts successfully**: ✅ Installation complete

### Integration Test (with OpenRouter API Key)

```python
# test_openrouter_connection.py
import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client
import os

async def test_openrouter():
    # Load API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set")
        return

    # Configure client
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    set_default_openai_client(client)

    # Create test agent
    agent = Agent(
        name="TestAgent",
        model="mistralai/devstral-2512:free",
        instructions="You are a helpful assistant.",
        tools=[]
    )

    # Run simple query
    print("Testing OpenRouter connection...")
    result = await Runner.run(agent=agent, input="Say 'Hello, OpenRouter!'")

    print(f"✅ Response: {result.final_output}")
    print("✅ OpenRouter integration working!")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
```

```bash
# Run test (requires OPENROUTER_API_KEY in environment or .env)
python test_openrouter_connection.py

# Expected output:
# Testing OpenRouter connection...
# ✅ Response: Hello, OpenRouter!
# ✅ OpenRouter integration working!

# Clean up
rm test_openrouter_connection.py
```

---

## Troubleshooting

### Issue: "No module named 'agents'"

**Cause**: Package not installed or wrong package name

**Solution**:
```bash
# Verify package name is "openai-agents" (not "openai-agents-sdk")
pip install openai-agents

# Check installation
pip list | grep openai-agents
```

---

### Issue: "ImportError: cannot import name 'AsyncOpenAI'"

**Cause**: Outdated `openai` package

**Solution**:
```bash
# Upgrade openai package
pip install --upgrade openai

# Verify version (must be >=1.51.0)
pip show openai | grep Version
```

---

### Issue: "ModuleNotFoundError: No module named 'torch'"

**Cause**: sentence-transformers dependency issue (PyTorch not installed)

**Solution**:
```bash
# Install PyTorch (CPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Or reinstall sentence-transformers
pip install --upgrade sentence-transformers
```

---

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause**: SSL certificate issues (common on macOS)

**Solution**:
```bash
# macOS: Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or disable SSL verification (NOT RECOMMENDED for production)
export PYTHONHTTPSVERIFY=0
```

---

### Issue: "pip install" hangs or times out

**Cause**: Network issues or PyPI mirrors

**Solution**:
```bash
# Use alternative PyPI mirror
pip install --index-url https://pypi.org/simple -r requirements.txt

# Or increase timeout
pip install --timeout 120 -r requirements.txt

# Or use pip cache
pip cache info
```

---

### Issue: "Permission denied" errors

**Cause**: Installing without virtual environment or insufficient permissions

**Solution**:
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use --user flag (not recommended)
pip install --user -r requirements.txt
```

---

### Issue: Dependency version conflicts

**Cause**: Incompatible package versions

**Solution**:
```bash
# Check for conflicts
pip check

# If conflicts found, create clean environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use pip's dependency resolver
pip install --upgrade pip
pip install -r requirements.txt --use-feature=2020-resolver
```

---

## Post-Installation Checklist

After completing installation, verify:

- ☐ Python 3.11+ is active (`python --version`)
- ☐ Virtual environment is activated (prompt shows `(venv)`)
- ☐ `openai-agents>=0.1.0` is installed (`pip show openai-agents`)
- ☐ `openai>=1.51.0` is installed (`pip show openai`)
- ☐ All imports work (agents, openai, fastapi, qdrant, sentence_transformers)
- ☐ `.env` file contains OPENROUTER_API_KEY
- ☐ Server starts without import errors (`uvicorn app.main:app`)
- ☐ Logs show "agents_sdk_configured" message

---

## Production Deployment Notes

### Docker (if applicable)

If using Docker, update `Dockerfile`:

```dockerfile
# Ensure Python 3.11+
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies (with build dependencies if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment (Render, Railway, etc.)

Ensure deployment environment:
- Python version: 3.11+
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: OPENROUTER_API_KEY, OPENROUTER_MODEL, BASE_URL

---

## Next Steps

After successful installation:

1. ✅ Dependencies installed
2. ➡️ **Proceed to file modifications** (see `file-modification-checklist.md`)
3. ➡️ Configure OpenRouter client in `app/main.py`
4. ➡️ Update `app/services/llm.py` to use Agents SDK
5. ➡️ Run tests and validate integration

---

## Reference Links

- **OpenAI Agents SDK Docs**: https://github.com/openai/openai-agents-python (if available)
- **OpenRouter Dashboard**: https://openrouter.ai/dashboard
- **PyPI - openai-agents**: https://pypi.org/project/openai-agents/
- **PyPI - openai**: https://pypi.org/project/openai/
- **Python venv docs**: https://docs.python.org/3/library/venv.html

---

**Installation Status**: Ready for code modifications
**Estimated Time**: 10-15 minutes
**Difficulty**: LOW (standard pip install workflow)
