import re
from .rg_common import digits_only, is_repeated_sequence


ES_POSITIVE_CONTEXT_WORDS = (
    "rg",
    "rg es",
    "identidade",
    "registro geral",
    "documento de identidade",
    "numero de identidade",
    "número de identidade",
    "carteira de identidade",
    "ssp/es",
    "sesp/es",
    "es",
)

ES_NEGATIVE_CONTEXT_WORDS = (
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


def normalize_es_rg(rg: str) -> str:
    return re.sub(r"[^0-9Xx]", "", rg).upper()


def has_es_positive_context(context: str) -> bool:
    if not context:
        return False

    ctx = context.lower()
    return any(word in ctx for word in ES_POSITIVE_CONTEXT_WORDS)


def has_es_negative_context(context: str) -> bool:
    if not context:
        return False

    ctx = context.lower()
    return any(word in ctx for word in ES_NEGATIVE_CONTEXT_WORDS)


def is_valid_es_rg_format(rg: str) -> bool:
    """
    Formato plausível ES:
    - 7 a 9 dígitos
    - ou 7 a 8 dígitos + X final
    """
    clean = normalize_es_rg(rg)

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


def is_valid_es_rg(rg: str, context: str = "") -> bool:
    clean = normalize_es_rg(rg)

    if not is_valid_es_rg_format(clean):
        return False

    if has_es_negative_context(context):
        return False

    return True
