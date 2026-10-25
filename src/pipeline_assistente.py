"""Etapa 2 — Pipeline instrumentado do assistente da Calmaria Spas.

Uso:
    python src/pipeline_assistente.py                # interação id=1 com assistente_calmaria.md
    python src/pipeline_assistente.py --id 17        # outra interação
    python src/pipeline_assistente.py --comparar     # baseline x improved (PROMPT_FILES) no mesmo trace
    python src/pipeline_assistente.py --comparar --quantidade 5   # 5 interações, um trace cada

Hierarquia registrada no Langfuse (um trace por interação):

    assistente-recomendacao-pipeline   span raiz: input/output do trace
    ├── load-dataset                   span
    ├── preprocessing                  span: strip() + comprimento em metadata
    └── prompt-<versao>                span (um por versão de prompt)
        ├── load-prompt                span: arquivo e tamanho do prompt
        └── resposta-<versao>          generation (criada pela integração langfuse.openai)
"""

import argparse
import logging
import sys
from datetime import datetime

from langfuse import propagate_attributes

from config import (
    DATASET, MAX_TOKENS_RESPOSTA, PROMPT_ASSISTENTE, PROMPT_FILES, TAGS_BASE,
    TEMPERATURA_ASSISTENTE, carregar_ambiente, credenciais_faltando,
)
from dataset import carregar_dataset, preprocessar_pergunta
from llm import ErroLLM, chamar_modelo, criar_cliente_openai
from observabilidade import inicializar_langfuse, marcar_erro
from prompts import carregar_prompt

logger = logging.getLogger("calmaria.pipeline")

NOME_TRACE = "assistente-recomendacao-pipeline"


def executar_interacao(langfuse, cliente, modelo, id_interacao, versoes, session_id):
    """Processa uma interação do dataset com cada versão de prompt em `versoes`.

    `versoes` é um dict {nome_da_versao: arquivo_md}. Devolve um dict com as
    respostas por versão (None quando houve falha técnica naquela versão).
    """
    with langfuse.start_as_current_observation(
        name=NOME_TRACE, as_type="span", input={"id_interacao": id_interacao, "versoes": list(versoes)},
    ) as raiz:
        with langfuse.start_as_current_observation(name="load-dataset", as_type="span") as span:
            df = carregar_dataset()
            span.update(
                output={"linhas": len(df), "colunas": list(df.columns)},
                metadata={"arquivo": DATASET.name},
            )
        linha = df.loc[df["id"] == id_interacao]
        if linha.empty:
            erro = ValueError(f"id {id_interacao} não existe no dataset")
            marcar_erro(raiz, erro)
            raise erro
        linha = linha.iloc[0]

        # Atributos de trace: valem para todas as observações criadas dentro do bloco.
        with propagate_attributes(
            session_id=session_id,
            user_id=f"cliente-{id_interacao}",  # pseudônimo sintético: o dataset não tem cliente real
            tags=[*TAGS_BASE, "etapa-2", *versoes],
            metadata={"categoria": linha["categoria"], "perfil_cliente": linha["perfil_cliente"]},
        ):
            with langfuse.start_as_current_observation(
                name="preprocessing", as_type="span", input=linha["pergunta_cliente"],
            ) as span:
                pergunta, comprimento = preprocessar_pergunta(linha["pergunta_cliente"])
                span.update(output=pergunta, metadata={"comprimento_pergunta": comprimento})

            respostas = {}
            for versao, arquivo in versoes.items():
                respostas[versao] = gerar_com_prompt(langfuse, cliente, modelo, versao, arquivo, pergunta)

        raiz.update(output={"pergunta": pergunta, "respostas": respostas})
    return respostas


def gerar_com_prompt(langfuse, cliente, modelo, versao, arquivo, pergunta):
    with langfuse.start_as_current_observation(
        name=f"prompt-{versao}", as_type="span", version=versao, metadata={"prompt_file": arquivo},
    ) as span_versao:
        with langfuse.start_as_current_observation(name="load-prompt", as_type="span") as span:
            system = carregar_prompt(arquivo)
            span.update(output={"arquivo": arquivo, "caracteres": len(system)})
        try:
            resposta = chamar_modelo(
                cliente, modelo=modelo, system=system, user=pergunta,
                nome=f"resposta-{versao}", temperatura=TEMPERATURA_ASSISTENTE,
                max_tokens=MAX_TOKENS_RESPOSTA, metadata={"prompt_version": versao},
            )
        except ErroLLM as erro:
            logger.error("Falha técnica na versão %s: %s", versao, erro)
            marcar_erro(span_versao, erro)
            return None
        span_versao.update(output=resposta)
        return resposta


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--id", type=int, default=1, help="id da primeira interação (padrão: 1)")
    parser.add_argument("--quantidade", type=int, default=1, help="quantas interações a partir do id")
    parser.add_argument("--comparar", action="store_true", help="usar PROMPT_FILES (baseline e improved)")
    return parser.parse_args(argv)


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    modelo = carregar_ambiente()
    faltando = credenciais_faltando()
    if faltando:
        logger.error("Preencha no .env: %s (ver README).", ", ".join(faltando))
        return 1

    versoes = PROMPT_FILES if args.comparar else {"calmaria": PROMPT_ASSISTENTE}
    langfuse = inicializar_langfuse()
    cliente = criar_cliente_openai()
    session_id = f"pipeline-{datetime.now():%Y%m%d-%H%M%S}"

    try:
        for id_interacao in range(args.id, args.id + args.quantidade):
            respostas = executar_interacao(langfuse, cliente, modelo, id_interacao, versoes, session_id)
            for versao, resposta in respostas.items():
                print(f"\n[id {id_interacao} · {versao}]\n{resposta}")
    finally:
        langfuse.flush()  # envia os eventos que ainda estão no buffer antes de o processo terminar
    print(f"\nSessão no Langfuse: {session_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
