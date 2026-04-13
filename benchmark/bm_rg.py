import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BENCHMARKS = [
    ("RJ", "bm_rg_rj.py"),
    ("ES", "bm_rg_es.py"),
    ("MG", "bm_rg_mg.py"),
    ("SP", "bm_rg_sp.py"),
    ("OUTROS", "bm_rg_outros.py"),
]


def run_benchmark(script_name: str):
    script_path = os.path.join(BASE_DIR, script_name)

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return {
        "script": script_name,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def extract_accuracy(output: str) -> str:
    for line in output.splitlines():
        if "acuracia" in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                return parts[1].strip()
    return "N/A"


def main():
    print("\n========== BENCHMARK MASTER RG ==========\n")

    summary = []

    for label, script in BENCHMARKS:
        print(f"Executando {label} -> {script}")
        result = run_benchmark(script)

        if result["returncode"] != 0:
            print("ERRO")
            print(result["stderr"])
            summary.append((label, "ERRO"))
            print("-" * 50)
            continue

        print(result["stdout"])
        acc = extract_accuracy(result["stdout"])
        summary.append((label, acc))
        print("-" * 50)

    print("\n========== RESUMO FINAL ==========\n")
    for label, acc in summary:
        print(f"{label:<10} : {acc}")

    print("\n=================================\n")


if __name__ == "__main__":
    main()
