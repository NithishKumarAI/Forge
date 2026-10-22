# Forge agent guide

Forge V1 is intentionally small and local-first. Prefer simple, readable code and avoid unnecessary dependencies or infrastructure.

- Treat the active confirmed curriculum as authoritative. AI must never silently change it.
- Confirmed curricula are structurally immutable; edits require a new draft/version.
- Mastery comes from evidence, never chat usage; doubt chat never changes mastery.
- Use structured output for machine-readable AI responses and validate it on the backend.
- Never make live provider calls in automated tests; inject a fake provider.
- Coding correctness relies primarily on deterministic tests, not LLM opinion.
- Completed practice attempts append evidence; pending evaluations do not count. Never mutate or delete historical evidence to manufacture a score.
- Mastery, confidence, readiness, mistakes, and review ratings are deterministic backend calculations. AI feedback never assigns them.
- Practice is capped at 79, clean unassisted transfer at 89, and 90+ requires successful recall at least 24 hours later.
- Mastery may decrease after weak delayed recall; do not preserve an old score artificially.
- Tutor and doubt chat never create mastery evidence. Doubt help during an open transfer must mark that transfer assisted.
- FSRS controls scheduling, not mastery. Keep its state versioned and map objective scores to ratings in code; do not let the model choose intervals or ratings.
- Daily plans are advisory and must preserve free manual access to every subject and topic.
- Run learner Python only in a worker, never on the UI main thread. Do not expose answers or reference solutions prematurely.
- Do not spend Gemini tokens on work that code can grade or reveal deterministically.
- Users may always choose any subject or topic, regardless of recommendations.
- Never expose API secrets to the browser.
- Run relevant tests and build checks before finishing changes.
- Interview mode is assessment, not tutoring; block tutor and doubt help while a scored interview is active.
- Never reveal detailed interview feedback until the scored interview is complete.
- Gemini cannot change blueprint competencies, rubric weights, or section weights.
- Forge Interview Score is never a hiring probability, and behavioral scoring never modifies technical mastery.
- Static accepted course content is authoritative; runtime AI cannot override the confirmed curriculum, coverage specification, or accepted lesson.
- Normal Learn never calls Gemini. AI Tutor teaches only from the static lesson, and normal Practice prefers the static course bank.
- Lesson progress never affects mastery. Runtime doubt retrieval stays within the local course corpus.
- Never scrape prohibited, authenticated, or paid content; fetch only explicit registered source URLs and preserve attribution.
- Use fixed rubrics, structured output, and at most one contextual follow-up per main question.
- Python, SQL/PostgreSQL, and DSA are foundational P0 tracks; planner changes must preserve that priority while keeping every topic manually accessible.
- Arena problems are original, static, versioned content. Never copy external challenge statements or expose reference solutions before pass or Give Up.
- Python and SQL correctness is deterministic. Run Python in the Pyodide worker and SQL in a fresh isolated PGlite worker database; never execute learner input against Forge data.
- Course reading is not mastery, and AI cannot replace independent coding evidence.
