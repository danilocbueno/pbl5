"""
coletar_respostas.py — coleta automaticamente as respostas dos modelos via Ollama API

Pré-requisito:
  1. Ollama instalado e rodando: https://ollama.com
  2. Modelos baixados:
       ollama pull qwen2.5-coder:1.5b
       ollama pull deepseek-coder:1.3b

Como usar:
  python coletar_respostas.py

O script salva o código gerado em generated_code_temp_zero.json,
que pode ser importado no test_suite.py.
"""

import json
import re
import urllib.request
import urllib.error
from test_suite import PROMPTS, PROMPT_TO_TEST

MODELOS = [
    "qwen2.5-coder:1.5b",
    "deepseek-coder:1.3b",
]

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """Você é um assistente de programação Python.
Responda APENAS com o código Python solicitado, sem explicações, sem markdown,
sem blocos de código cercados por ```. Apenas o código puro."""


def extrair_codigo(texto: str) -> str:
    """Remove blocos markdown se o modelo os incluir mesmo assim."""
    # Remove ```python ... ``` ou ``` ... ```
    texto = re.sub(r"```(?:python)?\n?(.*?)```", r"\1", texto, flags=re.DOTALL)
    return texto.strip()


def chamar_ollama(modelo: str, prompt: str) -> str:
    payload = json.dumps({
        "model": modelo,
        "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.0
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return extrair_codigo(data.get("response", ""))
    except TimeoutError:
        print(f"  TIMEOUT ao chamar Ollama (modelo pode estar sobrecarregado)")
        return ""
    except urllib.error.URLError as e:
        print(f"  ERRO ao chamar Ollama: {e}")
        print("  Verifique se o Ollama está rodando: ollama serve")
        return ""


def coletar_tudo():
    # Carrega resultados anteriores para não repetir prompts já coletados
    try:
        with open("generated_code_temp_zero.json", encoding="utf-8") as f:
            resultado = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        resultado = {}

    for modelo in MODELOS:
        chave_modelo = modelo.split(":")[0]  # "qwen2.5-coder" sem versão
        if chave_modelo not in resultado:
            resultado[chave_modelo] = {}
        print(f"\n{'='*60}")
        print(f"Modelo: {modelo}")
        print(f"{'='*60}")

        for variante, prompt in PROMPTS.items():
            # Pula se já foi coletado com sucesso
            if resultado[chave_modelo].get(variante):
                print(f"  Pulando prompt: {variante} (já coletado)")
                continue

            print(f"  Rodando prompt: {variante} ...", end=" ", flush=True)
            codigo = chamar_ollama(modelo, prompt)

            resultado[chave_modelo][variante] = codigo
            if codigo:
                print(f"OK ({len(codigo)} chars)")
            else:
                print("FALHOU (vazio)")

            # Salva após cada prompt para não perder progresso
            with open("generated_code_temp_zero.json", "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\nCódigos gerados salvos em generated_code_temp_zero.json")
    print("Para rodar os testes, execute: python rodar_testes.py")
    return resultado


if __name__ == "__main__":
    coletar_tudo()
