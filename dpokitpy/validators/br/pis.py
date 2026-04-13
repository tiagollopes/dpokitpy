import re


def normalize_pis(pis: str) -> str:
    return re.sub(r"\D", "", pis)


def is_valid_pis(pis: str) -> bool:
    digits = normalize_pis(pis)

    if len(digits) != 11:
        return False

    if digits == digits[0] * 11:
        return False

    weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(digits[i]) * weights[i] for i in range(10))

    remainder = total % 11
    check_digit = 0 if remainder in (0, 1) else 11 - remainder

    return check_digit == int(digits[10])


def find_pis(text: str) -> list[str]:
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

    pattern_masked = r"\b\d{3}\.\d{5}\.\d{2}-\d\b"
    pattern_raw = r"(?<!\d)\d{11}(?!\d)"

    for pattern in (pattern_masked, pattern_raw):
        for match in re.finditer(pattern, text):
            raw = match.group(0).strip()

            left_context = text[max(0, match.start() - 20):match.start()].lower()

            if any(word in left_context for word in negative_context_words):
                continue

            if is_valid_pis(raw):
                matches.append(raw)

    return list(dict.fromkeys(matches))
