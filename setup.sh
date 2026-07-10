#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "python3 not found. Install Python 3.9+ first (e.g. 'sudo apt install python3 python3-venv')." >&2
    exit 1
fi

echo "== Creating virtual environment (.venv) =="
python3 -m venv .venv
source .venv/bin/activate

echo "== Installing dependencies =="
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "Done. In future shells, activate with:"
echo "    source .venv/bin/activate"
