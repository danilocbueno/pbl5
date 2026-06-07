"""
rodar_testes.py — carrega generated_code_limpo_temp_zero.json e executa toda a bateria de testes

Como usar:
  1. Rode primeiro: python coletar_respostas.py
  2. Depois:        python rodar_testes.py

Gera results_temp_zero.json e imprime o resumo no terminal.
"""

import json
import sys
import test_suite

def main():
    try:
        with open("generated_code_limpo_temp_zero.json", "r", encoding="utf-8") as f:
            codigos = json.load(f)
    except FileNotFoundError:
        print("generated_code_limpo_temp_zero.json não encontrado.")
        print("Rode primeiro: python coletar_respostas.py && python extrair_codigo.py")
        sys.exit(1)

    # Injeta os códigos no test_suite
    test_suite.GENERATED_CODE = codigos

    # Roda tudo
    test_suite.rodar_todos("results_temp_zero.json")


if __name__ == "__main__":
    main()
