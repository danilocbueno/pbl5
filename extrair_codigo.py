"""
extrair_codigo.py — extrai apenas o código Python válido de respostas brutas dos modelos

O problema: modelos como deepseek-coder ignoram o system prompt e misturam
explicações em prosa junto com o código. Isso faz o exec() falhar por SyntaxError,
não porque o modelo não saiba resolver o problema.

Este script aplica uma heurística de extração linha a linha:
  - Mantém linhas que são código Python válido (def, return, if, for, etc.)
  - Descarta linhas que são claramente prosa em português ou inglês
  - Descarta linhas de print() e input() que não fazem parte da função
  - Salva o resultado em generated_code_limpo_temp_zero.json

Como usar:
  python extrair_codigo.py

Depois rode os testes com o arquivo limpo:
  python rodar_testes.py --input generated_code_limpo_temp_zero.json
"""

import json
import re
import ast
import sys

# ─── Heurísticas de classificação de linha ───────────────────────────────────

# Padrões que indicam início de prosa (não são código Python)
PADROES_PROSA = [
    r"^[A-ZÁÉÍÓÚÀÂÊÔÃÕÇ][a-záéíóúàâêôãõç].*[a-z]\s*$",  # frase começando com maiúscula
    r"^\s*#.*$",           # comentário — mantém (é válido em Python)
    r"^This ",
    r"^The ",
    r"^Note ",
    r"^Here ",
    r"^Esta ",
    r"^Essa ",
    r"^Esse ",
    r"^Este ",
    r"^Porque ",
    r"^porque ",
    r"^Retorna",
    r"^função",
    r"^A função",
    r"^O código",
]

# Tokens que indicam que a linha é Python
TOKENS_PYTHON = [
    "def ", "return ", "if ", "elif ", "else:",
    "for ", "while ", "class ", "import ",
    "try:", "except", "raise ", "with ",
    "    ", "\t",  # indentação
    "==", "!=", "<=", ">=", "+=", "-=",
    "None", "True", "False",
    "float(", "int(", "str(", "len(",
    "sorted(", "max(", "min(", "sum(",
    "isinstance(", "range(", "enumerate(",
]


def linha_e_prosa(linha: str) -> bool:
    """Retorna True se a linha parece ser prosa, não código Python."""
    stripped = linha.strip()

    # Linha vazia — mantém
    if not stripped:
        return False

    # Comentário Python — mantém
    if stripped.startswith("#"):
        return False

    # Tem tokens Python claros — mantém
    for token in TOKENS_PYTHON:
        if token in linha:
            return False

    # Parece prosa
    for padrao in PADROES_PROSA:
        if re.match(padrao, stripped):
            return True

    # Linha sem dois-pontos, sem parênteses, sem operadores — provavelmente prosa
    tem_estrutura_python = any(c in stripped for c in ["(", ")", ":", "=", "[", "]", "{", "}"])
    if not tem_estrutura_python and len(stripped.split()) > 4:
        return True

    return False


def remover_prints_e_inputs(codigo: str) -> str:
    """Remove chamadas a print() e input() fora de funções."""
    linhas = codigo.split("\n")
    resultado = []
    dentro_de_funcao = False
    nivel_indent = 0

    for linha in linhas:
        stripped = linha.strip()

        if stripped.startswith("def "):
            dentro_de_funcao = True
            nivel_indent = len(linha) - len(linha.lstrip())
            resultado.append(linha)
            continue

        if dentro_de_funcao:
            indent_atual = len(linha) - len(linha.lstrip()) if stripped else nivel_indent + 4
            if stripped and indent_atual <= nivel_indent:
                dentro_de_funcao = False

        if not dentro_de_funcao and (stripped.startswith("print(") or stripped.startswith("input(")):
            continue  # descarta print/input fora de funções

        resultado.append(linha)

    return "\n".join(resultado)


def extrair_bloco_python(texto: str) -> str:
    """
    Estratégia principal de extração:
    1. Se tem bloco ```python ... ```, usa ele
    2. Se tem linhas mistas, filtra as que parecem prosa
    3. Tenta validar a sintaxe do resultado
    """
    # Estratégia 1: bloco markdown explícito
    match = re.search(r"```(?:python)?\n?(.*?)```", texto, re.DOTALL)
    if match:
        codigo = match.group(1).strip()
        if validar_sintaxe(codigo):
            return remover_prints_e_inputs(codigo)

    # Estratégia 2: filtrar linha a linha
    linhas = texto.split("\n")
    linhas_codigo = []
    for linha in linhas:
        if not linha_e_prosa(linha):
            linhas_codigo.append(linha)

    codigo_filtrado = "\n".join(linhas_codigo).strip()
    codigo_filtrado = remover_prints_e_inputs(codigo_filtrado)

    # Remove blocos de texto solto que sobraram (sem indentação, sem tokens Python)
    linhas_finais = []
    for linha in codigo_filtrado.split("\n"):
        stripped = linha.strip()
        if not stripped:
            linhas_finais.append(linha)
            continue
        # Linha sem nenhuma estrutura Python e com múltiplas palavras — descarta
        tem_python = any(t in linha for t in ["def ", "return", "if ", "for ", "while ", "    ", "(", ")", ":", "="])
        if not tem_python and len(stripped.split()) > 5 and not stripped.startswith("#"):
            continue
        linhas_finais.append(linha)

    return "\n".join(linhas_finais).strip()


def validar_sintaxe(codigo: str) -> bool:
    """Retorna True se o código é sintaticamente válido."""
    try:
        ast.parse(codigo)
        return True
    except SyntaxError:
        return False


def processar_arquivo(caminho_entrada: str, caminho_saida: str):
    """Processa o arquivo de código bruto e salva versão limpa."""
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        dados = json.load(f)

    resultado = {}
    resumo = []

    for modelo, variantes in dados.items():
        resultado[modelo] = {}
        print(f"\n{'='*60}")
        print(f"Modelo: {modelo}")
        print(f"{'='*60}")

        for variante, codigo_bruto in variantes.items():
            codigo_limpo = extrair_bloco_python(codigo_bruto)
            sintaxe_ok = validar_sintaxe(codigo_limpo) if codigo_limpo else False

            resultado[modelo][variante] = codigo_limpo

            status = "✓ sintaxe OK" if sintaxe_ok else "✗ sintaxe inválida"
            mudou = "  (extraído)" if codigo_limpo != codigo_bruto.strip() else ""
            linha = f"  {variante:22s} | {status}{mudou}"
            print(linha)
            resumo.append({
                "modelo": modelo,
                "variante": variante,
                "sintaxe_ok": sintaxe_ok,
                "chars_antes": len(codigo_bruto),
                "chars_depois": len(codigo_limpo),
            })

    # Salva JSON limpo
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    # Relatório de sintaxe
    total = len(resumo)
    ok = sum(1 for r in resumo if r["sintaxe_ok"])
    print(f"\n{'='*60}")
    print(f"Sintaxe válida após extração: {ok}/{total}")

    invalidos = [r for r in resumo if not r["sintaxe_ok"]]
    if invalidos:
        print("\nAinda com sintaxe inválida (verificar manualmente):")
        for r in invalidos:
            print(f"  {r['modelo']:25s} | {r['variante']}")

    print(f"\nArquivo limpo salvo em: {caminho_saida}")
    return resultado


if __name__ == "__main__":
    entrada = "generated_code_temp_zero.json"
    saida = "generated_code_limpo_temp_zero.json"

    if len(sys.argv) > 1:
        entrada = sys.argv[1]
    if len(sys.argv) > 2:
        saida = sys.argv[2]

    processar_arquivo(entrada, saida)
