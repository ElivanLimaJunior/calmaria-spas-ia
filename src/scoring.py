"""Funções puras de avaliação: não chamam API, por isso são testadas em tests/.

Três tipos de resultado que NÃO devem ser confundidos:
- "ok": o juiz respondeu e a nota foi extraída (a nota pode ser baixa);
- "falha_parsing": o juiz respondeu, mas fora do formato SCORE: X | REASON: ...;
- "falha_tecnica": não houve resposta (erro de API, timeout, resposta vazia).
"""

import re
from collections import Counter

from config import (
    INTENCOES,
    LIMITE_RESPOSTA_LONGA,
    PALAVRAS_ESPERADAS,
    SCORE_FALHA,
    SCORE_THRESHOLD_FALLBACK,
    SCORE_THRESHOLD_REVIEW,
)

STATUS_OK = "ok"
STATUS_FALHA_PARSING = "falha_parsing"
STATUS_FALHA_TECNICA = "falha_tecnica"

SEVERIDADE_CRITICO = "critico"
SEVERIDADE_REVISAO = "revisao"
SEVERIDADE_ADEQUADO = "adequado"
SEVERIDADE_FALHA = "falha_avaliacao"


# --- Classificação de intenção ------------------------------------------------

def normalizar_intencao(texto):
    """Converte a saída do classificador em uma das INTENCOES.

    Aceita variações como " Consultar_Preco." ou "Categoria: reclamar".
    Devolve (intencao, valida). Saída fora da lista vira ("others", False),
    para distinguir "o modelo escolheu others" de "o modelo respondeu algo inválido".
    """
    limpo = texto.strip().lower()
    limpo = re.sub(r"^categoria\s*:\s*", "", limpo)
    limpo = limpo.strip(" .\"'`\n")
    if limpo in INTENCOES:
        return limpo, True
    return "others", False


def score_intencao(prevista, esperada):
    """Score binário: 1 se acertou, 0 se errou."""
    return int(prevista == esperada)


# --- Score simples (heurística) -----------------------------------------------

def simple_score(answer, expected_answer):
    """Heurística barata de comparação, conforme o enunciado.

    - length: caracteres da resposta gerada
    - expected_length: caracteres da resposta esperada
    - is_long: resposta gerada com mais de 200 caracteres
    - mentions_expected: alguma das 5 primeiras palavras da esperada aparece
      (como trecho de texto, em minúsculas) na resposta gerada

    Limitação conhecida: palavras curtas como "a" ou "o" estão entre as 5
    primeiras quase sempre e aparecem em quase qualquer texto, então
    mentions_expected tende a ser True. Não mede correção semântica.
    """
    resposta = answer.lower()
    primeiras = expected_answer.lower().split()[:PALAVRAS_ESPERADAS]
    return {
        "length": len(answer),
        "expected_length": len(expected_answer),
        "is_long": len(answer) > LIMITE_RESPOSTA_LONGA,
        "mentions_expected": any(palavra in resposta for palavra in primeiras),
    }


# --- LLM-as-Judge ---------------------------------------------------------------

class ErroParsingJuiz(ValueError):
    """O juiz respondeu, mas não no formato SCORE: X | REASON: ..."""


