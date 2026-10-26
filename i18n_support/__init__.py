"""Internacionalización para ANIME POSTER LAB.

Idiomas soportados: ``es``, ``en``, ``fr``, ``ja``, ``hi``.

Los catálogos son ficheros ``.po`` estándar en
``locale/<lang>/LC_MESSAGES/messages.po`` (compilables con ``msgfmt``), pero se
leen directamente en tiempo de ejecución para no exigir un paso de compilación.
"""
from __future__ import annotations

import os
from pathlib import Path

LOCALES = ("es", "en", "fr", "ja", "hi")
DEFAULT_LANG = "es"
_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"

_catalogo: dict[str, str] = {}
_lang: str = DEFAULT_LANG


def _descomillar(valor: str) -> str:
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        valor = valor[1:-1]
    return (valor.replace("\\n", "\n").replace("\\t", "\t")
                 .replace('\\"', '"').replace("\\\\", "\\"))


def _cargar_po(ruta: Path) -> dict[str, str]:
    """Lee un ``.po`` simple (msgid/msgstr de una línea) a un diccionario."""
    catalogo: dict[str, str] = {}
    if not ruta.is_file():
        return catalogo
    msgid: str | None = None
    for cruda in ruta.read_text(encoding="utf-8").splitlines():
        linea = cruda.strip()
        if not linea or linea.startswith("#"):
            continue
        if linea.startswith("msgid "):
            msgid = _descomillar(linea[6:])
        elif linea.startswith("msgstr ") and msgid is not None:
            catalogo[msgid] = _descomillar(linea[7:])
            msgid = None
    return catalogo


def available() -> tuple[str, ...]:
    """Idiomas soportados."""
    return LOCALES


def install(lang: str | None = None) -> str:
    """Activa un idioma (``lang``, ``APL_LANG`` o por defecto) y lo devuelve."""
    global _catalogo, _lang
    elegido = lang or os.environ.get("APL_LANG") or DEFAULT_LANG
    elegido = str(elegido).split(".")[0].split("_")[0].split("-")[0].lower()
    if elegido not in LOCALES:
        elegido = DEFAULT_LANG
    _catalogo = _cargar_po(_LOCALE_DIR / elegido / "LC_MESSAGES" / "messages.po")
    _lang = elegido
    return _lang


def tr(texto: str) -> str:
    """Traduce ``texto`` al idioma activo (devuelve el original si no hay entrada)."""
    return _catalogo.get(texto, texto)


def lang() -> str:
    """Idioma activo."""
    return _lang
