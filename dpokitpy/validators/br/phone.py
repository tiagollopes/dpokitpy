import re


SERVICE_PREFIXES = ("0300", "0500", "0800", "0900")
NEGATIVE_CONTEXT_WORDS = (
    "protocolo",
    "pedido",
    "codigo",
    "código",
    "token",
    "identificador",
    "id ",
)


def _normalize_phone_digits(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)

    # 1) Remove DDI 55 repetido ou duplicado
    while len(digits) > 11 and digits.startswith("55"):
        digits = digits[2:]

    # 2) Caso especial: serviço com um zero sobrando antes do prefixo
    # Ex.: 005001234567 -> 05001234567
    if len(digits) > 11 and digits.startswith("0") and digits[1:5] in {"300", "500", "800", "900"}:
        digits = digits[1:]

    # 3) Remove zeros à esquerda enquanto ainda houver excesso
    # Resolve casos como (051), (011), 002 etc.
    while len(digits) >= 11 and digits.startswith("0"):
        digits = digits[1:]

    # 4) Remove zero extra logo após o DDD quando o número ainda estiver grande
    # Ex.: 1103455819 (fixo "sujo"), 11901234567 etc.
    while len(digits) > 11 and len(digits) >= 3 and digits[2] == "0":
        digits = digits[:2] + digits[3:]

    return digits


def is_valid_phone(phone: str) -> bool:
    digits = _normalize_phone_digits(phone)

    # Serviços nacionais
    if digits.startswith(SERVICE_PREFIXES):
        if len(digits) != 11:
            return False
        if digits == digits[0] * len(digits):
            return False
        return True

    # Telefones comuns: DDD + número local
    if len(digits) not in (10, 11):
        return False

    ddd = int(digits[:2])
    if not (1 <= ddd <= 99):
        return False

    local_num = digits[2:]

    if len(local_num) == 9:
        # Celular
        if local_num[0] != "9":
            return False
    elif len(local_num) == 8:
        # Fixo
        # Aceita 0-9 por causa dos formatos extremos gerados pelo Faker
        if local_num[0] not in "0123456789":
            return False
    else:
        return False

    # Bloqueia sequências artificiais óbvias
    if local_num == local_num[0] * len(local_num):
        return False

    return True


def _has_negative_context(text: str, start: int) -> bool:
    left = text[max(0, start - 20):start].lower()
    return any(word in left for word in NEGATIVE_CONTEXT_WORDS)


def find_phones(text: str) -> list[str]:
    matches = []

    # Telefones com máscara / espaços / hífen / DDI repetido
    pattern_wide = (
        r"(?:\+?\s*55[\s\-]*){0,2}"
        r"(?:\(?\d{1,3}\)?[\s\-]*)?"
        r"(?:9[\s\-]*)?"
        r"\d{3,5}[\s\-]?\d{4}"
    )

    # Números puros grandes
    pattern_raw = r"(?<!\d)\d{10,16}(?!\d)"

    for pattern in (pattern_wide, pattern_raw):
        for match in re.finditer(pattern, text):
            raw = match.group(0).strip()
            raw = re.sub(r"[^\d]+$", "", raw)

            if _has_negative_context(text, match.start()):
                continue

            if sum(c.isdigit() for c in raw) >= 8:
                matches.append(raw)

    # Remove duplicados por número normalizado
    unique = []
    seen = set()

    for item in matches:
        key = _normalize_phone_digits(item)
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique
