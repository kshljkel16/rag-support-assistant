"""Step 1 — Load the help-centre articles and split them into chunks.

Test:  pytest tests/test_docs.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Doc:
    doc_id: str      # file name without .md, e.g. "atm-withdrawals"
    title: str       # the first line, without "# "
    text: str        # everything after the title line, stripped


@dataclass(frozen=True)
class Chunk:
    chunk_id: str    # "<doc_id>#<n>", n = 0, 1, 2, ... within the document
    doc_id: str
    title: str
    text: str        # "<title>\n<body>" — the title is repeated in every chunk (see GUIDE)
    n_words: int     # number of words in the BODY only (not the title)


def load_docs(folder: str | Path) -> list[Doc]:
    """Read every *.md file in `folder`, sorted by file name.

    Requirements (tested):
      * doc_id = file name without the extension (Path.stem).
      * The first line must start with "# "; title = that line without "# ", stripped.
        If it doesn't, raise ValueError mentioning the file name.
      * text = the rest of the file, stripped. Read files as UTF-8.
    """
    raise NotImplementedError("Step 1: implement load_docs")


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs: blocks separated by one or more blank lines.

    Requirements (tested): strip each paragraph; drop empty ones; keep the order.
    A table or a bulleted list with no blank lines inside is ONE paragraph.
    Hint: re.split(r"\\n\\s*\\n", text)
    """
    raise NotImplementedError("Step 1: implement split_paragraphs")


def chunk_doc(doc: Doc, max_words: int = 120) -> list[Chunk]:
    """Split one document into chunks of at most `max_words` body words.

    Algorithm (tested):
      1. Go through the paragraphs in order, packing whole paragraphs into the current chunk
         while the chunk stays within max_words. Paragraphs are joined with "\\n\\n".
      2. If the next paragraph doesn't fit, close the current chunk and start a new one.
      3. A single paragraph longer than max_words is cut into pieces of max_words words
         (the last piece may be shorter); each piece becomes its own chunk. Words in these
         pieces are joined with single spaces.
      4. chunk text = f"{doc.title}\\n{body}"; n_words = number of words in body.
      5. chunk_id = f"{doc.doc_id}#{i}" with i counting from 0.
    Never return an empty chunk. Every word of the body appears exactly once, in order.
    """
    raise NotImplementedError("Step 1: implement chunk_doc")


def chunk_docs(docs: list[Doc], max_words: int = 120) -> list[Chunk]:
    """All chunks of all documents, in document order. (Provided.)"""
    return [c for d in docs for c in chunk_doc(d, max_words)]


def load_questions(path: str | Path) -> list[dict]:
    """Read the evaluation set: one JSON object per line. (Provided.)"""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
