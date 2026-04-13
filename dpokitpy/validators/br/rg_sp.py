import re
from .rg_common import digits_only, is_repeated_sequence


SP_NEGATIVE_CONTEXT_WORDS = (
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


def normalize_sp_rg(rg: str) -> str:
    return re.sub(r"[^0-9Xx]", "", rg).upper()


def has_sp_negative_context(context: str) -> bool:
    if not context:
        return False

    ctx = context.lower()
    return any(word in ctx for word in SP_NEGATIVE_CONTEXT_WORDS)


def is_valid_sp_rg_format(rg: str) -> bool:
    """
    Formato plausível SP:
    - 8 dígitos + 1 DV
    - DV pode ser 0-9 ou X
    - total limpo = 9 chars
    """
    clean = normalize_sp_rg(rg)

    if not clean:
        return False

    if not re.fullmatch(r"\d{8}[0-9X]", clean):
        return False

    if "X" in clean and not clean.endswith("X"):
        return False

    digits = digits_only(clean)

    if len(digits) != 9 and not (len(digits) == 8 and clean.endswith("X")):
        return False

    if is_repeated_sequence(digits):
        return False

    if digits.startswith("0"):
        return False

    return True


def calc_sp_dv(base8: str) -> str:
    total = 0
    peso = 2

    for digit in reversed(base8):
        total += int(digit) * peso
        peso += 1

    resto = total % 11
    calc = 11 - resto

    if calc == 10:
        return "X"
    if calc == 11:
        return "0"
    return str(calc)


def is_valid_sp_rg(rg: str, context: str = "") -> bool:
    clean = normalize_sp_rg(rg)

    if not is_valid_sp_rg_format(clean):
        return False

    if has_sp_negative_context(context):
        return False

    base8 = clean[:8]
    dv = clean[8]
    expected_dv = calc_sp_dv(base8)

    return dv == expected_dv
