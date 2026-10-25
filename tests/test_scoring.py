import pytest

from scoring import (
    ErroParsingJuiz, SEVERIDADE_ADEQUADO, SEVERIDADE_CRITICO, SEVERIDADE_FALHA, SEVERIDADE_REVISAO,
    STATUS_FALHA_PARSING, STATUS_FALHA_TECNICA, STATUS_OK, classificar_severidade, extrair_score,
    extrair_score_seguro, normalizar_intencao, precisa_fallback, resumir_resultados, score_intencao,
    simple_score,
)


# --- simple_score -------------------------------------------------------------

def test_simple_score_campos_e_comprimentos():
    r = simple_score("Recomendo a massagem relaxante.", "Recomendo a Massagem Terapêutica Profunda")
    assert set(r) == {"length", "expected_length", "is_long", "mentions_expected"}
    assert r["length"] == 31
    assert r["expected_length"] == 41
    assert r["is_long"] is False
    assert r["mentions_expected"] is True


def test_is_long_so_acima_de_200():
    assert simple_score("x" * 200, "a")["is_long"] is False
    assert simple_score("x" * 201, "a")["is_long"] is True


def test_mentions_expected_ignora_maiusculas():
    assert simple_score("temos DRENAGEM amanhã", "Drenagem disponível")["mentions_expected"] is True


def test_mentions_expected_usa_so_as_cinco_primeiras_palavras():
    esperada = "um dois tres quatro cinco seis"
    assert simple_score("seis", esperada)["mentions_expected"] is False


def test_limitacao_palavra_curta_casa_com_qualquer_resposta():
    # Documenta a limitação: "a" está nas 5 primeiras e aparece em quase qualquer texto,
    # inclusive dentro de outras palavras ("cancelada").
    r = simple_score("Sua sessão foi cancelada.", "A Limpeza de Pele Completa custa R$150")
    assert r["mentions_expected"] is True


# --- intenção -----------------------------------------------------------------

@pytest.mark.parametrize("bruto, esperado", [
    ("consultar_preco", ("consultar_preco", True)),
    ("  Consultar_Preco.\n", ("consultar_preco", True)),
    ("Categoria: reclamar", ("reclamar", True)),
    ("others", ("others", True)),
    ("quero saber o preço", ("others", False)),
    ("", ("others", False)),
])
def test_normalizar_intencao(bruto, esperado):
    assert normalizar_intencao(bruto) == esperado


def test_score_intencao_binario():
    assert score_intencao("reclamar", "reclamar") == 1
    assert score_intencao("others", "reclamar") == 0


# --- parsing do juiz ----------------------------------------------------------

@pytest.mark.parametrize("texto, nota", [
    ("SCORE: 4 | REASON: clara e acolhedora", 4),
    ("score:5|reason: ok", 5),
    ("Avaliação\nSCORE: 1 | REASON: deu conselho médico", 1),
])
def test_extrair_score_valido(texto, nota):
    assert extrair_score(texto) == nota


@pytest.mark.parametrize("texto", [
    "Nota 4, muito boa",            # sem o rótulo SCORE
    "SCORE: 7 | REASON: ...",       # fora da escala
    "SCORE: 0 | REASON: ...",       # fora da escala
    "SCORE: 4.5 | REASON: ...",     # não inteiro
    "",
    None,
])
def test_extrair_score_invalido(texto):
    with pytest.raises(ErroParsingJuiz):
        extrair_score(texto)


def test_extrair_score_seguro_devolve_zero_e_status():
    assert extrair_score_seguro("SCORE: 3 | REASON: genérica") == (3, STATUS_OK, None)
    valor, status, erro = extrair_score_seguro("sem formato")
    assert (valor, status) == (0, STATUS_FALHA_PARSING)
    assert erro


# --- thresholds e severidade --------------------------------------------------

@pytest.mark.parametrize("score, severidade", [
    (1, SEVERIDADE_CRITICO), (2, SEVERIDADE_CRITICO),
    (3, SEVERIDADE_REVISAO),
    (4, SEVERIDADE_ADEQUADO), (5, SEVERIDADE_ADEQUADO),
])
def test_classificar_severidade_limites(score, severidade):
    assert classificar_severidade(score) == severidade


def test_falha_nao_e_tratada_como_nota_baixa():
    assert classificar_severidade(0, STATUS_FALHA_PARSING) == SEVERIDADE_FALHA
    assert classificar_severidade(0, STATUS_FALHA_TECNICA) == SEVERIDADE_FALHA


def test_precisa_fallback():
    assert precisa_fallback(SEVERIDADE_CRITICO) is True
    assert precisa_fallback(SEVERIDADE_REVISAO) is False
    assert precisa_fallback(SEVERIDADE_FALHA) is False
    assert precisa_fallback(SEVERIDADE_FALHA, regenerar_em_falha=True) is True


def _caso(score, status=STATUS_OK, categoria="massagem", fallback=None):
    return {"score_value": score, "status": status, "categoria": categoria,
            "severidade": classificar_severidade(score, status), "score_fallback": fallback}


def test_resumo_grupos_somam_o_total():
    resultados = [
        _caso(1, categoria="facial", fallback=4), _caso(2, categoria="facial", fallback=2),
        _caso(2, categoria="capilar", fallback=5), _caso(3), _caso(4), _caso(5),
        _caso(0, STATUS_FALHA_PARSING), _caso(0, STATUS_FALHA_TECNICA),
    ]
    r = resumir_resultados(resultados)
    assert r["total_avaliado"] == 8
    assert r["criticos"] + r["revisao_somente_score_3"] + r["adequados"] + r["falhas_parsing"] + r["falhas_tecnicas"] == 8
    assert (r["criticos"], r["revisao_somente_score_3"], r["revisao_total_score_ate_3"], r["adequados"]) == (3, 1, 4, 2)
    assert r["score_medio"] == round((1 + 2 + 2 + 3 + 4 + 5) / 6, 2)            # só avaliações válidas
    assert r["score_medio_incluindo_falhas_como_zero"] == round(17 / 8, 2)      # leitura literal do enunciado
    assert r["fallbacks_aplicados"] == 3
    assert r["fallbacks_que_melhoraram"] == 2
    assert r["categorias_mais_frequentes_nos_criticos"] == [("facial", 2), ("capilar", 1)]


def test_resumo_vazio_nao_quebra():
    r = resumir_resultados([])
    assert r["score_medio"] is None and r["total_avaliado"] == 0
