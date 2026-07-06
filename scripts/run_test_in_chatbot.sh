#!/usr/bin/env bash
# Run internal API tests in the chatbot conda/venv environment.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Internal API tests (chatbot environment)"
echo "=========================================="
echo ""

if [ -n "${CONDA_DEFAULT_ENV:-}" ]; then
    echo "Conda env: $CONDA_DEFAULT_ENV"
    if [[ "$CONDA_DEFAULT_ENV" == *"chatbot"* ]]; then
        echo "OK: already in chatbot conda env"
    else
        echo "WARN: not chatbot env, trying conda activate chatbot..."
        if command -v conda &> /dev/null; then
            eval "$(conda shell.bash hook)"
            conda activate chatbot 2>/dev/null || {
                echo "ERROR: could not activate chatbot"
                echo "Run: conda activate chatbot"
                exit 1
            }
            echo "OK: activated chatbot"
        fi
    fi
elif [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "Virtual env: $VIRTUAL_ENV"
    if [[ "$VIRTUAL_ENV" != *"chatbot"* ]]; then
        if [ -d "$ROOT/venv_chatbot" ]; then
            # shellcheck disable=SC1091
            source "$ROOT/venv_chatbot/bin/activate"
            echo "OK: activated venv_chatbot"
        else
            echo "WARN: virtual env is not chatbot; continuing anyway"
        fi
    fi
else
    echo "WARN: no virtual env detected"
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
        if conda env list | grep -q chatbot; then
            conda activate chatbot
            echo "OK: activated chatbot conda env"
        else
            echo "ERROR: chatbot conda env not found"
            conda env list
            exit 1
        fi
    else
        echo "ERROR: activate chatbot manually (conda or venv)"
        exit 1
    fi
fi

if [ -n "${CONDA_PREFIX:-}" ]; then
    PYTHON_CMD="$CONDA_PREFIX/bin/python"
else
    PYTHON_CMD="python3"
fi

echo ""
echo "Python:"
"$PYTHON_CMD" --version
"$PYTHON_CMD" -c "import sys; print('executable:', sys.executable)"

echo ""
echo "Installing dependencies..."
"$PYTHON_CMD" -m pip install -q -r "$ROOT/backend/requirements.txt"
"$PYTHON_CMD" -m pip install -q email-validator

echo ""
echo "=========================================="
echo "Running internal API tests"
echo "=========================================="
echo ""

cd "$ROOT"
"$PYTHON_CMD" -m pytest tests/integration/test_internal_api.py -v
