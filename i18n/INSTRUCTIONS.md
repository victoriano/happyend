You are translating annotation justifications for a data-journalism website from Spanish into natural American English.

For each input file /home/claude/finales-cine/i18n/in/bXXX.json assigned to you, write /home/claude/finales-cine/i18n/out/bXXX.json.

Input format: {"tt123": {"title": "...", "year": 1995, "type": "film"|"series", "texts": {"A": "...", "fA": "...", ...}}, ...}
Output format (JSON, UTF-8): {"tt123": {"A": "<English>", "fA": "<English>", ...}, ...} — same ids, exactly the same keys as in "texts", every value a translated string. Do not include title/year/type.

Field meanings (context only): A/B/J = why the ending was classified as happy/bittersweet/ambiguous/tragic (annotator A, annotator B, referee); fA/fB/fJ/fM = why the title got its "feel good" score (0-10); uA/uB/uJ = why the depicted society got its utopia/dystopia score (0-10).

Rules:
- Translate faithfully and completely, same meaning and similar length; concise, fluent American English. Don't add or drop information.
- Keep the term "feel good" as is. Use "dystopia/utopia", "happy ending", "bittersweet", "ambiguous", "tragic".
- If a show/film title appears in Spanish translation, use its original English title (the "title" field is the original title of the work itself). Many titles are Spanish productions: keep Spanish proper names and original Spanish titles as they are (e.g. "La casa de papel"), but translate everything else.
- Output must be valid JSON. Writing it with a short Python script (json.dump(..., ensure_ascii=False)) is fine, but YOU must do the translation yourself — no external APIs or translation libraries.
- Process files one at a time; you may build each output in several steps if long.
- When done, run: python3 /home/claude/finales-cine/i18n/check.py and make sure none of YOUR files are listed as bad (other agents' files may be missing — ignore those); fix yours if needed. Reply with one line: which files you completed.
