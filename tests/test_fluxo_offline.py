"""Testa os fluxos completos SEM rede: cliente LLM falso + Langfuse desabilitado.

Valida a orquestração (spans, fallback, contagens), não a qualidade do modelo.
Nenhum resultado deste teste é resultado real do projeto.
"""

from types import SimpleNamespace

import pytest
from langfuse import Langfuse

import avaliar_intencoes
import avaliar_respostas
import pipeline_assistente
from dataset import carregar_dataset
from llm import ErroLLM, chamar_modelo
from observabilidade import mascarar_dados_sensiveis


class ClienteFalso:
    """Imita client.chat.completions.create devolvendo respostas pré-definidas por `name`."""

    def __init__(self, roteiro):
        self.roteiro = roteiro
        self.chamadas = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.chamadas.append(kwargs)
        conteudo = self.roteiro(kwargs)
        if isinstance(conteudo, Exception):
            raise conteudo
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=conteudo))])


@pytest.fixture
def langfuse(monkeypatch):
    # Sem chaves e com tracing desligado: o cliente vira no-op e nada é enviado.
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    return Langfuse(tracing_enabled=False, mask=mascarar_dados_sensiveis)


def test_chamar_modelo_converte_resposta_vazia_em_erro():
    cliente = ClienteFalso(lambda kw: "")
    with pytest.raises(ErroLLM):
        chamar_modelo(cliente, modelo="m", system="s", user="u", nome="n", temperatura=0, max_tokens=10)


def test_pipeline_compara_baseline_e_improved(langfuse):
    cliente = ClienteFalso(lambda kw: f"resposta {kw['name']}")
    respostas = pipeline_assistente.executar_interacao(
        langfuse, cliente, "modelo-teste", 1, pipeline_assistente.PROMPT_FILES, "sessao-teste",
    )
    assert respostas == {"baseline": "resposta resposta-baseline", "improved": "resposta resposta-improved"}
    assert [c["name"] for c in cliente.chamadas] == ["resposta-baseline", "resposta-improved"]
    assert cliente.chamadas[0]["messages"][1]["content"] == "Quero uma massagem relaxante para aliviar dor nas costas"


def test_intencoes_score_binario(langfuse):
    # Acerta tudo, exceto quando a pergunta fala de "cancelar" (responde lixo -> others, saída inválida).
    df = carregar_dataset()
    gabarito = dict(zip(df["pergunta_cliente"], df["intencao"]))

    def roteiro(kw):
        pergunta = kw["messages"][1]["content"]
        return "não sei" if "cancelar" in pergunta.lower() else gabarito[pergunta]

    resultados, resumo = avaliar_intencoes.executar(langfuse, ClienteFalso(roteiro), "m", df, 10, "s")
    assert resumo == {"amostra": 10, "classificadas": 10, "acertos": 9, "acuracia": 0.9,
                      "falhas_tecnicas": 0, "saidas_invalidas": 1}
    errado = [r for r in resultados if r["score"] == 0][0]
    assert errado["id"] == 5 and errado["predicted_intent"] == "others"


def test_avaliacao_com_fallback_parsing_e_falha_tecnica(langfuse):
    # Roteiro do juiz por id (via texto da pergunta): critico, revisao, adequado, parsing, técnica.
    df = carregar_dataset()
    notas = {1: "SCORE: 2 | REASON: genérica", 2: "SCORE: 3 | REASON: ok", 3: "SCORE: 5 | REASON: ótima",
             4: "nota cinco", 5: ErroLLM("timeout simulado")}
    id_por_pergunta = dict(zip(df["pergunta_cliente"], df["id"]))

    def roteiro(kw):
        if kw["name"] == "juiz":
            pergunta = kw["messages"][1]["content"].split("\n")[0].removeprefix("Pergunta do cliente: ")
            if "resposta melhorada" in kw["messages"][1]["content"]:
                return "SCORE: 4 | REASON: melhorou"
            return notas[id_por_pergunta[pergunta]]
        if kw["name"] == "resposta-fallback":
            return "resposta melhorada"
        return "resposta inicial"

    resultados, resumo = avaliar_respostas.executar(langfuse, ClienteFalso(roteiro), "m", df, 5, "s")
    severidades = [r["severidade"] for r in resultados]
    assert severidades == ["critico", "revisao", "adequado", "falha_avaliacao", "falha_avaliacao"]
    assert [r["status"] for r in resultados][3:] == ["falha_parsing", "falha_tecnica"]
    assert resultados[0]["score_fallback"] == 4
    assert resumo["fallbacks_aplicados"] == 1 and resumo["fallbacks_que_melhoraram"] == 1
    assert resumo["score_medio"] == round((2 + 3 + 5) / 3, 2)
    assert resumo["categorias_mais_frequentes_nos_criticos"] == [("massagem", 1)]
    assert resultados[0]["simple_score"]["is_long"] is False
