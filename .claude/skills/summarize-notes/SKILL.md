---
name: summarize-notes
description: Turn pasted lecture notes, readings, or slide text into a structured study summary (key points, definitions, likely exam questions). Use when the user pastes raw notes or text and asks for a summary, study guide, or to "make this easier to review."
---

# Summarize notes

Given raw notes, slide text, or reading material pasted by the user:

1. Identify the core topic and structure — reorganize around concepts, don't just compress sentence-by-sentence.
2. Produce:
   - **Key points** — 5-10 bullets: the ideas that actually matter for understanding the material, not every fact mentioned.
   - **Definitions** — any term a student would need to know, explained in plain language.
   - **Likely exam questions** — 3-5 questions this material could plausibly be tested on, to prompt active recall.
3. Keep the summary meaningfully shorter than the source — if it's nearly as long as the original, cut harder.
4. If the pasted material is clearly incomplete or garbled (e.g. a partial OCR dump), say so rather than confidently summarizing the gaps.
