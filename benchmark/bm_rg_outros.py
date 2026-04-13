import os
import sys
import time
import random
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dpokitpy.guard import Guard


def random_digits(length: int) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def not_repeated(value: str) -> bool:
    return len(set(value)) > 1


def generate_non_repeated_digits(length: int) -> str:
    while True:
        value = random_digits(length)
        if not_repeated(value) and not value.startswith("0"):
            return value


def generate_valid_outros_rg() -> str:
    length = random.choice([7, 8, 9])
    return generate_non_repeated_digits(length)


def generate_invalid_outros_rg() -> str:
    invalid_options = [
        "1111111",
        "22222222",
        "999999999",
        "000000000",
        "012345678",
        "123",
        "1234567890",
        "ABCDEFG",
        "12X3456",
        "X1234567",
    ]

    if random.choice([True, False]):
        return random.choice(invalid_options)

    value = generate_non_repeated_digits(random.choice([7, 8, 9]))
    # força um começo inválido
    return "0" + value[1:]


def generate_noise_number() -> str:
    size = random.choice([7, 8, 9, 10, 11])
    return random_digits(size)


def build_sample():
    choice = random.choice([
        "OUTROS_VALID",
        "OUTROS_VALID",
        "OUTROS_VALID",
        "OUTROS_VALID",
        "OUTROS_INVALID",
        "NOISE",
        "NEGATIVE_CONTEXT",
        "STATE_SPECIFIC",
    ])

    if choice == "OUTROS_VALID":
        rg = generate_valid_outros_rg()
        text = random.choice([
            f"RG {rg}",
            f"Registro Geral {rg}",
            f"Identidade {rg}",
            f"Documento de identidade {rg}",
            f"Carteira de identidade {rg}",
            f"Meu número de identidade é {rg}",
        ])
        return text, True

    if choice == "OUTROS_INVALID":
        rg = generate_invalid_outros_rg()
        text = random.choice([
            f"RG {rg}",
            f"Registro Geral {rg}",
            f"Identidade {rg}",
            f"Documento de identidade {rg}",
        ])
        return text, False

    if choice == "NOISE":
        number = generate_noise_number()
        text = random.choice([
            f"Código {number}",
            f"Referência {number}",
            f"Identificador {number}",
            f"Matrícula {number}",
            f"Token {number}",
            f"Pedido {number}",
        ])
        return text, False

    if choice == "NEGATIVE_CONTEXT":
        rg = generate_valid_outros_rg()
        text = random.choice([
            f"Protocolo {rg}",
            f"Pedido {rg}",
            f"Token {rg}",
            f"Código {rg}",
            f"Identificador {rg}",
            f"Matrícula {rg}",
        ])
        return text, False

    if choice == "STATE_SPECIFIC":
        rg = generate_valid_outros_rg()
        text = random.choice([
            f"RG RJ {rg}",
            f"RG ES {rg}",
            f"RG MG {rg}",
            f"SSP/RJ {rg}",
            f"SSP/ES {rg}",
            f"SSP/MG {rg}",
            # SP fica fora do benchmark de OUTROS porque é outro fluxo
        ])
        return text, False

    return "RG 111111111", False


def issue_has_value(issue, text: str) -> bool:
    value = getattr(issue, "value", None)
    if value is None and isinstance(issue, dict):
        value = issue.get("value")
    if not value:
        return False
    return str(value) in text


def is_outros_hit(issue, text: str) -> bool:
    issue_type = getattr(issue, "type", None)
    valid = getattr(issue, "valid", None)

    if issue_type is None and isinstance(issue, dict):
        issue_type = issue.get("type")
    if valid is None and isinstance(issue, dict):
        valid = issue.get("valid")

    if issue_type != "RG" or not valid:
        return False

    text_up = text.upper()

    # Não conta como OUTROS se houver pista clara de estado específico
    forbidden_markers = (
        "RG RJ",
        "RG ES",
        "RG MG",
        "RG SP",
        "SSP/RJ",
        "SSP/ES",
        "SSP/MG",
        "SSP/SP",
        "DETRAN/RJ",
        "SESP/ES",
    )

    if any(marker in text_up for marker in forbidden_markers):
        return False

    # Tem que aparecer dentro de um contexto genérico
    generic_markers = (
        "RG ",
        "REGISTRO GERAL",
        "IDENTIDADE",
        "DOCUMENTO DE IDENTIDADE",
        "CARTEIRA DE IDENTIDADE",
        "NÚMERO DE IDENTIDADE",
        "NUMERO DE IDENTIDADE",
    )

    if not any(marker in text_up for marker in generic_markers):
        return False

    return issue_has_value(issue, text)


def run_benchmark(iterations=2000):
    guard = Guard(country="BR")

    false_negatives = 0
    false_positives = 0
    hits = 0
    errors = []

    start_time = time.perf_counter()

    for _ in range(iterations):
        text, should_find = build_sample()

        result = guard.validate(text)
        found_valid = [i for i in result.issues if is_outros_hit(i, text)]

        if should_find and found_valid:
            hits += 1
        elif should_find and not found_valid:
            false_negatives += 1
            errors.append(f"[FALSO NEGATIVO] Texto: '{text}'")
        elif not should_find and found_valid:
            false_positives += 1
            errors.append(f"[FALSO POSITIVO] Texto: '{text}'")

    end_time = time.perf_counter()

    total_errors = false_negatives + false_positives
    precision = round(((iterations - total_errors) / iterations) * 100, 2)
    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)

    log_path = os.path.join(os.path.dirname(__file__), "erros_rg_outros.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write("RELATÓRIO DE FALHAS - RG OUTROS\n")
            f.write(f"Total de amostras: {iterations}\n")
            f.write(f"Falsos negativos: {false_negatives}\n")
            f.write(f"Falsos positivos: {false_positives}\n\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    print("\n--- RESULTADO BENCHMARK RG OUTROS ---")
    print(f"amostras           : {iterations}")
    print(f"hits               : {hits}")
    print(f"falsos_negativos   : {false_negatives}")
    print(f"falsos_positivos   : {false_positives}")
    print(f"acuracia           : {precision}%")
    print(f"tempo_total_seg    : {total_time}")
    print(f"media_ms           : {avg_time_ms}")
    print(f"log_erros          : {log_path}")

    return {
    "type": "RG_OUTROS",
    "iterations": iterations,
    "total_time_sec": total_time,
    "avg_time_ms": avg_time_ms,
    "found_issues": hits,
    "errors_count": total_errors,
    "precision": f"{precision}%",
    }

if __name__ == "__main__":
    run_benchmark(2000)