PADRAO_SCORE = re.compile(r"SCORE\s*:\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)


def montar_judge_input(pergunta, categoria, resposta_esperada, resposta_gerada):
    return (
        f"Pergunta do cliente: {pergunta}\n"
        f"Categoria: {categoria}\n"
        f"Resposta de referência: {resposta_esperada}\n"
        f"Resposta gerada pelo assistente: {resposta_gerada}"
    )


def extrair_score(judge_score):
    """Extrai o inteiro de 'SCORE: X | REASON: ...'. Levanta ErroParsingJuiz se não houver nota de 1 a 5."""
    encontrado = PADRAO_SCORE.search(judge_score or "")
    if not encontrado:
        raise ErroParsingJuiz(f"Formato inesperado: {judge_score[:80]!r}" if judge_score else "Resposta vazia do juiz")
    bruto = encontrado.group(1)
    if not bruto.isdigit():
        raise ErroParsingJuiz(f"Score não inteiro: {bruto}")
    valor = int(bruto)
    if not 1 <= valor <= 5:
        raise ErroParsingJuiz(f"Score fora da escala 1-5: {valor}")
    return valor


def extrair_score_seguro(judge_score):
    """Como extrair_score, mas devolve (score_value, status, erro) sem levantar exceção.

    Em falha de parsing, score_value = SCORE_FALHA (0), como pede o enunciado.
    """
    try:
        return extrair_score(judge_score), STATUS_OK, None
    except ErroParsingJuiz as erro:
        return SCORE_FALHA, STATUS_FALHA_PARSING, str(erro)


# --- Thresholds e severidade --------------------------------------------------

def classificar_severidade(score_value, status=STATUS_OK):
    """Grupos mutuamente exclusivos (cada caso cai em exatamente um):

    - falha_avaliacao: não houve nota válida (status != ok); o 0 é só marcador
    - critico:  1 <= score <= SCORE_THRESHOLD_FALLBACK (2)
    - revisao:  SCORE_THRESHOLD_FALLBACK < score <= SCORE_THRESHOLD_REVIEW (3)
    - adequado: score > SCORE_THRESHOLD_REVIEW (4 ou 5)

    O enunciado chama de "revisão" tudo o que é <= 3; isso equivale a
    critico + revisao e é informado à parte em resumir_resultados.
    """
    if status != STATUS_OK:
        return SEVERIDADE_FALHA
    if score_value <= SCORE_THRESHOLD_FALLBACK:
        return SEVERIDADE_CRITICO
    if score_value <= SCORE_THRESHOLD_REVIEW:
        return SEVERIDADE_REVISAO
    return SEVERIDADE_ADEQUADO


def precisa_fallback(severidade, regenerar_em_falha=False):
    return severidade == SEVERIDADE_CRITICO or (regenerar_em_falha and severidade == SEVERIDADE_FALHA)


def resumir_resultados(resultados):
    """Consolida a lista de resultados da avaliação.

    Cada item precisa de: score_value, status, severidade, categoria e,
    se houve fallback, score_fallback.
    """
    total = len(resultados)
    validos = [r for r in resultados if r["status"] == STATUS_OK]
    por_severidade = Counter(r["severidade"] for r in resultados)
    criticos = [r for r in resultados if r["severidade"] == SEVERIDADE_CRITICO]
    fallbacks = [r for r in resultados if r.get("score_fallback") is not None]
    melhoraram = [r for r in fallbacks if r["score_fallback"] > r["score_value"]]

    def media(valores):
        return round(sum(valores) / len(valores), 2) if valores else None

    return {
        "total_avaliado": total,
        "avaliacoes_validas": len(validos),
        "score_medio": media([r["score_value"] for r in validos]),
        "score_medio_incluindo_falhas_como_zero": media([r["score_value"] for r in resultados]),
        "criticos": por_severidade[SEVERIDADE_CRITICO],
        "revisao_somente_score_3": por_severidade[SEVERIDADE_REVISAO],
        "revisao_total_score_ate_3": por_severidade[SEVERIDADE_CRITICO] + por_severidade[SEVERIDADE_REVISAO],
        "adequados": por_severidade[SEVERIDADE_ADEQUADO],
        "falhas_parsing": sum(r["status"] == STATUS_FALHA_PARSING for r in resultados),
        "falhas_tecnicas": sum(r["status"] == STATUS_FALHA_TECNICA for r in resultados),
        "fallbacks_aplicados": len(fallbacks),
        "fallbacks_que_melhoraram": len(melhoraram),
        "score_medio_apos_fallback": media([r["score_fallback"] for r in fallbacks]),
        "categorias_mais_frequentes_nos_criticos": Counter(r["categoria"] for r in criticos).most_common(),
    }
