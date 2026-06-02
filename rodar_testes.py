"""
rodar_testes.py — carrega generated_code.json e executa toda a bateria de testes

Como usar:
  1. Rode primeiro: python coletar_respostas.py
  2. Depois:        python rodar_testes.py

Gera results.json e imprime o resumo no terminal.
"""

import json
import sys
import test_suite

def main():
    try:
        with open("generated_code_limpo.json", "r", encoding="utf-8") as f:
            codigos = json.load(f)
    except FileNotFoundError:
        print("generated_code.json não encontrado.")
        print("Rode primeiro: python coletar_respostas.py")
        sys.exit(1)

    # Injeta os códigos no test_suite
    test_suite.GENERATED_CODE = codigos

    # Roda tudo
    test_suite.rodar_todos()


if __name__ == "__main__":
    main()
