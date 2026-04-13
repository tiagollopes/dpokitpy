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
    detect_rg_state,
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

    if not is_valid_outros_rg_format(clean):
        return False

    if is_obviously_invalid_rg(clean):
        return False

    if has_negative_context(context):
        return False

    if not has_strong_rg_context(context):
        return False

    # fallback genérico: se houver indício claro de UF, deixa para os validadores estaduais
    if detect_rg_state(clean, context=context):
        return False

    return True


def find_outros_rgs(text: str) -> List[str]:
    results = []
    seen = set()

    patterns = (
        r"(?i)\bRG(?!\s*(?:RJ|ES|MG|SP)\b)[\s:\-]+([0-9]{7,9}[Xx]?)\b",
        r"(?i)\bRegistro\s+Geral[\s:\-]+([0-9]{7,9}[Xx]?)\b",
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

    return results

