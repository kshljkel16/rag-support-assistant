# Step 1 notes

## 1. Chunks at 120 words

The corpus gives **28 chunks** from 26 articles. Two articles need a second chunk:

- `plans-overview#1` (14 words): the plans table has no blank lines, so it is one paragraph.
  `split()` splits on spaces, so table symbols like `|` and `£0` each count as a word, which
  makes the table large. Together with the next paragraph it reaches 120, so the last
  paragraph (annual billing) moves to a new chunk.
- `lost-stolen-card#1` (16 words): the article is just over 120 words, so its last paragraph
  ("If you see payments you don't recognise...") moves to chunk #1.

These tiny second chunks show a weakness of the 120-word setting: a 14-word chunk carries very
little context. This is one reason to test other chunk sizes in Step 2. It's also why the title
is repeated in every chunk: on its own, `lost-stolen-card#1` never mentions a card.

## 2. Why close the chunk instead of splitting the paragraph

A paragraph is usually one idea, and its facts depend on each other. If the replacement-card
paragraph were cut in the middle, one half could say "after that, a replacement costs £5 on
Standard and Plus" while the "first replacement in any 12 months is free" part sat in another
chunk. Retrieval might return only one half, and the answer would be wrong. So whole paragraphs
are moved to the next chunk; a paragraph is cut by words only when it is too long to fit even in
an empty chunk.

## 3. An unanswerable question that could mislead the LLM

q059: "I received 10k yuan and it wasn't mine, can I send it back?" The help centre never covers
money received by mistake. But "Sending money within the UK" says transfers usually can't be
reversed, and "Exchanging money" talks about holding currencies, so an LLM could confidently
answer "No, transfers can't be reversed" or give exchange instructions. Both would be invented.
The correct behaviour is to say the help centre doesn't cover this and suggest contacting support.

## 4. Why we need unanswerable questions

With only answerable questions, an assistant that always answers confidently, even by making
things up, could still score very well. We would never see that it invents fees, limits or rules,
which for a bank means telling real customers wrong information. Unanswerable questions are the
only way to measure whether it says "I don't know" when the documents don't contain the answer,
that is, to measure hallucination.