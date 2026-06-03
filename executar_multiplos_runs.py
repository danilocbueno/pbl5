"""
executar_multiplos_runs.py — executa runs 2-5 com temperatura padrão e agrega
com o run 1 já existente (results_temp_default.json).

Uso:
  python executar_multiplos_runs.py

Saída:
  generated_code_run_2.json ... generated_code_run_5.json
  results_run_2.json        ... results_run_5.json
  results_agregado.json     (média ± desvio padrão das 5 runs)
"""

import json
import re
import time
import platform
import urllib.request
import urllib.error
import statistics
import test_suite
from extrair_codigo import extrair_bloco_python, validar_sintaxe

MODELOS = ["qwen2.5-coder:1.5b", "deepseek-coder:1.3b"]
OLLAMA_URL = "http://localhost:11434/api/generate"
SYSTEM_PROMPT = """Você é um assistente de programação Python.
Responda APENAS com o código Python solicitado, sem explicações, sem markdown,
sem blocos de código cercados por ```. Apenas o código puro."""


# ─── Coleta ──────────────────────────────────────────────────────────────────

def _extrair_md(texto: str) -> str:
    texto = re.sub(r"```(?:python)?\n?(.*?)```", r"\1", texto, flags=re.DOTALL)
    return texto.strip()


def chamar_ollama(modelo: str, prompt: str) -> str:
    payload = json.dumps({
        "model": modelo,
        "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return _extrair_md(data.get("response", ""))
    except TimeoutError:
        print("TIMEOUT")
        return ""
    except urllib.error.URLError as e:
        print(f"ERRO: {e}")
        return ""


def coletar_run(run_id: int) -> dict:
    """Coleta uma run completa sem cache. Salva em generated_code_run_{id}.json."""
    fname = f"generated_code_run_{run_id}.json"
    resultado = {}

    for modelo in MODELOS:
        chave = modelo.split(":")[0]
        resultado[chave] = {}
        print(f"\n{'='*56}\nRun {run_id} — {modelo}\n{'='*56}")

        for variante, prompt in test_suite.PROMPTS.items():
            print(f"  {variante:25s} ...", end=" ", flush=True)
            codigo = chamar_ollama(modelo, prompt)
            resultado[chave][variante] = codigo
            print(f"OK ({len(codigo)}c)" if codigo else "FALHOU")

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"\nSalvo em {fname}")
    return resultado


# ─── Extração ────────────────────────────────────────────────────────────────

def extrair_run(generated_code: dict) -> dict:
    """Aplica a mesma pipeline de extrair_codigo.py sobre um dict em memória."""
    limpo = {}
    for modelo, variantes in generated_code.items():
        limpo[modelo] = {}
        for variante, codigo_bruto in variantes.items():
            codigo_limpo = extrair_bloco_python(codigo_bruto) if codigo_bruto else ""
            if codigo_limpo and not validar_sintaxe(codigo_limpo):
                codigo_limpo = ""
            limpo[modelo][variante] = codigo_limpo
    return limpo


# ─── Testes ──────────────────────────────────────────────────────────────────

def rodar_testes_run(generated_code_limpo: dict) -> list:
    """Injeta código no test_suite e retorna lista de resultados."""
    test_suite.GENERATED_CODE = generated_code_limpo
    saida = test_suite.rodar_todos()
    return saida["resultados"]


# ─── Agregação ───────────────────────────────────────────────────────────────

def agregar(lista_resultados: list) -> dict:
    """
    Recebe lista de 5 listas de resultados (uma por run).
    Retorna dict {(modelo, variante): {media, desvio, min, max, runs}}.
    """
    # Indexa por (modelo, variante)
    taxas_por_combinacao: dict = {}
    for run_resultados in lista_resultados:
        for r in run_resultados:
            chave = (r["modelo"], r["variante"])
            taxas_por_combinacao.setdefault(chave, []).append(r["taxa"])

    agregado = {}
    for (modelo, variante), taxas in taxas_por_combinacao.items():
        media = round(statistics.mean(taxas), 1)
        desvio = round(statistics.stdev(taxas), 1) if len(taxas) > 1 else 0.0
        agregado[(modelo, variante)] = {
            "media": media,
            "desvio": desvio,
            "min": min(taxas),
            "max": max(taxas),
            "runs": taxas,
        }
    return agregado


def imprimir_resumo_agregado(agregado: dict):
    print("\n" + "=" * 76)
    print(f"{'MODELO':25s} | {'VARIANTE':22s} | MÉDIA  | ±σ    | RUNS")
    print("-" * 76)
    for (modelo, variante), stats in sorted(agregado.items()):
        runs_str = str([f"{t:.0f}" for t in stats["runs"]])
        print(
            f"{modelo:25s} | {variante:22s} | "
            f"{stats['media']:5.1f}% | ±{stats['desvio']:4.1f} | {runs_str}"
        )
    print("=" * 76)

    # Consistência por problema
    print("\nCONSISTÊNCIA (variação max-min entre prompts do mesmo problema):\n")
    for modelo in set(m for m, _ in agregado):
        for problema in ["P1", "P2", "P3", "P4", "P5"]:
            medias = [
                v["media"] for (m, var), v in agregado.items()
                if m == modelo and var.startswith(problema)
            ]
            if len(medias) > 1:
                variacao = max(medias) - min(medias)
                print(f"  {modelo:25s} | {problema} | médias: {medias} | variação: {variacao:.1f}pp")


def salvar_agregado(agregado: dict, fname: str = "results_agregado.json"):
    serializavel = {
        f"{modelo}|{variante}": stats
        for (modelo, variante), stats in agregado.items()
    }
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(serializavel, f, ensure_ascii=False, indent=2)
    print(f"\nAgregado salvo em {fname}")


# ─── Main ────────────────────────────────────────────────────────────────────

def imprimir_ambiente():
    print("\n" + "=" * 60)
    print("AMBIENTE DE EXECUÇÃO")
    print("=" * 60)
    print(f"  Sistema:     {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python:      {platform.python_version()}")
    print(f"  Processador: {platform.processor() or 'Apple Silicon (M4)'}")
    try:
        import urllib.request as ur
        with ur.urlopen("http://localhost:11434/api/version", timeout=3) as r:
            v = json.loads(r.read())
            print(f"  Ollama:      {v.get('version', 'local')}")
    except Exception:
        print("  Ollama:      local (versão não obtida)")
    print(f"  Modelos:     {', '.join(MODELOS)}")
    print("=" * 60 + "\n")


def main():
    t_inicio = time.time()
    todos_resultados = []

    imprimir_ambiente()

    # Run 1 — já existe em results_temp_default.json
    print("Carregando run 1 (results_temp_default.json)...")
    with open("results_temp_default.json", encoding="utf-8") as f:
        run1 = json.load(f)
    todos_resultados.append(run1["resultados"])
    print(f"  Run 1: {len(run1['resultados'])} combinações carregadas.")

    # Runs 2-5 — coletar agora
    for run_id in range(2, 6):
        t_run = time.time()
        print(f"\n{'#'*60}")
        print(f"  INICIANDO RUN {run_id}/5")
        print(f"{'#'*60}")

        generated_code = coletar_run(run_id)
        generated_code_limpo = extrair_run(generated_code)

        # Salva código limpo para referência
        with open(f"generated_code_limpo_run_{run_id}.json", "w", encoding="utf-8") as f:
            json.dump(generated_code_limpo, f, ensure_ascii=False, indent=2)

        resultados = rodar_testes_run(generated_code_limpo)

        # Salva results desta run
        with open(f"results_run_{run_id}.json", "w", encoding="utf-8") as f:
            json.dump({"run": run_id, "resultados": resultados}, f, ensure_ascii=False, indent=2)

        todos_resultados.append(resultados)
        dur_run = time.time() - t_run
        print(f"\n  Run {run_id} concluída: {len(resultados)} combinações ({dur_run/60:.1f} min).")

    # Agrega
    print("\n" + "=" * 60)
    print("AGREGANDO 5 RUNS...")
    print("=" * 60)
    agregado = agregar(todos_resultados)
    imprimir_resumo_agregado(agregado)
    salvar_agregado(agregado)

    t_total = time.time() - t_inicio
    print(f"\nTempo total (runs 2-5 + agregação): {t_total/60:.1f} minutos")
    print(f"Tempo médio por run: {(t_total - 0)/4/60:.1f} min (estimado para runs 2-5)")


if __name__ == "__main__":
    main()
