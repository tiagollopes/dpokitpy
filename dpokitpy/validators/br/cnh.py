import re


def normalize_cnh(cnh: str) -> str:
    return re.sub(r"\D", "", cnh)


def is_valid_cnh(cnh: str) -> bool:
    digits = normalize_cnh(cnh)

    if len(digits) != 11:
        return False

    if digits == digits[0] * 11:
        return False

    nums = [int(d) for d in digits]

    # Primeiro dígito verificador
    sum1 = 0
    weight = 9
    for i in range(9):
        sum1 += nums[i] * weight
        weight -= 1

    dv1 = sum1 % 11
    if dv1 >= 10:
        dv1 = 0

    # Segundo dígito verificador
    sum2 = 0
    weight = 1
    for i in range(9):
        sum2 += nums[i] * weight
        weight += 1

    sum2 += dv1 * 9

    dv2 = sum2 % 11
    if dv2 >= 10:
        dv2 = 0

    return nums[9] == dv1 and nums[10] == dv2


def find_cnhs(text: str) -> list[str]:
    matches = []

    negative_context_words = (
        "protocolo",
        "pedido",
        "codigo",
        "código",
        "token",
        "identificador",
        "id "
    )

    pattern_raw = r"(?<!\d)\d{11}(?!\d)"

    for match in re.finditer(pattern_raw, text):
        raw = match.group(0).strip()

        left_context = text[max(0, match.start() - 20):match.start()].lower()

        if any(word in left_context for word in negative_context_words):
            continue

        if is_valid_cnh(raw):
            matches.append(raw)

    return list(dict.fromkeys(matches))
