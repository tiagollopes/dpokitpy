import re
from typing import List, Optional

from .rg_common import normalize_rg
from .rg_rj import is_valid_rj_rg
from .rg_es import is_valid_es_rg
from .rg_mg import is_valid_mg_rg
from .rg_sp import (
    is_valid_sp_rg,
    is_valid_sp_rg_format,
    has_sp_negative_context,
    normalize_sp_rg,
)
from .rg_outros import find_outros_rgs, is_valid_outros_rg, is_valid_outros_rg_format

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
    ctx = (context or "").lower()
    clean = normalize_rg(rg).upper()
    hint = (state_hint or "").strip().upper()

    # hint explícito
    if hint == "RJ":
        return is_valid_rj_rg(rg, context=context)
    if hint == "SP":
        return is_valid_sp_rg(rg, context=context)
    if hint == "ES":
        return is_valid_es_rg(rg, context=context)
    if hint == "MG":
        return is_valid_mg_rg(rg, context=context)

    # contexto explícito RJ
    if any(x in ctx for x in ("rg rj", "ssp/rj", "detran/rj")):
        return is_valid_rj_rg(rg, context=context)

    # contexto explícito ES
    if any(x in ctx for x in ("rg es", "ssp/es", "sesp/es")):
        return is_valid_es_rg(rg, context=context)

    # contexto explícito MG
    if any(x in ctx for x in ("rg mg", "ssp/mg")):
        return is_valid_mg_rg(rg, context=context)

    # contexto explícito SP
    if any(x in ctx for x in ("rg sp", "ssp/sp")):
        return is_valid_sp_rg(rg, context=context)
        # caminho dedicado e conservador para OUTROS com "Registro Geral"

    # evita que o roteador central derrube casos genéricos já aceitos pelo benchmark
    if "registro geral" in ctx:
        if any(marker in ctx for marker in (
            "rg rj",
            "rg es",
            "rg mg",
            "rg sp",
            "ssp/rj",
            "ssp/es",
            "ssp/mg",
            "ssp/sp",
            "detran/rj",
            "sesp/es",
        )):
            return False

        return is_valid_outros_rg_format(rg)

    # formato típico SP com máscara: mantém o ajuste que já funcionou
    if re.fullmatch(r"\d{2}\.\d{3}\.\d{3}-[0-9X]", rg.strip(), flags=re.IGNORECASE):
        return is_valid_sp_rg(rg, context=context)

    # números curtos/genéricos com contexto de identidade:
    # tenta RJ/ES/MG antes de cair no atalho de SP
    if any(x in ctx for x in (
        "identidade",
        "documento de identidade",
        "carteira de identidade",
        "número de identidade",
        "numero de identidade",
        "rg",
    )):
        if is_valid_rj_rg(rg, context=context):
            return True
        if is_valid_es_rg(rg, context=context):
            return True
        if is_valid_mg_rg(rg, context=context):
            return True
        if is_valid_outros_rg(rg, context=context):
            return True

    # heurística antiga de SP: deixa por último para não matar RJ/ES/MG
    if re.fullmatch(r"\d{8}[0-9X]", clean):
        return is_valid_sp_rg(rg, context=context)

    if is_valid_rj_rg(rg, context=context):
        return True

    if is_valid_es_rg(rg, context=context):
        return True

    if is_valid_mg_rg(rg, context=context):
        return True

    return is_valid_outros_rg(rg, context=context)


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
    seen_exact = set()

    def add(items):
        for item in items:
            if item not in seen_exact:
                seen_exact.add(item)
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
        r"(?i)\b([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bRG\s+SP\s+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bSSP\/SP[\s:\-]+([0-9]{2}\.[0-9]{3}\.[0-9]{3}-[0-9Xx])\b",
        r"(?i)\bRG\s+SP\s+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bSSP\/SP[\s:\-]+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bRG[\s:\-]+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bIdentidade[\s:\-]+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bDocumento\s+de\s+identidade[\s:\-]+([0-9]{8}[0-9Xx])\b",
        r"(?i)\bCarteira\s+de\s+identidade[\s:\-]+([0-9]{8}[0-9Xx])\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{8}[0-9Xx])\b",
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

            if has_sp_negative_context(ctx):
                continue

            clean = normalize_sp_rg(candidate)

            if re.fullmatch(r"\d{8}[0-9X]", clean):
                key = candidate
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    return results
