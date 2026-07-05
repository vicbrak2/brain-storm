"""Persistencia local de fable-forge: archivos planos, sin base de datos.

- Fábulas: markdown en <data_dir>/fables/.
- Series: un JSON por serie en <data_dir>/series/, con los personajes
  acumulados (extraídos del bloque fable-meta de cada fábula) y un resumen de
  cada entrega. Ese JSON es lo que se inyecta como bloque <serie> al generar
  la próxima fábula.

El directorio de datos por defecto es fable-forge/output/ (gitignoreado);
se puede cambiar con FABLE_FORGE_DATA.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

_META_RE = re.compile(r"```fable-meta\s*\n(.*?)```", re.DOTALL)
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_MORAL_RE = re.compile(r"\*\*Moraleja:\*\*\s*(.+)$", re.MULTILINE)


def data_dir() -> Path:
    env = os.environ.get("FABLE_FORGE_DATA")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "output"


def fables_dir() -> Path:
    return data_dir() / "fables"


def series_dir() -> Path:
    return data_dir() / "series"


def _slugify(text: str, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len] or "fabula"


def parse_fable(markdown: str) -> dict:
    """Extrae título, moraleja y metadata (bloque fable-meta) de una fábula."""
    title_m = _TITLE_RE.search(markdown)
    moral_m = _MORAL_RE.search(markdown)
    meta = None
    meta_m = _META_RE.search(markdown)
    if meta_m:
        try:
            meta = json.loads(meta_m.group(1))
        except json.JSONDecodeError:
            meta = None
    return {
        "titulo": title_m.group(1).strip() if title_m else None,
        "moraleja": moral_m.group(1).strip() if moral_m else None,
        "meta": meta,
    }


def save_fable(markdown: str, suffix: str | None = None) -> Path:
    """Guarda una fábula en fables/ y devuelve la ruta."""
    parsed = parse_fable(markdown)
    stem = _slugify(parsed["titulo"] or "fabula")
    if suffix:
        stem = f"{stem}--{suffix}"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = fables_dir() / f"{stamp}-{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------


def series_path(name: str) -> Path:
    return series_dir() / f"{_slugify(name)}.json"


def load_series(name: str) -> dict | None:
    path = series_path(name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_series() -> list[str]:
    if not series_dir().exists():
        return []
    return sorted(p.stem for p in series_dir().glob("*.json"))


def update_series(name: str, fable_markdown: str) -> dict:
    """Incorpora una fábula nueva a la serie (creándola si no existe).

    Los personajes se mergean por nombre: los nuevos se agregan, los
    existentes se conservan tal como se establecieron en su primera aparición
    (la identidad de un personaje recurrente no se redefine en cada entrega).
    """
    parsed = parse_fable(fable_markdown)
    serie = load_series(name) or {
        "nombre": name,
        "escenario": None,
        "personajes": [],
        "fabulas": [],
    }

    meta = parsed["meta"] or {}
    if not serie["escenario"] and meta.get("escenario"):
        serie["escenario"] = meta["escenario"]

    known = {p["nombre"].lower() for p in serie["personajes"] if p.get("nombre")}
    for personaje in meta.get("personajes", []):
        nombre = (personaje.get("nombre") or "").lower()
        if nombre and nombre not in known:
            serie["personajes"].append(personaje)
            known.add(nombre)

    serie["fabulas"].append(
        {
            "titulo": parsed["titulo"],
            "moraleja": parsed["moraleja"],
            "resumen": meta.get("resumen"),
        }
    )

    path = series_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(serie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return serie
