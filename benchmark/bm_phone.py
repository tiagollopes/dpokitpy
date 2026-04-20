import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from dpokitpy.guard import Guard

fake = Faker('pt_BR')

def run_benchmark(iterations=1000):
    guard = Guard(country="BR")

    print(f"--- Iniciando Stress Test de TELEFONE ({iterations} amostras) ---")

    samples = []

    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3, 4, 5, 6))

        ddd = str(fake.random_int(min=11, max=99))

        celular = ddd + "9" + str(fake.random_int(min=1000, max=9999)) + str(fake.random_int(min=1000, max=9999))
        fixo    = ddd + str(fake.random_int(min=2000, max=5999)) + str(fake.random_int(min=1000, max=9999))

        if choice == 1:
            samples.append((f"Telefone: ({ddd}) {celular[2:7]}-{celular[7:]}", True, "Celular máscara"))

        elif choice == 2:
            samples.append((f"Telefone: ({ddd}) {fixo[2:6]}-{fixo[6:]}", True, "Fixo máscara"))

        elif choice == 3:
            samples.append((f"Ligar para {celular}", True, "Celular bruto"))

        elif choice == 4:
            samples.append((f"WhatsApp +55 ({ddd}) {celular[2:7]}-{celular[7:]}", True, "Com DDI"))

        elif choice == 5:
            samples.append((f"Tel {ddd} {celular[2:7]}-{celular[7:]}", True, "Sem parênteses"))

        else:
            samples.append((f"Protocolo {fake.random_number(digits=11)}", False, "Falso positivo"))

    errors = []
    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        found_valid = [i for i in result.issues if i.type == "PHONE" and i.valid]

        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")
        elif not should_find and found_valid:
            # Telefones são mais permissivos, mas não devem pegar números de protocolo aleatórios
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}'")

    end_time = time.perf_counter()

    log_path = os.path.join(os.path.dirname(__file__), "erros_phone.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - TELEFONE\nTotal: {iterations}\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)
    errors_count = len(errors)
    precision = round(((iterations - errors_count) / iterations) * 100, 2)

    return {
        "type": "PHONE",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": 0,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }

if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK TELEFONE ---")
    for k, v in res.items():
        print(f"{k}: {v}")
