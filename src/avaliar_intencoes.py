"""Etapa 3.1 — Classificação de intenção com score binário.

Uso:  python src/avaliar_intencoes.py [--amostra 10]

Para cada uma das N primeiras linhas: o LLM prevê a intenção (predicted_intent),
comparamos com a coluna `intencao` (ground truth) e registramos score 1/0.

    avaliacao-intencoes-pipeline            span raiz
    └── intencao-<id>                       span
        ├── predict-intent                  span
        │   └── classificar-intencao        generation (langfuse.openai)
        └── evaluate-intent                 evaluator: score binário (+ score "intent_match")
"""

import argparse
import csv
import logging
import sys
from datetime import datetime

from langfuse import propagate_attributes

from config import (
    AMOSTRA, MAX_TOKENS_AVALIACAO, PASTA_RESULTADOS, PROMPT_INTENCAO, TAGS_BASE,
    TEMPERATURA_AVALIACAO, carregar_ambiente, credenciais_faltando,
)
from dataset import amostra, carregar_dataset, preprocessar_pergunta
from llm import ErroLLM, chamar_modelo, criar_cliente_openai
from observabilidade import inicializar_langfuse, marcar_erro
from prompts import carregar_prompt
from scoring import normalizar_intencao, score_intencao

logger = logging.getLogger("calmaria.intencoes")


def avaliar_linha(langfuse, cliente, modelo, system, linha):
    """Classifica uma linha e devolve o dict de resultado (status ok ou falha_tecnica)."""
    pergunta, _ = preprocessar_pergunta(linha["pergunta_cliente"])
    resultado = {"id": int(linha["id"]), "pergunta": pergunta, "intencao": linha["intencao"]}

    with langfuse.start_as_current_observation(name=f"intencao-{linha['id']}", as_type="span", input=pergunta) as span:
        with langfuse.start_as_current_observation(name="predict-intent", as_type="span", input=pergunta) as pred:
            try:
                bruto = chamar_modelo(
                    cliente, modelo=modelo, system=system, user=pergunta, nome="classificar-intencao",
                    temperatura=TEMPERATURA_AVALIACAO, max_tokens=MAX_TOKENS_AVALIACAO,
                )
            except ErroLLM as erro:
                marcar_erro(pred, erro)
                marcar_erro(span, erro)
                return {**resultado, "predicted_intent": None, "saida_valida": False, "score": None, "status": "falha_tecnica"}
            predicted, valida = normalizar_intencao(bruto)
            pred.update(output={"bruto": bruto, "predicted_intent": predicted, "saida_valida": valida})
            if not valida:
                pred.update(level="WARNING", status_message="Saída fora da lista de intenções; tratada como others")

        with langfuse.start_as_current_observation(
            name="evaluate-intent", as_type="evaluator",
            input={"predicted_intent": predicted, "intencao": linha["intencao"]},
        ) as avaliacao:
            score = score_intencao(predicted, linha["intencao"])
            avaliacao.update(output={"score": score})
            avaliacao.score(name="intent_match", value=score, comment=f"{predicted} vs {linha['intencao']}")

        span.update(output={"predicted_intent": predicted, "score": score})
    return {**resultado, "predicted_intent": predicted, "saida_valida": valida, "score": score, "status": "ok"}


def executar(langfuse, cliente, modelo, df, tamanho, session_id):
    system = carregar_prompt(PROMPT_INTENCAO)
    linhas = amostra(df, tamanho)
    with langfuse.start_as_current_observation(
        name="avaliacao-intencoes-pipeline", as_type="span", input={"amostra": len(linhas)},
    ) as raiz:
        with propagate_attributes(session_id=session_id, tags=[*TAGS_BASE, "etapa-3", "intencao"]):
            resultados = [avaliar_linha(langfuse, cliente, modelo, system, l) for _, l in linhas.iterrows()]
        validos = [r for r in resultados if r["status"] == "ok"]
        acertos = sum(r["score"] for r in validos)
        resumo = {
            "amostra": len(resultados),
            "classificadas": len(validos),
            "acertos": acertos,
            "acuracia": round(acertos / len(validos), 2) if validos else None,
            "falhas_tecnicas": len(resultados) - len(validos),
            "saidas_invalidas": sum(not r["saida_valida"] for r in validos),
        }
        raiz.update(output=resumo)
    return resultados, resumo


def salvar(resultados, nome):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_RESULTADOS / nome
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0]))
        escritor.writeheader()
        escritor.writerows(resultados)
    return caminho


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Avalia a classificação de intenção.")
    parser.add_argument("--amostra", type=int, default=AMOSTRA)
    args = parser.parse_args(argv)

    modelo = carregar_ambiente()
    faltando = credenciais_faltando()
    if faltando:
        logger.error("Preencha no .env: %s (ver README).", ", ".join(faltando))
        return 1

    langfuse = inicializar_langfuse()
    carimbo = f"{datetime.now():%Y%m%d-%H%M%S}"
    try:
        resultados, resumo = executar(
            langfuse, criar_cliente_openai(), modelo, carregar_dataset(), args.amostra, f"intencoes-{carimbo}",
        )
    finally:
        langfuse.flush()

    for r in resultados:
        marca = "✔" if r["score"] == 1 else "✘" if r["score"] == 0 else "!"
        print(f"{marca} id {r['id']:>2}  esperado={r['intencao']:<22} previsto={r['predicted_intent']}")
    print("\nResumo:", resumo)
    print("Resultados salvos em", salvar(resultados, f"intencoes_{carimbo}.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
