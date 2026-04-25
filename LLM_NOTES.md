# LLM_NOTES.md

## Tools used

- **ChatGPT (GPT-4 class)** — used for scaffolding boilerplate (FastAPI app
  layout, Vite + React starter files), and for sanity-checking the rule-based
  scoring weights I'd already sketched on paper.
- **GitHub Copilot (in editor)** — used for inline autocomplete on small,
  obvious things: `Pydantic` field declarations, repetitive React form
  fields, and JSON shape examples in the README.

I did not use an LLM to design the scoring rules, the API contract, the
test cases, or the validation/error handling — those are my own decisions.

## Where / how I used them

- Asked the LLM for a "minimal FastAPI project layout for a single POST
  endpoint with structured logging," then trimmed and reorganised it to
  match my own preferences (separate `schemas.py`, `scoring.py`,
  `logging_config.py`, custom 422 handler).
- Asked it to remind me of the cleanest way to flatten Pydantic v2's
  `RequestValidationError.errors()` into a `{field, message, type}` list,
  because v2's error shape differs from v1.
- Used Copilot to autocomplete the React form's controlled-input boilerplate.

## What I personally checked, changed, or corrected

- The first FastAPI sketch the LLM produced put scoring logic inline in
  the route handler. I split it out into a pure `compute_score()` function
  in `scoring.py` so it could be unit-tested without the HTTP layer.
- The LLM's initial validation handler returned the raw Pydantic error
  list, which leaks the internal `body.field.x` location prefix. I added
  the `loc[1:]` style flattening so the frontend gets clean field names
  like `land_area_acres` instead of `body.land_area_acres`.
- The LLM proposed `enum` typing for `annual_income_band` using a Python
  `Enum`. I switched to `typing.Literal[...]` because Pydantic v2 produces
  cleaner JSON-schema and error messages with `Literal`, and it avoids the
  `.value` ceremony in the response model.
- The LLM's logger setup used the root logger and `basicConfig`. I replaced
  it with a named, non-propagating logger so it doesn't double-log when
  uvicorn's own logger is configured, and so that pytest captures don't
  conflict.
- I rewrote the LLM-suggested CORS config — it had `allow_credentials=True`
  with `allow_origins=["*"]`, which browsers reject. Removed credentials
  since this app doesn't use them.
- I dropped LLM-suggested `print()` debug lines and replaced them with the
  audit logger.

## Example prompts I used (paraphrased)

1. *"Give me a minimal FastAPI app structure for a single POST endpoint
   that takes 4 fields, validates them with Pydantic v2, and returns a
   UUID, a score, reason codes, and an ISO timestamp."*
2. *"How do I write a custom RequestValidationError handler in FastAPI
   that returns a flat list of `{field, message, type}` per error?"*
3. *"Show me the smallest Vite + React starter (no TypeScript) that
   proxies `/score` to `http://localhost:8000` in dev."*
4. *"What's the cleanest Pydantic v2 way to express an enum field that
   accepts exactly `<2L`, `2-5L`, `5-10L`, `>10L`?"*
5. *"How do I set up a Python `logging` logger that writes JSON lines to
   both stdout and a file, without leaking through to the root logger?"*

## One concrete correction example

The first draft of `scoring.py` the LLM produced returned 4 reason codes
(one per input field, including `crop_type`). The brief specifies
**exactly 3** reason codes. I removed the crop-type code because crop type
isn't actually used in the score in this version — including it as a
"reason" would have been dishonest about what drove the number. I
restructured the function to emit one code per scoring component
(repayment, income, land), which matches both the brief and the actual
scoring math.
