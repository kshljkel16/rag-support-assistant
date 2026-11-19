"""Paths and settings shared by every step."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "data" / "docs"
QUESTIONS_PATH = ROOT / "data" / "eval" / "questions.jsonl"
REPORTS_DIR = ROOT / "reports"

MAX_WORDS = 120      # chunk size in words (Step 1); you will test other values in Step 2
