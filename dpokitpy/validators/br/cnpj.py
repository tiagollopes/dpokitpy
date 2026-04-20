import re

def is_valid_cnpj(cnpj: str) -> bool:
    # Limpa o CNPJ mantendo letras e números
    cnpj = re.sub(r"[^A-Z0-9]", "", cnpj.upper())

    if len(cnpj) != 14:
        return False

    # CNPJs com todos os dígitos iguais ainda são inválidos no sistema novo
    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(payload, pesos):
        soma = 0
        for i, char in enumerate(payload):
            # No novo CNPJ, letras são convertidas pelo valor ASCII - 48
            valor = ord(char) - 48
            soma += valor * pesos[i]

        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos oficiais da Receita Federal
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Validação do primeiro dígito
    dg1 = calcular_digito(cnpj[:12], pesos1)
    if cnpj[12] != str(dg1):
        return False

    # Validação do segundo dígito
    dg2 = calcular_digito(cnpj[:13], pesos2)
    if cnpj[13] != str(dg2):
        return False

    return True

import re

def find_cnpjs(text: str) -> list[str]:
    matches = []

    patterns = [
        # mascarado completo: 12 base alfanumérica + 2 DVs numéricos
        r"(?<![A-Z0-9])[A-Z0-9]{2}\.[A-Z0-9]{3}\.[A-Z0-9]{3}/[A-Z0-9]{4}-\d{2}(?![A-Z0-9])",

        # sem os pontos, mas com / e -
        r"(?<![A-Z0-9])[A-Z0-9]{8}/[A-Z0-9]{4}-\d{2}(?![A-Z0-9])",

        # colado
        r"(?<![A-Z0-9])[A-Z0-9]{12}\d{2}(?![A-Z0-9])",
    ]

    upper_text = text.upper()

    for pattern in patterns:
        matches.extend(re.findall(pattern, upper_text, flags=re.IGNORECASE))

    return list(dict.fromkeys(matches))
