"""Verifica a hierarquia de observações que os pipelines enviam ao Langfuse.

Os spans são capturados em memória (InMemorySpanExporter do OpenTelemetry), então
nada sai da máquina. As generations não aparecem aqui porque o cliente falso não
passa pela integração langfuse.openai; com o cliente real elas ficam dentro dos
spans indicados nos docstrings dos scripts.
"""

from types import SimpleNamespace

import pytest
from langfuse import Langfuse
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import avaliar_respostas
import pipeline_assistente
from dataset import carregar_dataset


@pytest.fixture(scope="module")
def cliente_langfuse():
    # O Langfuse guarda os recursos por public_key (singleton): um segundo Langfuse(...)
    # com a mesma chave reaproveitaria o primeiro exportador. Por isso, um por módulo.
    exportador = InMemorySpanExporter()
    langfuse = Langfuse(
        public_key="pk-lf-teste-hierarquia", secret_key="sk-lf-teste", base_url="http://127.0.0.1:9",
        tracing_enabled=True, span_exporter=exportador,
    )
    yield langfuse, exportador
    langfuse.shutdown()


@pytest.fixture
def capturar(cliente_langfuse):
    _, exportador = cliente_langfuse
    exportador.clear()
    return cliente_langfuse


def cliente(conteudo_por_nome):
    def create(**kwargs):
        texto = conteudo_por_nome.get(kwargs["name"], "resposta")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=texto))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def arvore(exportador):
    """Lista (profundidade, nome, tipo) na ordem de início."""
    spans = exportador.get_finished_spans()
    por_id = {s.context.span_id: s for s in spans}
    linhas = []
    for s in sorted(spans, key=lambda s: s.start_time):
        profundidade, pai = 0, s.parent
        while pai is not None and pai.span_id in por_id:
            profundidade, pai = profundidade + 1, por_id[pai.span_id].parent
        linhas.append((profundidade, s.name, s.attributes.get("langfuse.observation.type")))
    return linhas, {s.name: s for s in spans}


def test_hierarquia_pipeline_assistente(capturar):
    langfuse, exportador = capturar
    pipeline_assistente.executar_interacao(langfuse, cliente({}), "m", 1, pipeline_assistente.PROMPT_FILES, "sessao-t")
    langfuse.flush()
    linhas, por_nome = arvore(exportador)
    assert linhas == [
        (0, "assistente-recomendacao-pipeline", "span"),
        (1, "load-dataset", "span"),
        (1, "preprocessing", "span"),
        (1, "prompt-baseline", "span"),
        (2, "load-prompt", "span"),
        (1, "prompt-improved", "span"),
        (2, "load-prompt", "span"),
    ]
    raiz = por_nome["assistente-recomendacao-pipeline"].attributes
    assert raiz["user.id"] == "cliente-1" and raiz["session.id"] == "sessao-t"
    assert "langfuse.observation.input" in raiz and "langfuse.observation.output" in raiz
    assert por_nome["preprocessing"].attributes["langfuse.observation.metadata.comprimento_pergunta"] == "56"


def test_hierarquia_avaliacao_com_fallback(capturar):
    langfuse, exportador = capturar
    juiz_critico = cliente({"juiz": "SCORE: 2 | REASON: genérica"})
    avaliar_respostas.executar(langfuse, juiz_critico, "m", carregar_dataset(), 1, "sessao-t")
    langfuse.flush()
    linhas, _ = arvore(exportador)
    assert linhas == [
        (0, "avaliacao-respostas-pipeline", "span"),
        (1, "avaliacao-1", "span"),
        (2, "simple-score", "span"),
        (2, "llm-judge", "evaluator"),
        (1, "analyze-priority-cases", "span"),
        (2, "fallback-1", "span"),
        (3, "llm-judge", "evaluator"),
        (3, "fallback-applied", "event"),
    ]
