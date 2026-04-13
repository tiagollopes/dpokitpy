import sys
import os
import time
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from dpokitpy.guard import Guard

fake = Faker('pt_BR')


def generate_valid_cnh():
    base = [random.randint(0, 9) for _ in range(9)]

    sum1 = 0
    weight = 9
    for i in range(9):
        sum1 += base[i] * weight
        weight -= 1

    dv1 = sum1 % 11
    if dv1 >= 10:
        dv1 = 0

    sum2 = 0
    weight = 1
    for i in range(9):
        sum2 += base[i] * weight
        weight += 1

    sum2 += dv1 * 9

    dv2 = sum2 % 11
    if dv2 >= 10:
        dv2 = 0

    digits = "".join(map(str, base)) + str(dv1) + str(dv2)
    return digits


def generate_invalid_cnh():
    while True:
        cnh = "".join(str(random.randint(0, 9)) for _ in range(11))
        if cnh != cnh[0] * 11:
            if not is_generated_cnh_valid(cnh):
                return cnh


def is_generated_cnh_valid(cnh: str) -> bool:
    nums = [int(d) for d in cnh]

    sum1 = 0
    weight = 9
    for i in range(9):
        sum1 += nums[i] * weight
        weight -= 1

    dv1 = sum1 % 11
    if dv1 >= 10:
        dv1 = 0

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


def run_benchmark(iterations=2000):
    guard = Guard(country="BR")

    print(f"--- Iniciando Stress Test de CNH ({iterations} amostras) ---")

    samples = []

    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3))

        if choice == 1:
            cnh = generate_valid_cnh()
            samples.append((f"CNH: {cnh}", True, "CNH Válida"))

        elif choice == 2:
            cnh = generate_invalid_cnh()
            samples.append((f"CNH inválida {cnh}", False, "CNH Inválida"))

        else:
            fake_num = str(fake.random_number(digits=11, fix_len=True))
            samples.append((f"Protocolo {fake_num}", False, "Número Aleatório"))

    errors = []
    found_issues_count = 0

    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        found_valid = [i for i in result.issues if i.type == "CNH" and i.valid]

        if found_valid:
            found_issues_count += len(found_valid)

        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")
        elif not should_find and found_valid:
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}'")

    end_time = time.perf_counter()

    log_path = os.path.join(os.path.dirname(__file__), "erros_cnh.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - CNH\nTotal: {iterations}\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)
    errors_count = len(errors)
    precision = round(((iterations - errors_count) / iterations) * 100, 2)

    return {
        "type": "CNH",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": found_issues_count,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }


if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK CNH ---")
    for k, v in res.items():
        print(f"{k}: {v}")
