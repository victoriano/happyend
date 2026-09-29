"""Cegado de sinopsis para anotación: sin título, año, década, popularidad ni puntuación.

Limitación documentada: el texto puede contener pistas de época (tecnología, referencias históricas,
nombres de actores no, porque las sinopsis de Wikipedia no suelen incluirlos). El cegado elimina las
señales explícitas, no todas las implícitas.
"""
from __future__ import annotations

import hashlib
import re

YEAR_RE = re.compile(r"\b(1[89]\d{2}|2[01]\d{2})s?\b|['’]\d0s\b")
PAREN_RE = re.compile(r"\s*\([^)]*\)\s*$")


def blind_id(tconst: str, seed: int) -> str:
    return "F" + hashlib.sha256(f"blind|{seed}|{tconst}".encode()).hexdigest()[:8].upper()


def title_variants(*titles: str | None) -> list[str]:
    out = set()
    for t in titles:
        if not isinstance(t, str) or not t.strip():
            continue
        t = t.replace("_", " ").strip()
        out.add(t)
        out.add(PAREN_RE.sub("", t))           # "Heat (1995 film)" -> "Heat"
        if ":" in t:
            out.add(t.split(":", 1)[0].strip())  # título principal antes de los dos puntos
    # Evita enmascarar palabras muy cortas y comunes (p. ej., un título "It" o "Up").
    return sorted((v for v in out if len(v) >= 4), key=len, reverse=True)


def mask(text: str, titles: list[str]) -> str:
    for t in titles:
        text = re.sub(r"\b" + re.escape(t) + r"\b", "[TÍTULO]", text, flags=re.IGNORECASE)
    text = YEAR_RE.sub("[AÑO]", text)
    return text


def truncate_words(text: str, max_words: int) -> tuple[str, bool]:
    words = text.split()
    if len(words) <= max_words:
        return text, False
    # Se conserva el principio y el final (el final es lo que más importa para clasificar el cierre).
    head = int(max_words * 0.45)
    tail = max_words - head
    return " ".join(words[:head]) + " […] " + " ".join(words[-tail:]), True
