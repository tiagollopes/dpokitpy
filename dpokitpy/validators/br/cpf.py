import re


def is_valid_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)

    resto = total % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto

    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)

    resto = total % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto

    return cpf[9] == str(digito1) and cpf[10] == str(digito2)


def find_cpfs(text: str) -> list[str]:
    matches = []

    pattern_masked = r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"
    matches.extend(re.findall(pattern_masked, text))

    pattern_context = r"\bCPF\s*:\s*(\d{11})\b"
    matches.extend(re.findall(pattern_context, text, flags=re.IGNORECASE))

    return matches
