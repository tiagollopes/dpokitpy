import os
import sys
import time
import random

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


def generate_valid_mg_rg() -> str:
    use_x = random.choice([True, False])

    if use_x:
        base_len = random.choice([7, 8])
        return generate_non_repeated_digits(base_len) + "X"

    total_len = random.choice([7, 8, 9])
    return generate_non_repeated_digits(total_len)


def generate_invalid_mg_rg() -> str:
    invalid_options = [
        "1111111",
        "0000000",
        "99999999",
        "123",
        "1234567890",
        "ABCDEFGH",
        "12X34567",
        "X1234567",
        "1234567XX",
        "00000000X",
        "11111111X",
        "01234567",
    ]
    return random.choice(invalid_options)


def generate_noise_number() -> str:
    size = random.choice([7, 8, 9, 10, 11])
    return random_digits(size)


def build_sample():
    choice = random.choice([
        "MG_VALID",
        "MG_VALID",
        "MG_VALID",
        "MG_VALID",
        "MG_VALID",
        "MG_INVALID",
        "NOISE",
        "NEGATIVE_CONTEXT",
    ])

    if choice == "MG_VALID":
        rg = generate_valid_mg_rg()
        text = random.choice([
            f"RG MG {rg}",
            f"Identidade {rg}",
            f"Documento de identidade {rg}",
            f"Carteira de identidade {rg}",
            f"Meu número de identidade é {rg}",
            f"SSP/MG {rg}",
        ])
        return text, True

    if choice == "MG_INVALID":
        rg = generate_invalid_mg_rg()
        text = random.choice([
            f"RG MG {rg}",
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
        ])
        return text, False

    if choice == "NEGATIVE_CONTEXT":
        rg = generate_valid_mg_rg()
        text = random.choice([
            f"Protocolo {rg}",
            f"Pedido {rg}",
            f"Token {rg}",
            f"Código {rg}",
        ])
        return text, False

    return "RG MG 11111111", False


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
        found_valid = [i for i in result.issues if i.type == "RG" and i.valid]

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

    log_path = os.path.join(os.path.dirname(__file__), "erros_rg_mg.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write("RELATÓRIO DE FALHAS - RG MG\n")
            f.write(f"Total de amostras: {iterations}\n")
            f.write(f"Falsos negativos: {false_negatives}\n")
            f.write(f"Falsos positivos: {false_positives}\n\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    print("\n--- RESULTADO BENCHMARK RG MG ---")
    print(f"amostras           : {iterations}")
    print(f"hits               : {hits}")
    print(f"falsos_negativos   : {false_negatives}")
    print(f"falsos_positivos   : {false_positives}")
    print(f"acuracia           : {precision}%")
    print(f"tempo_total_seg    : {total_time}")
    print(f"media_ms           : {avg_time_ms}")
    print(f"log_erros          : {log_path}")

    return {
    "type": "RG_MG",
    "iterations": iterations,
    "total_time_sec": total_time,
    "avg_time_ms": avg_time_ms,
    "found_issues": hits,
    "errors_count": total_errors,
    "precision": f"{precision}%",
    }

if __name__ == "__main__":
    run_benchmark(2000)
