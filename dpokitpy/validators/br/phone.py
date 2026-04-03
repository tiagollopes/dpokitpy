import re


def find_phones(text: str) -> list[str]:
    matches = []

    pattern_masked = r"(?:\(\d{2}\)\s?9?\d{4}-?\d{4}|\(\d{2}\)\s?\d{4}-?\d{4})"
    matches.extend(re.findall(pattern_masked, text))

    pattern_context = r"\b(?:telefone|celular|fone)\s*:\s*(\d{10,11})\b"
    matches.extend(re.findall(pattern_context, text, flags=re.IGNORECASE))

    return matches


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)

    if len(digits) not in (10, 11):
        return False

    ddd = digits[:2]
    numero = digits[2:]

    if not ddd.isdigit():
        return False

    if len(numero) == 8:
        return True

    if len(numero) == 9 and numero[0] == "9":
        return True

    return False
