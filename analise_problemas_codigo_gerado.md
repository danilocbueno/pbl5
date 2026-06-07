# Análise dos problemas encontrados no código gerado

## Resposta direta

**Sim — a maior parte dos problemas não está na lógica do algoritmo, e sim em
sintaxe, formatação e nomenclatura.** Das ~20 combinações que falharam (total
ou parcialmente) sob temperatura zero, apenas **9** envolvem um erro real no
*algoritmo* em si (Seção 2). As demais falham por: código genuinamente
malformado (sintaxe inválida), nome de função diferente do pedido no
*prompt*, ou formatação/prosa ao redor de um código que, isolado, está correto.
O mesmo padrão se confirma nas cinco execuções com temperatura padrão: os
"achados" mais reveladores (Seção 3) são, de novo, predominantemente
estruturais — não de lógica.

Esta análise cobre o experimento de **temperatura zero** (determinístico — um
único exemplar por combinação, o que permite listar exaustivamente) e cita os
principais achados estruturais e de lógica observados nas cinco execuções com
**temperatura padrão**.

---

## 1. Problemas de sintaxe, formatação e nomenclatura (não são bugs de lógica)

### 1.1 Sintaxe genuinamente inválida

Casos em que o próprio código gerado pelo modelo — não a extração — contém um
erro estrutural que o `ast.parse` rejeita.

| Modelo / Variante | Código gerado (trecho relevante) | Teste / erro | Explicação |
|---|---|---|---|
| `deepseek-coder` \| `P1_verboso` (T=0) | ```python\ndef maior_numero(*args):\n    return max(args) if args else None\n    `max() é um método que encontra o máximo...\n``` | `ast.parse`: `invalid syntax` (linha 3) | O modelo despeja uma explicação em prosa **dentro do corpo da função**, na indentação do `return`, abrindo a linha com um acento grave (`` ` ``) como se iniciasse um bloco *markdown*. Função em si correta; bloco completo, inválido. |
| `deepseek-coder` \| `P2_vago` (T=0) | ```python\ndef is_anagram(s1, s2):\n    return sorted(...) == \\\n           sorted([' '.join((str(ord(ch)) * int(0.5)).replace('.', '')])\n``` | `ast.parse`: `closing parenthesis ']' does not match opening parenthesis '('` | Modelo perde o controle do próprio aninhamento de parênteses/colchetes ao tentar montar uma expressão complexa — também resolve o **problema errado** (`is_anagram` em vez de `palindromo`). |
| `deepseek-coder` \| `P3_verboso` (T=0) | ```python\ndef fatorial(n):\n    if n == 0 or n == 1:\n        return 1\n     else :\n         return n * fatorial(n-1)\n``` | `ast.parse`: `unindent does not match any outer indentation level` | `else` indentado com 5 espaços, `if` com 4 — nível de indentação não corresponde a nenhum bloco aberto. |
| `deepseek-coder` \| `P4_vago` (T=0) | ```python\ndef count_consonants(text):\n    consonant = "bcdfgh...XYZ"\n    count = 0\n    text = ''.join(filter((consonant).__contains__, text))\n    count = len(''.join(filter((consonant).__contains__, text\n``` | `ast.parse`: `'(' was never closed` | O modelo abre uma chamada `len(...filter(...)` e nunca a fecha — também resolve o problema errado (conta consoantes, não vogais). |
| `deepseek-coder` \| `P3_original` (run 1) | ```python\ndef fatorial(n):\n    if not isinstance(n, int) or n < 0:\n        raise ValueError(...)\n    return 1 if (n == 0 else n * fatorial(n-1))\n``` | `ast.parse`: `invalid syntax` | Operador ternário malformado: o modelo confunde a sintaxe do Python (`X if cond else Y`) com a de outras linguagens (`cond ? a : b`), colocando o `else` dentro dos parênteses da condição. |
| `deepseek-coder` \| `P5_vago` (run 1, temp. padrão) | ```python\ndef dois_maiores(lst):\n    lst = [x for x in set([int(y) if isinstance(y, str) and y[0] != '-'\n           else float('-inf')]) | sort(), 2)]))]))))) \n``` | `ast.parse`: `closing parenthesis ')' does not match opening parenthesis '['` | Tentando compor uma *list comprehension* aninhada com conversões de tipo, o modelo perde completamente o controle da própria construção, terminando em seis fechamentos sem abertura correspondente. |

> Nestes seis casos não há separação possível entre "código" e "prosa" a ser
> corrigida pela extração — o erro está na **construção sintática que o
> próprio modelo tentou escrever**. Apenas a reamostragem (sob temperatura
> positiva) poderia produzir uma resposta válida; sob temperatura zero, são
> falhas estruturais reprodutíveis.

### 1.2 Nome de função diferente do especificado no *prompt*

