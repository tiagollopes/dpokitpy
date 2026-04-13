import re

def is_valid_cpf(cpf: str) -> bool:
    # Remove qualquer caractere que não seja número
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    # Validação do primeiro dígito
    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)
    resto = total % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Validação do segundo dígito
    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)
    resto = total % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return cpf[9] == str(digito1) and cpf[10] == str(digito2)

def find_cpfs(text: str) -> list[str]:
    """
    Busca CPFs em diversos formatos: com máscara, sem máscara,
    com espaços ou colados em outros caracteres.
    """
    matches = []

    # 1. Padrão com máscara padrão: 000.000.000-00
    pattern_masked = r"\d{3}\.\d{3}\.\d{3}-\d{2}"
    matches.extend(re.findall(pattern_masked, text))

    # 2. Padrão apenas números (11 dígitos sequenciais)
    # Usamos lookahead/lookbehind negativos para não pegar sequências maiores que 11
    pattern_digits = r"(?<!\d)\d{11}(?!\d)"
    matches.extend(re.findall(pattern_digits, text))

    # 3. Padrão com espaços: 000 000 000 00
    pattern_spaced = r"\d{3}\s\d{3}\s\d{3}\s\d{2}"
    matches.extend(re.findall(pattern_spaced, text))

    # Remove duplicatas mantendo a ordem
    return list(dict.fromkeys(matches))
