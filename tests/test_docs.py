from pathlib import Path

import pytest

from rag.config import DOCS_DIR, MAX_WORDS, QUESTIONS_PATH
from rag.docs import Doc, chunk_doc, chunk_docs, load_docs, load_questions, split_paragraphs


def words(n, start=0):
    return " ".join(f"w{i}" for i in range(start, start + n))


def test_load_docs(tmp_path: Path):
    (tmp_path / "b-doc.md").write_text("# Second\n\nBody B.\n", encoding="utf-8")
    (tmp_path / "a-doc.md").write_text("# First title  \n\nPara one.\n\nPara two.\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")
    docs = load_docs(tmp_path)
    assert [d.doc_id for d in docs] == ["a-doc", "b-doc"]
    assert docs[0].title == "First title"
    assert docs[0].text == "Para one.\n\nPara two."
    assert not docs[0].text.startswith("#")


def test_load_docs_requires_title(tmp_path: Path):
    (tmp_path / "bad.md").write_text("No title here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bad"):
        load_docs(tmp_path)


def test_split_paragraphs():
    text = "One.\n\n\nTwo line a\nTwo line b\n  \nThree.\n\n"
    assert split_paragraphs(text) == ["One.", "Two line a\nTwo line b", "Three."]


def test_short_doc_is_one_chunk():
    doc = Doc("fees", "Fees", "Para one.\n\nPara two.")
    [c] = chunk_doc(doc, max_words=120)
    assert c.chunk_id == "fees#0" and c.doc_id == "fees" and c.title == "Fees"
    assert c.text == "Fees\nPara one.\n\nPara two."
    assert c.n_words == 4


def test_packs_whole_paragraphs():
    doc = Doc("d", "T", "\n\n".join([words(50, 0), words(50, 50), words(50, 100)]))
    chunks = chunk_doc(doc, max_words=120)
    assert [c.n_words for c in chunks] == [100, 50]
    assert [c.chunk_id for c in chunks] == ["d#0", "d#1"]


def test_long_paragraph_is_cut():
    doc = Doc("d", "T", words(300))
    assert [c.n_words for c in chunk_doc(doc, max_words=120)] == [120, 120, 60]


def test_mixed_and_every_word_once():
    doc = Doc("d", "T", "\n\n".join([words(30, 0), words(200, 30), words(10, 230)]))
    chunks = chunk_doc(doc, max_words=120)
    assert all(0 < c.n_words <= 120 for c in chunks)
    body_words = [w for c in chunks for w in c.text.split("\n", 1)[1].split()]
    assert body_words == [f"w{i}" for i in range(240)]


def test_real_corpus():
    docs = load_docs(DOCS_DIR)
    assert len(docs) == 26
    chunks = chunk_docs(docs, MAX_WORDS)
    assert all(c.n_words <= MAX_WORDS for c in chunks)
    assert len({c.chunk_id for c in chunks}) == len(chunks)


def test_eval_set_points_to_real_docs():          # passes before you write any code
    ids = {p.stem for p in DOCS_DIR.glob("*.md")}
    qs = load_questions(QUESTIONS_PATH)
    assert len({q["id"] for q in qs}) == len(qs)
    for q in qs:
        assert set(q["gold_docs"]) <= ids, q["id"]
        assert q["answerable"] == bool(q["gold_docs"]), q["id"]