O padrão mais recorrente entre as falhas do `deepseek-coder`: o modelo ignora
o nome exato pedido (`palindromo`, `dois_maiores`) e gera variações em inglês
ou com erros de digitação — o *harness* então reporta
`FUNÇÃO '<nome esperado>' NÃO ENCONTRADA NO CÓDIGO GERADO`, zerando a taxa de
aprovação **independentemente da corretude do algoritmo**.

| Modelo / Variante | Código gerado | Teste / erro | Explicação |
|---|---|---|---|
| `deepseek-coder` \| `P2_original` (T=0) | ```python\ndef palindrome(s):\n    s = ''.join(filter(str.isalnum, s)).lower()\n    return s == s[::-1]\n``` | `args=['arara']` → `FUNÇÃO 'palindromo' NÃO ENCONTRADA` | **Lógica perfeitamente correta** (normaliza e compara com a reversa) — falha só porque a função se chama `palindrome`, não `palindromo`. |
| `deepseek-coder` \| `P2_reformulado` (T=0) | ```python\ndef palindrome(word):\n    word = ''.join(filter(str.isalnum, word)).lower()\n    return word == word[::-1]\n``` | `args=['arara']` → `FUNÇÃO 'palindromo' NÃO ENCONTRADA` | Idem — lógica correta (o próprio comentário do modelo até menciona "palindromo" como nome pretendido!), mas a função foi escrita como `palindrome`. |
| `deepseek-coder` \| `P2_com_ruido` (T=0) | ```python\ndef palindrome(s):\n    s = ''.join(filter(str.isalnum, s)).lower()\n    return s == s[::-1]\n``` | `args=['arara']` → `FUNÇÃO 'palindromo' NÃO ENCONTRADA` | Mesmo padrão — terceira ocorrência de `palindrome` em vez de `palindromo`, lógica correta. |
| `deepseek-coder` \| `P5_com_ruido` (T=0) | ```python\ndef dos_maiores(numeros):\n    numeros = list(set(numeros))\n    if len(numeros) < 2:\n        return None, None\n    ...\n``` | `args=[[1,1,3,4,5]]` → `FUNÇÃO 'dois_maiores' NÃO ENCONTRADA` | Erro de digitação: `dos_maiores` em vez de `dois_maiores`. |
| `deepseek-coder` \| `P5_com_ruido` (run 1, temp. padrão) | ```python\ndef duas_maiores(lst):\n    lst = list(set(lst))\n    lst.sort(reverse=True)\n    return (lst[0], lst[1])\n``` | `FUNÇÃO 'dois_maiores' NÃO ENCONTRADA` | Variação `duas_maiores`. |
| `deepseek-coder` \| `P5_vago` (run 5, temp. padrão) | ```python\ndef duos_maiores(numeros):\n    if len(numeros) < 2:\n        raise ValueError(...)\n    numeros = sorted(set(numeros))\n    return (numeros[-2], numeros[-1])\n``` | `FUNÇÃO 'dois_maiores' NÃO ENCONTRADA` | Variação `duos_maiores`. |

> **Quão sistemático é esse padrão?** Levantamos o nome de função realmente
> gerado pelo `deepseek-coder` em todas as 5 execuções de temperatura padrão:
> - **P2** (esperado `palindromo`): de 30 gerações válidas, apenas **5**
>   usaram o nome correto; as demais geraram `palindrome` (13×),
>   `is_palindrome` (5×) ou `is_anagram` (2×).
> - **P5** (esperado `dois_maiores`): de 24 gerações válidas, apenas **11**
>   usaram o nome correto; as demais geraram `dos_maiores` (5×),
>   `duas_maiores` (2×) ou `duos_maiores` (1×).
>
> Ou seja: a maioria das implementações de P2 — e quase metade das de P5 —
> **resolveria o problema corretamente sob outro nome**. O modelo viola o
> "contrato de interface" (nome exato pedido), e essa violação por si só
> explica boa parte dos 0% que, à primeira vista, parecem indicar incapacidade
> de resolver o problema.

### 1.3 Formatação/prosa recuperável (falsos negativos da extração)

Casos em que o código gerado pelo modelo está **sintaticamente correto**, mas
a heurística automática de extração não conseguiu separá-lo de texto
explicativo anexado — exigindo reextração manual (arquivos `_v2` deste
trabalho). Não são falhas do modelo nem bugs de lógica, mas artefatos do
*pipeline* de extração:

- `qwen2.5-coder` \| `P1_reformulado` (T=0): a função `def maior_numero(nums): return max(nums)` está correta, mas o modelo anexa a frase `"Essa função utiliza a função built-in max()..."` que contém parênteses e por isso não é descartada pela heurística — `ast.parse` rejeita o módulo inteiro.
- Diversos casos nas 5 execuções de temperatura padrão (entre 5 e 11 por execução, variando estocasticamente) seguem o mesmo padrão: código correto seguido ou precedido de explicação em prosa que confunde a heurística de extração.

