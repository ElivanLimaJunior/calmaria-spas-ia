"""Chamadas ao modelo via integração Langfuse-OpenAI.

`from langfuse.openai import OpenAI` é um substituto direto do cliente oficial:
cada `chat.completions.create` vira uma *generation* no Langfuse, aninhada no
span que estiver ativo no momento, com modelo, tokens, custo estimado e latência.
Os parâmetros extras `name` e `metadata` são lidos pela integração e não são
enviados à OpenAI.
"""

import openai

from config import MAX_TENTATIVAS, TIMEOUT_SEGUNDOS


class ErroLLM(RuntimeError):
    """Falha técnica: a API não respondeu, recusou a chamada ou devolveu vazio."""


def criar_cliente_openai():
    from langfuse.openai import OpenAI

    return OpenAI(timeout=TIMEOUT_SEGUNDOS, max_retries=MAX_TENTATIVAS)


def chamar_modelo(cliente, *, modelo, system, user, nome, temperatura, max_tokens, metadata=None):
    """Envia system + user ao modelo e devolve o texto da resposta.

    `nome` vira o nome da generation no Langfuse. Erros da API e respostas vazias
    são convertidos em ErroLLM, para quem chama tratar falha técnica de um jeito só.
    """
    try:
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperatura,
            max_tokens=max_tokens,
            name=nome,
            metadata=metadata or {},
        )
    except openai.APIError as erro:
        raise ErroLLM(f"Erro na API da OpenAI: {type(erro).__name__}") from erro

    if not resposta.choices or not resposta.choices[0].message.content:
        raise ErroLLM("O modelo devolveu uma resposta vazia.")
    return resposta.choices[0].message.content.strip()
