import sys
import os
import time
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from dpokitpy.guard import Guard

fake = Faker('pt_BR')


def generate_valid_pis():
    base = [random.randint(0, 9) for _ in range(10)]
    weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    total = sum(base[i] * weights[i] for i in range(10))
    remainder = total % 11
    check_digit = 0 if remainder in (0, 1) else 11 - remainder

    digits = "".join(map(str, base)) + str(check_digit)
    return digits


def format_pis(pis: str) -> str:
    return f"{pis[:3]}.{pis[3:8]}.{pis[8:10]}-{pis[10]}"


def generate_invalid_pis():
    while True:
        pis = "".join(str(random.randint(0, 9)) for _ in range(11))
        if not pis == pis[0] * 11:
            valid = generate_check_for_compare(pis[:10])
            if str(valid) != pis[10]:
                return pis


def generate_check_for_compare(first_ten: str) -> int:
    weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(first_ten[i]) * weights[i] for i in range(10))
    remainder = total % 11
    return 0 if remainder in (0, 1) else 11 - remainder


def run_benchmark(iterations=2000):
    guard = Guard(country="BR")

    print(f"--- Iniciando Stress Test de PIS ({iterations} amostras) ---")

    samples = []

    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3, 4))

        if choice == 1:
            pis = generate_valid_pis()
            samples.append((f"PIS: {format_pis(pis)}", True, "PIS com Máscara"))

        elif choice == 2:
            pis = generate_valid_pis()
            samples.append((f"Número {pis}", True, "PIS sem Máscara"))

        elif choice == 3:
            pis = generate_invalid_pis()
            samples.append((f"PIS inválido {format_pis(pis)}", False, "PIS Inválido"))

        else:
            fake_num = str(fake.random_number(digits=11, fix_len=True))
            samples.append((f"Protocolo {fake_num}", False, "Número Aleatório"))

    errors = []
    found_issues_count = 0

    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        found_valid = [i for i in result.issues if i.type == "PIS" and i.valid]

        if found_valid:
            found_issues_count += len(found_valid)

        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")
        elif not should_find and found_valid:
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}'")

    end_time = time.perf_counter()

    log_path = os.path.join(os.path.dirname(__file__), "erros_pis.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - PIS\nTotal: {iterations}\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)
    errors_count = len(errors)
    precision = round(((iterations - errors_count) / iterations) * 100, 2)

    return {
        "type": "PIS",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": found_issues_count,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }


if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK PIS ---")
    for k, v in res.items():
        print(f"{k}: {v}")
