# RAG Support Assistant — build guide

**Goal:** a customer-support assistant for a bank that answers questions **only** from the help
centre, cites the article it used, and says "I don't know" when the help centre doesn't cover the
question. Then measure it honestly, the way you did in your other two projects: against simple
baselines, on retrieval, answer correctness, refusals, cost and latency.

**Why this project for Revolut:** customer support is one of the main places fintech companies use
LLMs. The hard part isn't calling the model. It's making sure it doesn't invent a fee or a limit,
and proving that with numbers.

> The bank, **Orbit**, is fictional. All articles in `data/docs/` were written for this project,
> so you can publish everything. Never copy a real bank's help pages into a public repo.

## The plan

| Step | What you build | What you learn |
|---|---|---|
| 0 | Repo, venv, GitHub | Same setup as before |
| **1** | **Load articles, split them into chunks; add your own eval questions** | Chunking; designing an evaluation set |
| 2 | BM25 keyword retrieval + retrieval metrics (Recall@k, MRR) | How to evaluate retrieval *before* any LLM |
| 3 | Embedding (dense) retrieval + hybrid (reciprocal rank fusion) | When meaning beats keywords, and when it doesn't |
| 4 | Answer generation with Kimi: citations, refusals, JSON output | Grounding; prompt design; parsing |
| 5 | Answer evaluation: key facts, citation accuracy, refusal rate, LLM-as-judge + your own check; closed-book baseline | Measuring hallucination |
| 6 | FastAPI + Docker | Shipping it (you've done this before) |
| 7 | README with results, LinkedIn post | Telling the story |

Commit at the end of every step (and after every meaningful part of a step). Small, honest
commits with clear messages are exactly the GitHub history recruiters like.

---

## Step 0 — Setup (PowerShell, in PyCharm's terminal)

1. On GitHub, create an **empty public** repo named `rag-support-assistant` (no README, no
   .gitignore, no licence — we have our own).
2. Unzip this folder where you keep projects, open it in PyCharm, then:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest -q
```

Expected: **1 passed, 8 failed**. The passing test checks the evaluation set; the 8 failures are
the functions you write in Step 1. That's the starting point.

3. In PyCharm: Settings → Project → Python Interpreter → select `.venv`.
4. Copy `.env` from your first project into this folder (same Moonshot key). Check that `.env` is
   in `.gitignore` — it is.
5. Git:

```powershell
git init
git branch -M main
git add .
git status                      # .env must NOT be listed
git commit -m "Project skeleton: fictional help centre, eval set, Step 1 tests"
git remote add origin https://github.com/kshljkel16/rag-support-assistant.git
git remote -v                   # check it's the right repo
git push -u origin main
```

---

## Step 1 — Documents, chunks and the evaluation set

### Concepts

**What RAG is.** Retrieval-Augmented Generation: instead of asking the LLM from its memory, you
(1) *retrieve* the few help articles relevant to the question, (2) put them in the prompt, and
(3) tell the model to answer only from them. Its knowledge then comes from documents you control
and can update, not from training data that may be wrong or out of date.

**Why chunk.** Retrieval returns pieces of text, not whole files. Pieces that are too big waste
prompt tokens (cost) and mix several topics, so retrieval gets fuzzier. Pieces that are too small
lose context: "£5 on Standard and Plus" means nothing without "replacement card" nearby.
We start with up to 120 words and test other sizes in Step 2. Measured, not guessed.

**Why split by paragraph.** A paragraph is usually one idea. Cutting in the middle of a
sentence or a table separates a number from what it refers to. So we pack *whole* paragraphs,
and cut by words only when a single paragraph is too long.

**Why repeat the title in every chunk.** The second chunk of "My card is lost or stolen" may
never say "card" or "lost". With the title on top, retrieval and the LLM both know what it's
about. This is a cheap, standard trick.

**The evaluation set is the most important file in the project.** `data/eval/questions.jsonl`
has 52 questions. Each line:

```json
{"id": "q008", "question": "...", "answerable": true, "gold_docs": ["atm-withdrawals"],
 "reference_answer": "...", "key_facts": ["£2"]}
```

- `gold_docs`: the article(s) that contain the answer. Step 2 uses them to score retrieval.
- `key_facts`: short strings a correct answer must contain. Step 5 uses them to score answers.
- `answerable: false`: 10 questions the help centre **doesn't** cover (Bitcoin, mortgages, joint
  accounts...). A good assistant must refuse these instead of inventing an answer. Without them
  you can't measure hallucination at all.

Look at the mix: simple lookups ("How much is Plus?"), small calculations ("£30 over the
allowance": 2% is 60p, but the minimum fee is £1), questions that need two articles ("I'm 16"),
and traps where the obvious article is wrong (contactless limit vs Apple Pay).

### Your code: `src/rag/docs.py`

Write three functions. The docstrings give the exact requirements, and the tests check them.
1. `load_docs` — read the `.md` files into `Doc` objects.
2. `split_paragraphs` — one regex.
3. `chunk_doc` — the packing algorithm. Draw it on paper first with the test example:
   paragraphs of 50, 50 and 50 words and max 120 → `[100, 50]`. Why not `[120, 30]`?

```powershell
pytest tests/test_docs.py -q      # goal: 9 passed
```

Then look at the real result:

```powershell
python -c "from rag.docs import *; from rag.config import *; cs = chunk_docs(load_docs(DOCS_DIR)); print(len(cs), 'chunks'); [print(c.chunk_id, c.n_words) for c in cs if c.chunk_id.endswith('#1')]"
```

### Your evaluation questions

Add **8 questions of your own** to the end of `questions.jsonl` (ids `q053`–`q060`):
- 5 answerable. Read an article and write a question a real customer would ask, in their
  words, not the article's. ("My card got eaten by an ATM in Italy" is better than "What is
  the replacement card delivery time internationally?") Fill in `gold_docs`, a short
  `reference_answer` and 1–2 `key_facts`.
- 3 unanswerable, but *close* to something the help centre covers, so they're hard. Example:
  "Can I raise my contactless limit to £200?" looks covered by "Card limits", but the answer
  needs care.

Keep the JSON on one line per question, then run `pytest -q` again: the eval-set test checks
your `gold_docs` exist.

### Write in `notes/step1.md`

1. How many chunks does the corpus give at 120 words? Which documents become 2 chunks, and why?
2. Why does `chunk_doc` close the current chunk instead of splitting a paragraph that doesn't fit?
3. Pick one of your unanswerable questions. What wrong answer might an LLM give, and which
   article would mislead it?
4. Why can't we evaluate a RAG system with only answerable questions?

### Commit

```powershell
pytest -q                       # 9 passed
git add src/rag/docs.py data/eval/questions.jsonl notes/step1.md
git commit -m "Step 1: paragraph-aware chunking and 8 more eval questions"
git push
```

Done when: 9 tests pass, you've added 8 questions, `notes/step1.md` is written, and it's pushed.
Then send me your notes and chunk counts, and we'll start Step 2.
