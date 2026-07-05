"""Cliente de la API de Claude para fable-forge.

Backend único: claude-fable-5 vía Messages API. Sin RAG, sin base de datos,
sin otros servicios.

Notas específicas de claude-fable-5:
- El thinking está siempre activo y no se configura: no se pasa el parámetro
  `thinking` (un `disabled` explícito devuelve 400).
- No acepta `temperature`/`top_p`/`top_k`.
- Los clasificadores de seguridad pueden devolver `stop_reason: "refusal"`
  (HTTP 200). Para fábulas infantiles es prácticamente imposible, pero se
  maneja igual: por defecto se opta al fallback server-side hacia
  claude-opus-4-8, desactivable con FABLE_FORGE_NO_FALLBACK=1 si se quiere
  claude-fable-5 de forma estrictamente exclusiva.
"""

from __future__ import annotations

import os

from anthropic import Anthropic

MODEL = "claude-fable-5"
FALLBACK_MODEL = "claude-opus-4-8"
FALLBACK_BETA = "server-side-fallback-2026-06-01"

# El thinking de claude-fable-5 cuenta contra max_tokens, así que se deja
# margen amplio; una fábula + metadata rara vez supera los ~3000 tokens de
# texto visible.
DEFAULT_MAX_TOKENS = 16000


class FableForgeError(Exception):
    """Error de generación de fable-forge."""


class RefusalError(FableForgeError):
    """El modelo (y su fallback, si estaba activo) declinó el pedido."""


def _fallback_enabled() -> bool:
    return os.environ.get("FABLE_FORGE_NO_FALLBACK", "") not in ("1", "true", "yes")


def generate(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Hace una llamada a claude-fable-5 y devuelve el texto de la respuesta.

    El system prompt lleva cache_control: en usos repetidos dentro de la
    ventana de caché (series, tandas de variantes) el prefijo se sirve
    cacheado.
    """
    client = Anthropic()
    system = [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]
    messages = [{"role": "user", "content": user_prompt}]

    if _fallback_enabled():
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            betas=[FALLBACK_BETA],
            fallbacks=[{"model": FALLBACK_MODEL}],
            system=system,
            messages=messages,
        )
    else:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )

    if response.stop_reason == "refusal":
        detail = ""
        if response.stop_details and response.stop_details.explanation:
            detail = f" ({response.stop_details.explanation})"
        raise RefusalError(f"El modelo declinó el pedido{detail}.")

    if response.stop_reason == "max_tokens":
        raise FableForgeError(
            "La respuesta se cortó por max_tokens; reintentá con --max-tokens más alto."
        )

    text = "".join(block.text for block in response.content if block.type == "text")
    if not text.strip():
        raise FableForgeError("La respuesta llegó vacía.")
    return text