---

## 2. Problemas de lógica (bugs reais no algoritmo)

Estes são os casos em que o código está **sintaticamente válido**, tem o
**nome de função correto**, mas o **algoritmo em si produz resultado
incorreto**.

### qwen2.5-coder (3 casos — todos em P5, sob temperatura zero)

| Variante | Código gerado | Teste que falhou | Explicação |
|---|---|---|---|
| `P5_original` (14%) | ```python\ndef dois_maiores(nums):\n    return tuple(sorted(nums)[-2:])\n``` | `[3,1,4,1,5]` → esperado `(5,4)`, obtido `(4,5)` | Ordena em ordem **crescente**; pega os dois últimos, mas devolve na ordem (menor, maior) em vez de (maior, segundo maior). |
| `P5_verboso` (0%) | ```python\ndef dois_maiores(nums):\n    nums.sort(reverse=True)\n    return nums[:2]\n``` | `[5,4,3,1,1]` → esperado `(5,4)`, obtido `[5, 4]` | Ordenação correta, mas devolve **lista**, não **tupla** — o teste de igualdade `[5,4] == (5,4)` falha. |
| `P5_vago` (0%) | ```python\ndef dois_maiores(lista):\n    return tuple(sorted(set(lista))[-2:])\n``` | `[5,4,3,1,1]` → esperado `(5,4)`, obtido `(4,5)` | Dois bugs simultâneos: usa `set()` (perde duplicatas — falha em `[5,5,5]`) e ordena em ordem crescente (ordem da tupla invertida). |

### deepseek-coder (8 casos — temperatura zero + 1 da temperatura padrão)

| Variante | Código gerado | Teste que falhou | Explicação |
|---|---|---|---|
| `P2_ingles` (70%) | ```python\ndef palindromo(s):\n    return s == s[::-1]\n``` | `'AmanaplanacanalPanama'` → esperado `True`, obtido `False` | Nome correto, mas a normalização (remover espaços/maiúsculas) foi **esquecida** — só funciona para strings já normalizadas. |
| `P2_verboso` (70%) | ```python\ndef palindromo(s):\n    return s == s[::-1]\n``` | `'Arara'` → esperado `True`, obtido `False` | Mesmo bug — função com nome correto mas sem qualquer normalização (`lower`/remoção de espaços). |
| `P3_ingles` (88%) | ```python\ndef fatorial(n):\n    ...\n    elif n == 0 or n == 1:\n        return n\n``` | `fatorial(0)` → esperado `1`, obtido `0` | Caso base retorna `n` em vez de `1`: para `n=0`, devolve `0` em vez de `0! = 1`. Bug sutil — só aparece em um caso de teste. |
| `P3_com_ruido` (0%) | ```python\ndef fatorial(n):\n    if not isinstance(n, int) or n < 0:\n        return 1\n    elif n == 0:\n        return n * fatorial(n-1)\n    else:\n        return n * fatorial(n-1)\n``` | `fatorial(0)` e `fatorial(1)` → esperado `1`, obtido `0` | Caso base mal definido: `fatorial(0) = 0 * fatorial(-1)`. Como `-1 < 0` cai no primeiro `if` e retorna `1`, o resultado final é `0 * 1 = 0`. A recursão "funciona" (não trava), mas a aritmética do caso base está errada. |
| `P4_reformulado` (0%) | ```python\ndef count_consonants(string):\n    consonant = "bcdfgh...XYZ"\n    ...\n``` | `'hello'` → esperado `2`, obtido `FUNÇÃO 'contar_vogais' NÃO ENCONTRADA` | **Problema trocado**: o modelo implementou contagem de **consoantes**, não de vogais — a lógica está completamente invertida em relação ao que foi pedido (também erra o nome da função como consequência). |
| `P5_original` (71%) | ```python\ndef dois_maiores(numeros):\n    numeros = list(set(numeros))\n    if len(numeros) < 2: raise ValueError(...)\n    max1, max2 = 0, 0\n    for num in numeros[:]:\n        if num > max1:\n            max2 = max1; max1 = num\n    return (max1, max2)\n``` | `[-1,-2,-3]` → esperado `(-1,-2)`, obtido `(0, 0)`; `[5,5,5]` → `ERRO: List must contain at least two elements` | Dois bugs de lógica: (1) `max1, max2` inicializados em `0, 0` — falha quando todos os números são negativos; (2) remove duplicatas com `set()` antes de checar o tamanho — falha em listas como `[5,5,5]`, que deveriam retornar `(5,5)`. |
| `P5_reformulado` (0%) | ```python\ndef dois_maiores(numeros):\n    numeros.sort()\n    return (numeros[-1], numeros[-2]) if len(numeros) > 1 else None, max(numeros), min(numeros)\n``` | `[1,1,3,4,5]` → esperado `(5,4)`, obtido `((5,4), 5, 1)` | Erro de precedência/estrutura: a expressão monta uma **tupla de 3 elementos** `(tupla_interna, max, min)` em vez de devolver só `(maior, segundo_maior)` — o `return` não tem os parênteses que o modelo achava que tinha. |
| `P5_ingles` (86%) | ```python\ndef dois_maiores(nums):\n    nums = sorted(set(nums), reverse=True)\n    return tuple(nums[:2])\n``` | `[5,5,5]` → esperado `(5,5)`, obtido `(5,)` | Remove duplicatas com `set()` antes de ordenar — perde a informação de repetição e retorna tupla de um único elemento. |
| `P5_verboso` (86%) | ```python\ndef dois_maiores(numeros):\n    numeros = list(set(numeros))\n    if len(numeros) < 2: raise ValueError(...)\n    ...\n``` | `[5,5,5]` → esperado `(5,5)`, obtido `ERRO: List must have more than one distinct number` | Mesmo bug de deduplicação prematura — trata `[5,5,5]` como lista inválida em vez de retornar `(5,5)`. |
| `P5_vago` (0%) | ```python\ndef dois_maiores(lista):\n    ...\n    return (maior1, maior2) if len(lista) == 3 else "Lista com menos que dois elementos"\n``` | `[1,1,3,4,5]` → esperado `(5,4)`, obtido `'Lista com menos que dois elementos'` | Tipo de retorno inconsistente: só devolve a tupla correta quando a lista tem **exatamente 3 elementos**; em qualquer outro caso (incluindo listas válidas maiores), devolve uma **string** de erro com nome enganoso. |

