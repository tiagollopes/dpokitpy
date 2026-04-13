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

def build_valid_sp_text(rg: str) -> str:
    # se já vier mascarado, usa direto
    if "." in rg:
        masked = rg
    else:
        masked = format_sp_rg(rg[:8], rg[8])

    return random.choice([
        f"RG SP {rg}",
        f"SSP/SP {rg}",
        f"RG SP {masked}",
        f"SSP/SP {masked}",
        f"RG {masked}",
        f"Identidade {masked}",
        f"Documento de identidade {masked}",
    ])

def build_invalid_sp_text(rg: str) -> str:
    clean = rg.replace(".", "").replace("-", "").upper()

    invalid_texts = [
        f"RG SP {rg}",
        f"SSP/SP {rg}",
    ]

    # só cria versão mascarada se realmente tiver 9 chars no padrão SP
    # e mesmo assim evita o caso clássico 12.345.678-9
    if len(clean) == 9 and clean[:-1].isdigit() and clean[-1] in "0123456789X":
        masked = format_sp_rg(clean[:8], clean[8])

        # só adiciona mascarado se ele continuar inválido no validador SP
        if not masked == "12.345.678-9":
            invalid_texts.extend([
                f"RG SP {masked}",
                f"SSP/SP {masked}",
                f"RG {masked}",
                f"Identidade {masked}",
                f"Documento de identidade {masked}",
            ])

    return random.choice(invalid_texts)

def calc_sp_dv(base8: str) -> str:
    total = 0
    peso = 2

    for digit in reversed(base8):
        total += int(digit) * peso
        peso += 1

    resto = total % 11
    calc = 11 - resto

    if calc == 10:
        return "X"
    if calc == 11:
        return "0"
    return str(calc)


def format_sp_rg(base8: str, dv: str) -> str:
    full = base8 + dv
    return f"{full[0:2]}.{full[2:5]}.{full[5:8]}-{full[8]}"


def generate_valid_sp_rg(masked: bool = False) -> str:
    base8 = generate_non_repeated_digits(8)
    dv = calc_sp_dv(base8)

    if masked:
        return format_sp_rg(base8, dv)

    return base8 + dv


def generate_invalid_sp_rg() -> str:
    invalid_options = [
        "111111111",
        "000000000",
        "999999999",
        "123",
        "1234567890",
        "ABCDEFGHJ",
        "12X345678",
        "X12345678",
        "12345678XX",
        "012345678",
    ]

    if random.choice([True, False]):
        return random.choice(invalid_options)

    base8 = generate_non_repeated_digits(8)
    valid_dv = calc_sp_dv(base8)
    wrong_dvs = [x for x in "0123456789X" if x != valid_dv]
    wrong_dv = random.choice(wrong_dvs)
    return base8 + wrong_dv


def generate_noise_number() -> str:
    size = random.choice([7, 8, 9, 10, 11])
    return random_digits(size)


def build_sample():
    choice = random.choice([
        "SP_VALID",
        "SP_VALID",
        "SP_VALID",
        "SP_VALID",
        "SP_VALID",
        "SP_INVALID",
        "NOISE",
        "NEGATIVE_CONTEXT",
    ])

    if choice == "SP_VALID":
        rg = generate_valid_sp_rg(masked=random.choice([True, False]))
        text = build_valid_sp_text(rg)
        return text, True

    if choice == "SP_INVALID":
        rg = generate_invalid_sp_rg()
        text = build_invalid_sp_text(rg)
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
        rg = generate_valid_sp_rg(masked=random.choice([True, False]))
        text = random.choice([
            f"Protocolo {rg}",
            f"Pedido {rg}",
            f"Token {rg}",
            f"Código {rg}",
        ])
        return text, False

    return "RG SP 111111111", False


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

    log_path = os.path.join(os.path.dirname(__file__), "erros_rg_sp.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write("RELATÓRIO DE FALHAS - RG SP\n")
            f.write(f"Total de amostras: {iterations}\n")
            f.write(f"Falsos negativos: {false_negatives}\n")
            f.write(f"Falsos positivos: {false_positives}\n\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    print("\n--- RESULTADO BENCHMARK RG SP ---")
    print(f"amostras           : {iterations}")
    print(f"hits               : {hits}")
    print(f"falsos_negativos   : {false_negatives}")
    print(f"falsos_positivos   : {false_positives}")
    print(f"acuracia           : {precision}%")
    print(f"tempo_total_seg    : {total_time}")
    print(f"media_ms           : {avg_time_ms}")
    print(f"log_erros          : {log_path}")

    return {
    "type": "RG_SP",
    "iterations": iterations,
    "total_time_sec": total_time,
    "avg_time_ms": avg_time_ms,
    "found_issues": hits,
    "errors_count": total_errors,
    "precision": f"{precision}%",
    }

if __name__ == "__main__":
    run_benchmark(2000)

