import re
from typing import List
from .rg_sp import is_valid_sp_rg

from .rg_common import (
    normalize_rg,
    digits_only,
    has_negative_context,
    has_strong_rg_context,
    is_repeated_sequence,
    is_obviously_invalid_rg,
)

def normalize_outros_rg(rg: str) -> str:
    return re.sub(r"[^0-9Xx]", "", rg).upper()


def is_valid_outros_rg_format(rg: str) -> bool:
    clean = normalize_outros_rg(rg)

    if not clean:
        return False

    if "X" in clean and not clean.endswith("X"):
        return False

    if not re.fullmatch(r"\d{7,9}|\d{7,8}X", clean):
        return False

    digits = digits_only(clean)

    if len(digits) < 7 or len(digits) > 9:
        return False

    if is_repeated_sequence(digits):
        return False

    if digits.startswith("0"):
        return False

    return True


def is_valid_outros_rg(rg: str, context: str = "") -> bool:
    clean = normalize_outros_rg(rg)
    ctx = (context or "").lower()

    if not is_valid_outros_rg_format(clean):
        return False

    if has_negative_context(context):
        return False

    # contexto forte local para OUTROS
    has_generic_rg_context = (
        "registro geral" in ctx
        or "rg " in ctx
        or "identidade" in ctx
        or "documento de identidade" in ctx
        or "carteira de identidade" in ctx
        or "número de identidade" in ctx
        or "numero de identidade" in ctx
    )

    if not has_generic_rg_context:
        return False

    # rejeita apenas quando houver marcador explícito de UF
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

    # aqui sim a heurística de "obviamente inválido"
    # mas sem punir o caso forte "Registro Geral <numero>"
    if "registro geral" not in ctx and is_obviously_invalid_rg(clean):
        return False

    return True

def find_outros_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    # caminho dedicado para "Registro Geral"
    registro_geral_pattern = r"(?i)\bRegistro\s+Geral[\s:\-]+([0-9]{7,9}[Xx]?)\b"

    for match in re.finditer(registro_geral_pattern, text, flags=re.IGNORECASE):
        candidate = match.group(1).strip()

        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        ctx = text[start:end]
        ctx_lower = ctx.lower()

        if not is_valid_outros_rg_format(candidate):
            continue

        if has_negative_context(ctx):
            continue

        if any(marker in ctx_lower for marker in (
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
            continue

        key = normalize_rg(candidate)
        if key not in seen:
            seen.add(key)
            results.append(candidate)

    patterns = (
        r"(?i)\bRG(?!\s*(?:RJ|ES|MG|SP)\b)[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bIdentidade(?!\s*(?:RJ|ES|MG|SP)\b)[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bDocumento\s+de\s+identidade(?!\s*(?:RJ|ES|MG|SP)\b)[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bCarteira\s+de\s+identidade(?!\s*(?:RJ|ES|MG|SP)\b)[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\b(?:Meu\s+)?n[úu]mero\s+de\s+identidade\s*(?:é|e|:)?\s*([0-9]{7,9}[Xx]?)\b",
    )

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidate = match.group(1).strip()

            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            ctx = text[start:end]

            if is_valid_outros_rg(candidate, context=ctx):
                key = normalize_rg(candidate)
                if key not in seen:
                    seen.add(key)
                    results.append(candidate)

    # fallback para RG cru solto em contexto documental
    fallback_pattern = r"\b([0-9]{8}[Xx]|[0-9]{9})\b"

    for match in re.finditer(fallback_pattern, text):
        candidate = match.group(1).strip()

        start = max(0, match.start() - 60)
        end = min(len(text), match.end() + 60)
        ctx = text[start:end]
        ctx_lower = ctx.lower()

        if not any(word in ctx_lower for word in (
            "rg",
            "identidade",
            "documento",
            "registro geral",
            "carteira de identidade",
        )):
            continue

        if has_negative_context(ctx):
            continue

        if any(marker in ctx_lower for marker in (
            "rg rj",
            "rg es",
            "rg mg",
           # "rg sp",
            "ssp/rj",
            "ssp/es",
            "ssp/mg",
            "ssp/sp",
            "detran/rj",
            "sesp/es",
        )):
            continue

        if is_valid_outros_rg(candidate, context=ctx):
            key = normalize_rg(candidate)
            if key not in seen:
                seen.add(key)
                results.append(candidate)

    return results