### "Achados" adicionais de lógica/robustez nas execuções com temperatura padrão

- **`deepseek-coder` \| `P3_reformulado` (run 4)** — bug de lógica com
  consequência grave de robustez: o modelo gerou casos-base que retornam
  **strings de mensagem de erro** em vez de inteiros
  (`return 'Por favor informe número positivo'`). A linha
  `return n * fatorial(n - 1)` então executa **multiplicação de string**
  (`int * str` repete a string `n` vezes). `fatorial(10)` produziu uma string
  de ~116 milhões de caracteres, inflando o arquivo de resultados da run para
  116 MB. Nas outras quatro execuções do mesmo *prompt*, o modelo gerou
  código diferente, e o bug não se repetiu — evidência de que é genuinamente
  estocástico, não estrutural.
- **`qwen2.5-coder` \| `P2_com_ruido`** (~94% de média): em uma das cinco
  execuções, o modelo gerou uma normalização incompleta (não tratando todos
  os caracteres não alfanuméricos), causando falha pontual — mas correto nas
  demais quatro execuções e em temperatura zero.
- **`qwen2.5-coder` \| `P4_ingles`** (~86% de média, $\sigma=31$): em algumas
  execuções o modelo usou `texto.lower().count('aeiou')`, que busca a
  *substring* inteira `"aeiou"` em vez de cada vogal individualmente — bug de
  lógica que não aparece em temperatura zero (onde o mesmo prompt produz um
  laço correto).

---

## 3. Conclusão

A contagem confirma a impressão inicial:

| Categoria | Nº de casos (T=0) | Predomina em |
|---|---|---|
| Sintaxe genuinamente inválida | 6 | `deepseek-coder` |
| Nome de função incorreto | 6 | `deepseek-coder` (P2 e P5) |
| Formatação/prosa recuperável (falso negativo) | ~1 por combinação problemática, variável | ambos, mais `deepseek-coder` |
| **Bugs de lógica reais** | **9** (3 `qwen2.5-coder`, 6 `deepseek-coder` em T=0, +1 acima) | concentrados em **P5** (o problema mais difícil) e em normalizações de string (P2) |

Os bugs de lógica genuínos existem, mas são **minoritários e concentrados**:
quase todos giram em torno de **P5** (a tarefa mais complexa do conjunto —
retornar os dois maiores valores como tupla ordenada, com casos extremos de
duplicatas e negativos) ou de detalhes de **normalização de string** em P2/P4.
Os problemas que mais inflam as taxas de reprovação — sobretudo do
`deepseek-coder` — são, de fato, **estruturais**: sintaxe malformada, nomes de
função que não correspondem ao contrato pedido, e prosa misturada ao código.
Isso tem implicação direta para quem avalia LLMs de geração de código: medir
apenas a taxa de aprovação bruta superestima a frequência de "erros de
raciocínio", quando grande parte da reprovação vem de o modelo não seguir
instruções de formato/interface — um problema de *instruction-following*, não
de capacidade algorítmica.
