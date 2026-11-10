# -*- coding: utf-8 -*-
"""Điểm vào cho Vercel (Python serverless): dùng lại ứng dụng FastAPI trong app.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402,F401
