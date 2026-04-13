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

    print(f"--- Iniciando Stress Test de CPF ({iterations} amostras) ---")

    samples = []
    for _ in range(iterations):
        choice = fake.random_element(elements=(1, 2, 3, 4, 5, 6))
        raw_cpf = fake.cpf() # Gera um CPF válido com máscara
        digits_only = "".join(filter(str.isdigit, raw_cpf))

        if choice == 1: # Padrão: 000.000.000-00
            samples.append((raw_cpf, True, "Mascara Padrão"))

        elif choice == 2: # Apenas números: 00000000000
            samples.append((f"CPF:{digits_only}", True, "Apenas Números com Prefixo"))

        elif choice == 3: # Números puros no meio do texto
            samples.append((f"O registro {digits_only} foi localizado.", True, "Apenas Números no Meio"))

        elif choice == 4: # Formato com espaços: 000 000 000 00
            spaced = f"{digits_only[:3]} {digits_only[3:6]} {digits_only[6:9]} {digits_only[9:]}"
            samples.append((f"Doc: {spaced}", True, "Com Espaços"))

        elif choice == 5: # Colado/Sujo: id000.000.000-00_ref
            samples.append((f"id{raw_cpf}_ref", True, "Caracteres Colados"))

        else: # Falso Positivo: Texto aleatório ou números que NÃO são CPF
            samples.append((fake.text(max_nb_chars=40), False, "Texto Aleatório"))

    errors = []
    start_time = time.perf_counter()

    for text, should_find, category in samples:
        result = guard.validate(text)
        # Filtra apenas CPFs que o validador considerou matematicamente válidos
        found_valid = [i for i in result.issues if i.type == "CPF" and i.valid]

        # 1. Falha em detectar (Falso Negativo)
        if should_find and not found_valid:
            errors.append(f"[FALSO NEGATIVO] Categoria: {category} | Texto: '{text}'")

        # 2. Detectou algo onde não devia (Falso Positivo)
        # Nota: Pode ocorrer se o Faker gerar números aleatórios que por coincidência passam no DV.
        elif not should_find and found_valid:
            errors.append(f"[FALSO POSITIVO] Categoria: {category} | Texto: '{text}' | Valor Achado: {found_valid[0].value}")

    end_time = time.perf_counter()

    # Gravação do Log de Depuração
    log_path = os.path.join(os.path.dirname(__file__), "erros_cpf.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        if errors:
            f.write(f"RELATÓRIO DE FALHAS - CPF\n")
            f.write(f"Total de amostras: {iterations}\n")
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
        "type": "CPF",
        "iterations": iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time_ms,
        "found_issues": 0,
        "errors_count": errors_count,
        "precision": f"{precision}%"
    }


if __name__ == "__main__":
    res = run_benchmark(2000)
    print("\n--- RESULTADO DO BENCHMARK ---")
    for k, v in res.items():
        print(f"{k}: {v}")
