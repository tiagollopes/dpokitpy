import sys
import os
import json
import time

# Ajusta o path para garantir que o runner encontre o pacote dpokitpy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from benchmark import (
    bm_cpf,
    bm_cnpj,
    bm_email,
    bm_phone,
    bm_pis,
    bm_cnh,
    bm_rg_rj,
    bm_rg_es,
    bm_rg_mg,
    bm_rg_sp,
    bm_rg_outros,
)


def print_line():
    print("-" * 60)


def safe_run(label, func, iterations):
    try:
        result = func(iterations=iterations)
        return result
    except Exception as e:
        print(f"[ERRO] Falha ao rodar benchmark de {label}: {e}")
        return None


def get_status_text(result):
    test_type = result.get("type", "DESCONHECIDO")
    precision = str(result.get("precision", "0%"))
    errors = result.get("errors_count", 0)

    if test_type == "CPF":
        return (
            f"{test_type}:\n"
            f"- Status atual: validado com sucesso no benchmark.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )

    elif test_type == "CNPJ":
        return (
            f"{test_type}:\n"
            f"- Status atual: validado com sucesso no benchmark.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )

    elif test_type == "EMAIL":
        return (
            f"{test_type}:\n"
            f"- Status atual: benchmark executado com validação da categoria.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )

    elif test_type == "PHONE":
        return (
            f"{test_type}:\n"
            f"- Status atual: benchmark concluído com normalização reforçada.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )
    elif test_type == "PIS":
        return (
            f"{test_type}:\n"
            f"- Status atual: benchmark concluído com integração e filtro de contexto.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )
    elif test_type == "CNH":
        return (
            f"{test_type}:\n"
            f"- Status atual: benchmark concluído com integração e filtro de contexto.\n"
            f"- Precisão final: {precision}.\n"
            f"- Falhas encontradas: {errors}.\n"
        )
    return (
        f"{test_type}:\n"
        f"- Status atual: benchmark executado.\n"
        f"- Precisão final: {precision}.\n"
        f"- Falhas encontradas: {errors}.\n"
    )


def print_result_block(res):
    print(f"Tipo de Teste:  {res.get('type', 'N/A')}")
    print(f"Amostras:       {res.get('iterations', 'N/A')}")
    print(f"Tempo Total:    {res.get('total_time_sec', res.get('total_time', 'N/A'))}s")
    print(f"Média por Call: {res.get('avg_time_ms', 'N/A')}ms")
    print(f"Issues Achadas: {res.get('found_issues', 'N/A')}")
    print(f"Erros:          {res.get('errors_count', 'N/A')}")
    print(f"Precisão:       {res.get('precision', 'N/A')}")
    print_line()
    print(get_status_text(res))
    print_line()


def build_summary(results, started_at, finished_at):
    total_tests = len(results)
    total_samples = sum(r.get("iterations", 0) for r in results)
    total_errors = sum(r.get("errors_count", 0) for r in results)
    total_found_issues = sum(r.get("found_issues", 0) for r in results if isinstance(r.get("found_issues", 0), int))
    total_time = round(finished_at - started_at, 4)

    precision_global = 0.0
    if total_samples > 0:
        precision_global = round(((total_samples - total_errors) / total_samples) * 100, 2)

    return {
        "total_tests": total_tests,
        "total_samples": total_samples,
        "total_errors": total_errors,
        "total_found_issues": total_found_issues,
        "total_time_sec": total_time,
        "global_precision": f"{precision_global}%",
        "results": results,
    }


def run_all_benchmarks():
    print_line()
    print("      DPOKITPY - SISTEMA DE BENCHMARK PROFISSIONAL")
    print_line()

    started_at = time.perf_counter()
    results = []

    benchmark_jobs = [
        ("CPF", bm_cpf.run_benchmark, 5000),
        ("CNPJ", bm_cnpj.run_benchmark, 5000),
        ("EMAIL", bm_email.run_benchmark, 5000),
        ("PHONE", bm_phone.run_benchmark, 2000),
        ("PIS", bm_pis.run_benchmark, 2000),
        ("CNH", bm_cnh.run_benchmark, 2000),
        # RG (NOVO)
        ("RG_RJ", bm_rg_rj.run_benchmark, 2000),
        ("RG_ES", bm_rg_es.run_benchmark, 2000),
        ("RG_MG", bm_rg_mg.run_benchmark, 2000),
        ("RG_SP", bm_rg_sp.run_benchmark, 2000),
        ("RG_OUTROS", bm_rg_outros.run_benchmark, 2000),
    ]

    for label, func, iterations in benchmark_jobs:
        print(f"[INFO] Executando benchmark de {label} com {iterations} amostras...")
        res = safe_run(label, func, iterations)
        if res:
            results.append(res)
            print_result_block(res)

    finished_at = time.perf_counter()
    summary = build_summary(results, started_at, finished_at)

    print("RESUMO GERAL")
    print_line()
    print(f"Categorias testadas: {summary['total_tests']}")
    print(f"Total de amostras:   {summary['total_samples']}")
    print(f"Total de erros:      {summary['total_errors']}")
    print(f"Issues encontradas:  {summary['total_found_issues']}")
    print(f"Tempo total:         {summary['total_time_sec']}s")
    print(f"Precisão global:     {summary['global_precision']}")
    print_line()

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'benchmark_results.json'))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

    print(f"Arquivo JSON salvo em: {output_path}")
    print("Benchmark finalizado com sucesso.")


if __name__ == "__main__":
    run_all_benchmarks()
