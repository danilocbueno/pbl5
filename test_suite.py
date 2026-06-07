"""
PBL — Teste de Software: Estratégias de teste para sistemas baseados em IA
Disciplina: Teste de Aplicações Inteligentes — FT Unicamp

Este arquivo contém:
  1. PROBLEMAS      — 5 funções Python simples (o "gabarito" para referência)
  2. PROMPTS        — variações de prompt para testar consistência e robustez
  3. TESTES         — baterias de testes unitários para avaliar o código gerado
  4. RUNNER         — utilitário para executar código gerado e registrar resultados

Como usar:
  1. Para cada problema, envie cada variação de prompt ao modelo (Ollama)
  2. Cole o código gerado na função run_generated_code()
  3. Execute este arquivo: python test_suite.py
  4. Os resultados são salvos no arquivo de saída indicado (ver rodar_todos)
"""

import json
import traceback
import copy
from datetime import datetime

# =============================================================================
# SEÇÃO 1 — GABARITO (referência, não enviar ao modelo)
# =============================================================================

def gabarito_maior_numero(lista):
    return max(lista)

def gabarito_palindromo(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

def gabarito_fatorial(n):
    if n == 0 or n == 1:
        return 1
    return n * gabarito_fatorial(n - 1)

def gabarito_contar_vogais(s):
    return sum(1 for c in s.lower() if c in "aeiou")

def gabarito_dois_maiores(lista):
    s = sorted(lista, reverse=True)
    return (s[0], s[1])


# =============================================================================
# SEÇÃO 2 — PROMPTS (copie e envie ao modelo no Ollama)
# =============================================================================
#
# Para enviar ao Ollama via terminal:
#   ollama run qwen2.5-coder:1.5b "COLE O PROMPT AQUI"
#
# Salve a resposta (só o código Python) em uma variável no SEÇÃO 3.

PROMPTS = {

    # ------------------------------------------------------------------
    # PROBLEMA 1 — Maior número de uma lista
    # ------------------------------------------------------------------
    "P1_original": """
Escreva uma função Python chamada `maior_numero` que recebe uma lista de
inteiros e retorna o maior valor da lista.
""",

    "P1_reformulado": """
Implemente em Python uma função chamada `maior_numero` que, dado um array
de números inteiros, encontra e devolve o elemento de maior valor.
""",

    "P1_ingles": """
Write a Python function called `maior_numero` that takes a list of integers
and returns the largest value in the list.
""",

    "P1_verboso": """
Preciso de uma função Python. O nome deve ser `maior_numero`. Ela vai receber
como parâmetro uma lista contendo números inteiros (positivos, negativos ou
zero). O retorno deve ser o número mais alto presente nessa lista. Não precisa
tratar lista vazia.
""",

    "P1_vago": """
Função Python `maior_numero` que retorna o maior elemento de uma lista.
""",

    "P1_com_ruido": """
Estou aprendendo estruturas de dados em Python. Por sinal, o algoritmo de busca
do maior elemento foi estudado por Knuth no livro TAOCP. De qualquer forma,
escreva uma função chamada `maior_numero` que recebe uma lista de inteiros e
retorna o maior valor.
""",

    # ------------------------------------------------------------------
    # PROBLEMA 2 — Verificar palíndromo
    # ------------------------------------------------------------------
    "P2_original": """
Escreva uma função Python chamada `palindromo` que recebe uma string e
retorna True se ela for um palíndromo (igual lida de trás pra frente,
ignorando maiúsculas e espaços), ou False caso contrário.
""",

    "P2_reformulado": """
Crie uma função Python `palindromo` que verifica se uma palavra ou frase
é um palíndromo. Desconsidere diferenças entre maiúsculas e minúsculas e
espaços. Retorne True ou False.
""",

    "P2_ingles": """
Write a Python function called `palindromo` that checks whether a string
is a palindrome. Ignore case and spaces. Return True or False.
""",

    "P2_vago": """
Função Python `palindromo` que checa palíndromo, ignora maiúsculas e espaços.
""",

    "P2_verboso": """
Preciso de uma função Python. O nome deve ser `palindromo`. Ela vai receber
como parâmetro uma string qualquer, que pode ter letras maiúsculas, minúsculas
e espaços. O retorno deve ser True se a string for um palíndromo (igual quando
lida de trás para frente), ou False caso contrário. Para a comparação, ignore
diferenças entre maiúsculas e minúsculas e desconsidere os espaços.
""",

    "P2_com_ruido": """
Estou estudando strings em Python. Aliás, a palavra palíndromo vem do grego
palindromos, que significa correr de volta. De qualquer forma, escreva uma
função chamada `palindromo` que recebe uma string e retorna True se ela for
um palíndromo, ignorando maiúsculas e espaços, ou False caso contrário.
""",

    # ------------------------------------------------------------------
    # PROBLEMA 3 — Fatorial recursivo
    # ------------------------------------------------------------------
    "P3_original": """
Escreva uma função Python chamada `fatorial` que calcula o fatorial de um
número inteiro n usando recursão. Considere que n >= 0.
""",

    "P3_reformulado": """
Implemente recursivamente em Python a função `fatorial(n)` que retorna o
produto de todos os inteiros positivos de 1 até n. Para n=0, retorne 1.
""",

    "P3_ingles": """
Write a recursive Python function called `fatorial` that computes the
factorial of a non-negative integer n.
""",

    "P3_com_ruido": """
Estou aprendendo Python e preciso de ajuda com uma função. Aliás, você sabia
que o fatorial foi inventado por Euler? De qualquer forma, escreva uma função
chamada `fatorial` que calcula n! de forma recursiva para n >= 0.
""",

    "P3_verboso": """
Preciso de uma função Python. O nome deve ser `fatorial`. Ela vai receber como
parâmetro um número inteiro n, onde n é sempre maior ou igual a zero. O retorno
deve ser o fatorial de n, calculado de forma recursiva (a função deve chamar a
si mesma). O caso base é fatorial(0) = 1 e fatorial(1) = 1. Para n > 1,
fatorial(n) = n * fatorial(n-1).
""",

    "P3_vago": """
Função Python `fatorial` recursiva para n >= 0.
""",

    # ------------------------------------------------------------------
    # PROBLEMA 4 — Contar vogais
    # ------------------------------------------------------------------
    "P4_original": """
Escreva uma função Python chamada `contar_vogais` que recebe uma string e
retorna a quantidade de vogais (a, e, i, o, u) presentes nela, ignorando
maiúsculas e minúsculas.
""",

    "P4_reformulado": """
Crie em Python a função `contar_vogais` que conta quantas letras vogais
existem em uma string, sem distinção entre letras maiúsculas e minúsculas.
""",

    "P4_ingles": """
Write a Python function called `contar_vogais` that counts the number of
vowels (a, e, i, o, u) in a string, case-insensitive.
""",

    "P4_verboso": """
Preciso de uma função Python. O nome deve ser `contar_vogais`. Ela vai receber
como parâmetro uma string qualquer, que pode conter letras maiúsculas,
minúsculas, números e símbolos. O retorno deve ser um número inteiro
representando a quantidade de vogais (apenas as letras a, e, i, o, u) presentes
na string. A comparação deve ignorar diferenças entre maiúsculas e minúsculas.
Não precisa tratar o caso de string vazia de forma especial.
""",

    "P4_vago": """
Função Python `contar_vogais` que conta vogais, ignora maiúsculas.
""",

    "P4_com_ruido": """
Estou estudando processamento de strings em Python. Por sinal, as vogais
existem em praticamente todos os idiomas do mundo. De qualquer forma, escreva
uma função chamada `contar_vogais` que recebe uma string e retorna a quantidade
de vogais (a, e, i, o, u) presentes, sem distinção entre maiúsculas e minúsculas.
""",

    # ------------------------------------------------------------------
    # PROBLEMA 5 — Dois maiores números
    # ------------------------------------------------------------------
    "P5_original": """
Escreva uma função Python chamada `dois_maiores` que recebe uma lista de
inteiros (com pelo menos 2 elementos) e retorna uma tupla com os dois maiores
valores em ordem decrescente.
""",

    "P5_reformulado": """
Implemente a função Python `dois_maiores` que, dada uma lista de inteiros,
encontra os dois elementos de maior valor e os retorna como uma tupla
(maior, segundo_maior).
""",

    "P5_ingles": """
Write a Python function called `dois_maiores` that takes a list of integers
and returns a tuple with the two largest values in descending order.
""",

    "P5_verboso": """
Preciso de uma função Python. O nome deve ser `dois_maiores`. Ela vai receber
como parâmetro uma lista de números inteiros, podendo conter positivos, negativos
ou zero, garantidamente com pelo menos dois elementos. O retorno deve ser uma
tupla Python contendo exatamente dois valores: o maior e o segundo maior da
lista, nessa ordem (do maior para o menor). Pode haver duplicatas na lista.
""",

    "P5_vago": """
Função Python `dois_maiores` que retorna os dois maiores de uma lista como tupla.
""",

    "P5_com_ruido": """
Estou treinando algoritmos de ordenação em Python. Aliás, o algoritmo quicksort
foi inventado por Tony Hoare em 1959. De qualquer forma, escreva uma função
chamada `dois_maiores` que recebe uma lista de inteiros e retorna uma tupla com
os dois maiores valores em ordem decrescente.
""",
}


# =============================================================================
# SEÇÃO 3 — COLE O CÓDIGO GERADO PELOS MODELOS AQUI
# =============================================================================
# Formato: GENERATED_CODE[modelo][variante] = "def funcao(...):\n    ..."
#
# Exemplo de como preencher após rodar os prompts no Ollama:
#
# GENERATED_CODE["qwen2.5-coder"]["P1_original"] = """
# def maior_numero(lista):
#     return max(lista)
# """

GENERATED_CODE = {
    "qwen2.5-coder": {
        # Cole aqui os resultados do modelo qwen2.5-coder
        # "P1_original": "...",
        # "P1_reformulado": "...",
        # etc.
    },
    "deepseek-coder": {
        # Cole aqui os resultados do modelo deepseek-coder
    },
}


# =============================================================================
# SEÇÃO 4 — BATERIAS DE TESTES UNITÁRIOS
# =============================================================================

TEST_CASES = {

    # --- Problema 1: maior_numero ---
    "P1": {
        "funcao": "maior_numero",
        "casos": [
            {"args": [[3, 1, 4, 1, 5, 9, 2, 6]],    "esperado": 9},
            {"args": [[1]],                           "esperado": 1},
            {"args": [[-3, -1, -4, -1, -5]],         "esperado": -1},
            {"args": [[0, 0, 0]],                     "esperado": 0},
            {"args": [[100, 200, 150]],               "esperado": 200},
            {"args": [[-10, 0, 10]],                  "esperado": 10},
            {"args": [[42]],                          "esperado": 42},
            {"args": [[7, 7, 7, 7]],                  "esperado": 7},
        ],
    },

    # --- Problema 2: palindromo ---
    "P2": {
        "funcao": "palindromo",
        "casos": [
            {"args": ["arara"],        "esperado": True},
            {"args": ["python"],       "esperado": False},
            {"args": ["A man a plan a canal Panama".replace(" ", "")], "esperado": True},
            {"args": ["Arara"],        "esperado": True},
            {"args": ["racecar"],      "esperado": True},
            {"args": ["hello"],        "esperado": False},
            {"args": [""],             "esperado": True},
            {"args": ["a"],            "esperado": True},
            {"args": ["ab"],           "esperado": False},
            {"args": ["Ana"],          "esperado": True},
        ],
    },

    # --- Problema 3: fatorial ---
    "P3": {
        "funcao": "fatorial",
        "casos": [
            {"args": [0],  "esperado": 1},
            {"args": [1],  "esperado": 1},
            {"args": [2],  "esperado": 2},
            {"args": [3],  "esperado": 6},
            {"args": [4],  "esperado": 24},
            {"args": [5],  "esperado": 120},
            {"args": [10], "esperado": 3628800},
            {"args": [7],  "esperado": 5040},
        ],
    },

    # --- Problema 4: contar_vogais ---
    "P4": {
        "funcao": "contar_vogais",
        "casos": [
            {"args": ["hello"],        "esperado": 2},
            {"args": ["python"],       "esperado": 1},
            {"args": ["aeiou"],        "esperado": 5},
            {"args": ["bcdfg"],        "esperado": 0},
            {"args": ["AEIOU"],        "esperado": 5},
            {"args": ["Hello World"],  "esperado": 3},
            {"args": [""],             "esperado": 0},
            {"args": ["Unicamp"],      "esperado": 3},
            {"args": ["a"],            "esperado": 1},
            {"args": ["xyz"],          "esperado": 0},
        ],
    },

    # --- Problema 5: dois_maiores ---
    "P5": {
        "funcao": "dois_maiores",
        "casos": [
            {"args": [[3, 1, 4, 1, 5]], "esperado": (5, 4)},
            {"args": [[10, 20]],         "esperado": (20, 10)},
            {"args": [[-1, -2, -3]],     "esperado": (-1, -2)},
            {"args": [[5, 5, 5]],        "esperado": (5, 5)},
            {"args": [[1, 2, 3, 4, 5]], "esperado": (5, 4)},
            {"args": [[100, 1, 50]],     "esperado": (100, 50)},
            {"args": [[0, -1, 1]],       "esperado": (1, 0)},
        ],
    },
}

# Mapeamento: qual bateria de testes vale para qual variante de prompt
PROMPT_TO_TEST = {
    "P1_original":    "P1",
    "P1_reformulado": "P1",
    "P1_ingles":      "P1",
    "P1_verboso":     "P1",
    "P1_vago":        "P1",
    "P1_com_ruido":   "P1",
    "P2_original":    "P2",
    "P2_reformulado": "P2",
    "P2_ingles":      "P2",
    "P2_vago":        "P2",
    "P2_verboso":     "P2",
    "P2_com_ruido":   "P2",
    "P3_original":    "P3",
    "P3_reformulado": "P3",
    "P3_ingles":      "P3",
    "P3_com_ruido":   "P3",
    "P3_verboso":     "P3",
    "P3_vago":        "P3",
    "P4_original":    "P4",
    "P4_reformulado": "P4",
    "P4_ingles":      "P4",
    "P4_verboso":     "P4",
    "P4_vago":        "P4",
    "P4_com_ruido":   "P4",
    "P5_original":    "P5",
    "P5_reformulado": "P5",
    "P5_ingles":      "P5",
    "P5_verboso":     "P5",
    "P5_vago":        "P5",
    "P5_com_ruido":   "P5",
}


# =============================================================================
# SEÇÃO 5 — RUNNER: executa o código gerado e coleta resultados
# =============================================================================

def run_generated_code(codigo: str, funcao: str, args: list):
    # Bloqueia uso de input() no código gerado
    if "input(" in codigo:
        return None, "ERRO: código gerado usa input() — não é uma função pura"

    namespace = {}
    try:
        exec(codigo, namespace)
    except Exception as e:
        return None, f"ERRO DE SINTAXE: {e}"

    if funcao not in namespace:
        return None, f"FUNÇÃO '{funcao}' NÃO ENCONTRADA NO CÓDIGO GERADO"

    try:
        # Cópia profunda: impede que código gerado que muta argumentos in-place
        # (ex.: lst.sort()) corrompa permanentemente os casos em TEST_CASES,
        # contaminando execuções futuras (mesmo em runs/variantes diferentes).
        args_copia = copy.deepcopy(args)
        resultado = namespace[funcao](*args_copia)
        return resultado, None
    except Exception as e:
        return None, f"ERRO EM EXECUÇÃO: {e}\n{traceback.format_exc()}"


def avaliar_modelo(modelo: str, variante: str) -> dict:
    """
    Roda a bateria de testes para um modelo + variante de prompt.
    Retorna um dicionário com os resultados.
    """
    if variante not in PROMPT_TO_TEST:
        return {"erro": f"Variante '{variante}' não mapeada"}

    bateria_id = PROMPT_TO_TEST[variante]
    bateria = TEST_CASES[bateria_id]
    funcao = bateria["funcao"]
    codigo = GENERATED_CODE.get(modelo, {}).get(variante, "")

    if not codigo.strip():
        return {
            "modelo": modelo,
            "variante": variante,
            "status": "SEM_CODIGO",
            "aprovados": 0,
            "total": len(bateria["casos"]),
            "taxa": 0.0,
            "detalhes": [],
        }

    detalhes = []
    aprovados = 0

    for i, caso in enumerate(bateria["casos"]):
        resultado, erro = run_generated_code(codigo, funcao, caso["args"])
        passou = (erro is None) and (resultado == caso["esperado"])
        if passou:
            aprovados += 1

        detalhes.append({
            "caso": i + 1,
            "args": str(caso["args"]),
            "esperado": str(caso["esperado"]),
            "obtido": str(resultado) if erro is None else erro,
            "passou": passou,
        })

    total = len(bateria["casos"])
    return {
        "modelo": modelo,
        "variante": variante,
        "status": "OK",
        "aprovados": aprovados,
        "total": total,
        "taxa": round(aprovados / total * 100, 1),
        "detalhes": detalhes,
    }


def rodar_todos(saida_path: str = "results.json") -> dict:
    """
    Roda todos os modelos × variantes que tiverem código preenchido.
    Salva em saida_path e imprime um resumo.
    """
    todos_resultados = []
    resumo = []

    for modelo in GENERATED_CODE:
        for variante in GENERATED_CODE[modelo]:
            r = avaliar_modelo(modelo, variante)
            todos_resultados.append(r)
            linha = (
                f"{modelo:25s} | {variante:22s} | "
                f"{r.get('aprovados', 0):2d}/{r.get('total', 0):2d} | "
                f"{r.get('taxa', 0):5.1f}%"
            )
            resumo.append(linha)

    # Imprime resumo
    print("\n" + "="*72)
    print(f"{'MODELO':25s} | {'VARIANTE':22s} | PASS | TAXA")
    print("-"*72)
    for linha in resumo:
        print(linha)
    print("="*72)

    # Calcula consistência por problema/modelo
    print("\nANÁLISE DE CONSISTÊNCIA (mesmo problema, prompts diferentes):\n")
    for modelo in GENERATED_CODE:
        for problema in ["P1", "P2", "P3", "P4", "P5"]:
            taxas = []
            for r in todos_resultados:
                if r["modelo"] == modelo and r["variante"].startswith(problema):
                    taxas.append(r.get("taxa", 0))
            if len(taxas) > 1:
                variacao = max(taxas) - min(taxas)
                print(
                    f"  {modelo:25s} | {problema} | "
                    f"taxas: {taxas} | variação: {variacao:.1f}pp"
                )

    # Salva JSON
    saida = {
        "timestamp": datetime.now().isoformat(),
        "resultados": todos_resultados,
    }
    with open(saida_path, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"\nResultados salvos em {saida_path}")
    return saida


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    print("PBL — Teste de LLMs para geração de código")
    print("Preencheu os códigos gerados em GENERATED_CODE? Rodando avaliação...\n")
    rodar_todos()
