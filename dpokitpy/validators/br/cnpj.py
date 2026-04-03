import re


def is_valid_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r"\D", "", cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = 0
    for i in range(12):
        total += int(cnpj[i]) * pesos1[i]

    resto = total % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = 0
    for i in range(13):
        total += int(cnpj[i]) * pesos2[i]

    resto = total % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto

    return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)


def find_cnpjs(text: str) -> list[str]:
    matches = []

    pattern_masked = r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"
    matches.extend(re.findall(pattern_masked, text))

    pattern_context = r"\bCNPJ\s*:\s*(\d{14})\b"
    matches.extend(re.findall(pattern_context, text, flags=re.IGNORECASE))

    return matches
