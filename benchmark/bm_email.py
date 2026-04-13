import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from dpokitpy.guard import Guard

fake = Faker('pt_BR')

def run_benchmark(iterations=1000):
    guard = Guard(country="BR")

    print(f"--- Iniciando Stress Test de EMAIL ({iterations} amostras) ---")

    samples = []
    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3, 4, 5))

        if choice == 1: # Padrão simples
            email = fake.email()
            samples.append((email, True, "Email Padrão"))

        elif choice == 2: # Com tag de filtro (+)
            email = f"user+tag{fake.random_int()}@gmail.com"
            samples.append((f"Contato: {email}", True, "Email com Tag (+)"))

        elif choice == 3: # Colado em pontuação
            email = fake.email()
            samples.append((f"Escreva para({email}).", True, "Email entre Pontuação"))

        elif choice == 4: # Subdomínios complexos
            email = f"admin@{fake.domain_name()}.{fake.tld()}.br"
            samples.append((email, True, "Email Subdomínio"))

        else: # Falso Positivo (Texto que lembra email mas é inválido)
            samples.append((f"usuario@{fake.word()}", False, "Texto Incompleto"))

    errors = []
    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        found_valid = [i for i in result.issues if i.type == "EMAIL" and i.valid]

        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")
        elif not should_find and found_valid:
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}'")

    end_time = time.perf_counter()

    log_path = os.path.join(os.path.dirname(__file__), "erros_email.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - EMAIL\nTotal: {iterations}\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)
    errors_count = len(errors)
    precision = round(((iterations - errors_count) / iterations) * 100, 2)

    return {
        "type": "EMAIL",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": 0,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }


if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK EMAIL ---")
    for k, v in res.items():
        print(f"{k}: {v}")
