import re
from typing import List, Optional

from .rg_common import normalize_rg
from .rg_rj import is_valid_rj_rg
from .rg_es import is_valid_es_rg
from .rg_mg import is_valid_mg_rg
from .rg_sp import is_valid_sp_rg
from .rg_outros import find_outros_rgs, is_valid_outros_rg

RJ_NEGATIVE_MARKERS = (
    "protocolo",
    "pedido",
    "codigo",
    "código",
    "token",
    "identificador",
    "matricula",
    "matrícula",
    "referencia",
    "referência",
)


def _context_window(text: str, start: int, end: int, left: int = 80, right: int = 80) -> str:
    return text[max(0, start - left):min(len(text), end + right)]


def _has_negative_context(context: str) -> bool:
    ctx = context.lower()
    return any(marker in ctx for marker in RJ_NEGATIVE_MARKERS)


def is_valid_rg(rg: str, context: str = "", state_hint: Optional[str] = None) -> bool:

    return is_valid_rj_rg(rg, context=context)


def find_rj_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    patterns = (
        r"(?i)\bRG\s+RJ\s+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bRG[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bIdentidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bDocumento\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bCarteira\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bSSP\/RJ[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bDETRAN\/RJ[\s:\-]+([0-9]{7,9}[Xx]?)\b",
    )

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidate = match.group(1).strip()
            ctx = _context_window(text, match.start(), match.end(), left=100, right=100)

            if _has_negative_context(ctx):
                continue

            if is_valid_rj_rg(candidate, context=ctx):
                key = normalize_rg(candidate)
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    return results


def find_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    def add(items):
        for item in items:
            key = normalize_rg(item)
            if key not in seen:
                seen.add(key)
                results.append(item)

    add(find_rj_rgs(text))
    add(find_es_rgs(text))
    add(find_mg_rgs(text))
    add(find_sp_rgs(text))
    add(find_outros_rgs(text))

    return results

def find_es_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    patterns = (
        r"(?i)\bRG\s+ES\s+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bRG[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bIdentidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bDocumento\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bCarteira\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bSSP\/ES[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bSESP\/ES[\s:\-]+([0-9]{7,9}[Xx]?)\b",
    )

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidate = match.group(1).strip()
            ctx = _context_window(text, match.start(), match.end(), left=100, right=100)

            if _has_negative_context(ctx):
                continue

            if is_valid_es_rg(candidate, context=ctx):
                key = normalize_rg(candidate)
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    return results

def find_mg_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    patterns = (
        r"(?i)\bRG\s+MG\s+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bIdentidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bDocumento\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bCarteira\s+de\s+identidade[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bSSP\/MG[\s:\-]+([0-9]{7,9}[Xx]?)\b",
    )

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidate = match.group(1).strip()
            ctx = _context_window(text, match.start(), match.end(), left=100, right=100)

            if _has_negative_context(ctx):
                continue

            if is_valid_mg_rg(candidate, context=ctx):
                key = normalize_rg(candidate)
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    return results

def find_sp_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    patterns = (
        # forte com SP
        r"(?i)\bRG\s+SP\s+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bRG\s+SP\s+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bSSP\/SP[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bSSP\/SP[\s:\-]+([0-9]{8}[0-9Xx])\b",

        # genérico permitido só no formato mascarado clássico de SP
        r"(?i)\bRG[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bIdentidade[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bDocumento\s+de\s+identidade[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bCarteira\s+de\s+identidade[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
    )

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidate = match.group(1).strip()
            ctx = _context_window(text, match.start(), match.end(), left=100, right=100)

            if _has_negative_context(ctx):
                continue

            if is_valid_sp_rg(candidate, context=ctx):
                key = normalize_rg(candidate)
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    return results
