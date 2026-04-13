import sys
import os
import time

# Garante que o Python encontre a pasta dpokitpy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faker import Faker
from dpokitpy.guard import Guard

fake = Faker('pt_BR')

def run_benchmark(iterations=1000):
    guard = Guard(country="BR")

    print(f"--- Iniciando Stress Test de CNPJ ({iterations} amostras) ---")

    samples = []
    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3, 4, 5, 6))
        raw_cnpj = fake.cnpj() # Gera CNPJ válido com máscara (00.000.000/0000-00)
        digits_only = "".join(filter(str.isdigit, raw_cnpj))

        if choice == 1: # Padrão: 00.000.000/0000-00
            samples.append((raw_cnpj, True, "Mascara Padrão"))

        elif choice == 2: # Apenas números: 00000000000000
            samples.append((f"CNPJ:{digits_only}", True, "Apenas Números com Prefixo"))

        elif choice == 3: # Números puros no meio do texto
            samples.append((f"Empresa registro {digits_only} ativa.", True, "Apenas Números no Meio"))

        elif choice == 4: # Formato sem pontos, apenas barra e traço: 00000000/0001-00
            sujo = f"{digits_only[:8]}/{digits_only[8:12]}-{digits_only[12:]}"
            samples.append((f"Doc: {sujo}", True, "Mascara Parcial"))

        elif choice == 5: # Colado/Sujo: cnpj:00.000.000/0000-00_faturamento
            samples.append((f"cnpj:{raw_cnpj}_fat", True, "Caracteres Colados"))

        else: # Falso Positivo: Texto aleatório
            samples.append((fake.company(), False, "Texto Aleatório"))

    errors = []
    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        found_valid = [i for i in result.issues if i.type == "CNPJ" and i.valid]

        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")
        elif not should_find and found_valid:
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}' | Valor: {found_valid[0].value}")

    end_time = time.perf_counter()

    log_path = os.path.join(os.path.dirname(__file__), "erros_cnpj.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - CNPJ\nTotal: {iterations}\n")
            f.write("-" * 50 + "\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("Nenhum erro encontrado. Precisão de 100%.")

    total_time = end_time - start_time
    precision = ((iterations - len(errors)) / iterations) * 100

    total_time = round(end_time - start_time, 4)
    avg_time_ms = round(((end_time - start_time) / iterations) * 1000, 6)
    errors_count = len(errors)
    precision = round(((iterations - errors_count) / iterations) * 100, 2)

    return {
        "type": "CNPJ",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": 0,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }


if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK CNPJ ---")
    for k, v in res.items():
        print(f"{k}: {v}")
