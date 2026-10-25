"""Inicialização do Langfuse (SDK v5) e máscara de dados pessoais.

Na v5 a instrumentação é baseada em OpenTelemetry:
- `Langfuse(...)` configura o cliente uma vez (aqui com a função de máscara);
- `get_client()` devolve um cliente que compartilha essa configuração;
- spans são criados com `start_as_current_observation(as_type="span")`
  (na v3 o método era `start_as_current_span`, que não existe mais).
"""

import re

from langfuse import Langfuse, get_client

# Identificadores diretos que não devem chegar aos traces. O dataset do projeto
# não tem nenhum, mas o chat em produção pode receber. Termos de saúde NÃO são
# mascarados aqui: isso tornaria a avaliação impossível; ver DECISOES.md (D6).
PADROES_PII = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "[TELEFONE]"),
]


def mascarar_texto(texto):
    for padrao, substituto in PADROES_PII:
        texto = padrao.sub(substituto, texto)
    return texto


def mascarar_dados_sensiveis(*, data, **kwargs):
    """Função de máscara no formato exigido pelo Langfuse (`mask=`).

    Percorre strings, listas e dicionários; o restante passa sem alteração.
    """
    if isinstance(data, str):
        return mascarar_texto(data)
    if isinstance(data, dict):
        return {k: mascarar_dados_sensiveis(data=v) for k, v in data.items()}
    if isinstance(data, list):
        return [mascarar_dados_sensiveis(data=v) for v in data]
    return data


def inicializar_langfuse():
    """Configura o cliente com a máscara e o devolve via get_client().

    As credenciais vêm das variáveis LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY e
    LANGFUSE_BASE_URL. Sem elas, o cliente fica desabilitado (não quebra o script).
    """
    Langfuse(mask=mascarar_dados_sensiveis)
    return get_client()


def marcar_erro(observacao, erro):
    """Registra um erro na observação sem expor detalhes além da mensagem."""
    observacao.update(level="ERROR", status_message=f"{type(erro).__name__}: {erro}"[:500])
