"""Etapa 3.2 a 3.4 — Score simples, LLM-as-Judge, thresholds e fallback.

Uso:  python src/avaliar_respostas.py [--amostra 10]

Fluxo:
1. Loop principal: para cada linha, gera a resposta com assistente_calmaria.md,
   calcula o simple_score, monta o judge_input, pede a nota ao juiz e extrai o score.
2. Fora do loop: `analyze-priority-cases` classifica a severidade de cada caso e,
   para os críticos (score <= 2), regenera a resposta com assistente_improved.md,
   reavalia com o juiz e registra o evento `fallback-applied`.
3. Imprime e salva o resumo (score médio, críticos, revisão, adequados, fallbacks,
   categorias mais frequentes nos críticos).

    avaliacao-respostas-pipeline              span raiz
    ├── avaliacao-<id>                        span (um por linha)
    │   ├── gerar-resposta                    generation
    │   ├── simple-score                      span
    │   └── llm-judge                         evaluator (judge_score + score_value)
    │       └── juiz                          generation
    └── analyze-priority-cases                span (fora do loop)
        └── fallback-<id>                     span (um por caso crítico)
            ├── resposta-fallback             generation
            ├── llm-judge                     evaluator
            │   └── juiz                      generation
            └── fallback-applied              event
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime

from langfuse import propagate_attributes

from config import (
    AMOSTRA, MAX_TOKENS_AVALIACAO, MAX_TOKENS_RESPOSTA, PASTA_RESULTADOS, PROMPT_ASSISTENTE,
    PROMPT_FALLBACK, PROMPT_JUIZ, REGENERAR_EM_FALHA_DE_AVALIACAO, SCORE_FALHA,
    SCORE_THRESHOLD_FALLBACK, SCORE_THRESHOLD_REVIEW, TAGS_BASE, TEMPERATURA_ASSISTENTE,
    TEMPERATURA_AVALIACAO, carregar_ambiente, credenciais_faltando,
)
from dataset import amostra, carregar_dataset, preprocessar_pergunta
from llm import ErroLLM, chamar_modelo, criar_cliente_openai
from observabilidade import inicializar_langfuse, marcar_erro
from prompts import carregar_prompt
from scoring import (
    STATUS_FALHA_TECNICA, STATUS_OK, classificar_severidade, extrair_score_seguro,
    montar_judge_input, precisa_fallback, resumir_resultados, simple_score,
)

logger = logging.getLogger("calmaria.avaliacao")


def gerar_resposta(cliente, modelo, system, pergunta, nome):
    return chamar_modelo(
        cliente, modelo=modelo, system=system, user=pergunta, nome=nome,
        temperatura=TEMPERATURA_ASSISTENTE, max_tokens=MAX_TOKENS_RESPOSTA,
    )


def julgar(langfuse, cliente, modelo, prompt_juiz, linha, resposta):
    """Pede a nota ao juiz dentro de um span evaluator.

    Devolve (judge_score, score_value, status). judge_score é o texto completo do
    juiz; score_value é o número extraído (0 se falhou).
    """
    judge_input = montar_judge_input(
        linha["pergunta_cliente"], linha["categoria"], linha["resposta_esperada"], resposta,
    )
    with langfuse.start_as_current_observation(name="llm-judge", as_type="evaluator", input=judge_input) as span:
        try:
            judge_score = chamar_modelo(
                cliente, modelo=modelo, system=prompt_juiz, user=judge_input, nome="juiz",
                temperatura=TEMPERATURA_AVALIACAO, max_tokens=MAX_TOKENS_AVALIACAO,
            )
        except ErroLLM as erro:
            marcar_erro(span, erro)
            return None, SCORE_FALHA, STATUS_FALHA_TECNICA

        score_value, status, erro = extrair_score_seguro(judge_score)
        span.update(output={"judge_score": judge_score, "score_value": score_value, "status": status})
        if erro:
            span.update(level="ERROR", status_message=f"Falha de parsing: {erro}")
        else:
            span.score(name="score_value", value=score_value, comment=judge_score[:500])
        return judge_score, score_value, status


def avaliar_linha(langfuse, cliente, modelo, prompts, linha):
    pergunta, _ = preprocessar_pergunta(linha["pergunta_cliente"])
    base = {"id": int(linha["id"]), "categoria": linha["categoria"], "intencao": linha["intencao"], "pergunta": pergunta}

    with langfuse.start_as_current_observation(name=f"avaliacao-{linha['id']}", as_type="span", input=pergunta) as span:
        try:
            resposta = gerar_resposta(cliente, modelo, prompts["assistente"], pergunta, "gerar-resposta")
        except ErroLLM as erro:
            marcar_erro(span, erro)
            return {**base, "resposta": None, "judge_score": None, "score_value": SCORE_FALHA,
                    "status": STATUS_FALHA_TECNICA, "simple_score": None}

        with langfuse.start_as_current_observation(name="simple-score", as_type="span") as s:
            simples = simple_score(resposta, linha["resposta_esperada"])
            s.update(output=simples)

        judge_score, score_value, status = julgar(langfuse, cliente, modelo, prompts["juiz"], linha, resposta)
        span.update(output={"resposta": resposta, "score_value": score_value, "status": status})

    return {**base, "resposta": resposta, "judge_score": judge_score, "score_value": score_value,
            "status": status, "simple_score": simples}


def analisar_casos_prioritarios(langfuse, cliente, modelo, prompts, df, resultados):
    """Span `analyze-priority-cases`: severidade de todos os casos e fallback dos críticos."""
    with langfuse.start_as_current_observation(
        name="analyze-priority-cases", as_type="span",
        metadata={"threshold_review": SCORE_THRESHOLD_REVIEW, "threshold_fallback": SCORE_THRESHOLD_FALLBACK},
    ) as span:
        for r in resultados:
            r["severidade"] = classificar_severidade(r["score_value"], r["status"])
            r["score_fallback"] = None
            if precisa_fallback(r["severidade"], REGENERAR_EM_FALHA_DE_AVALIACAO):
                aplicar_fallback(langfuse, cliente, modelo, prompts, df.loc[df["id"] == r["id"]].iloc[0], r)
        span.update(output={"severidades": {r["id"]: r["severidade"] for r in resultados}})


def aplicar_fallback(langfuse, cliente, modelo, prompts, linha, resultado):
    """Regenera com o prompt improved a partir da pergunta original e reavalia."""
    with langfuse.start_as_current_observation(
        name=f"fallback-{resultado['id']}", as_type="span",
        input={"pergunta": resultado["pergunta"], "score_original": resultado["score_value"]},
    ) as span:
        try:
            nova = gerar_resposta(cliente, modelo, prompts["fallback"], resultado["pergunta"], "resposta-fallback")
        except ErroLLM as erro:
            marcar_erro(span, erro)
            return
        _, novo_score, status = julgar(langfuse, cliente, modelo, prompts["juiz"], linha, nova)
        resultado["resposta_fallback"] = nova
        resultado["score_fallback"] = novo_score if status == STATUS_OK else None
        span.create_event(
            name="fallback-applied",
            metadata={
                "id": resultado["id"], "categoria": resultado["categoria"],
                "prompt_fallback": PROMPT_FALLBACK, "score_original": resultado["score_value"],
                "score_fallback": novo_score, "status_reavaliacao": status,
            },
        )
        span.update(output={"resposta": nova, "score_fallback": novo_score})


def executar(langfuse, cliente, modelo, df, tamanho, session_id):
    prompts = {
        "assistente": carregar_prompt(PROMPT_ASSISTENTE),
        "fallback": carregar_prompt(PROMPT_FALLBACK),
        "juiz": carregar_prompt(PROMPT_JUIZ),
    }
    linhas = amostra(df, tamanho)
    with langfuse.start_as_current_observation(
        name="avaliacao-respostas-pipeline", as_type="span", input={"amostra": len(linhas)},
    ) as raiz:
        with propagate_attributes(session_id=session_id, tags=[*TAGS_BASE, "etapa-3", "llm-judge"]):
            resultados = [avaliar_linha(langfuse, cliente, modelo, prompts, l) for _, l in linhas.iterrows()]
            analisar_casos_prioritarios(langfuse, cliente, modelo, prompts, df, resultados)
        resumo = resumir_resultados(resultados)
        raiz.update(output=resumo)
    return resultados, resumo


def imprimir(resultados, resumo):
    print(f"\n{'id':>3}  {'categoria':<20} {'score':>5}  {'severidade':<16} fallback")
    for r in resultados:
        print(f"{r['id']:>3}  {r['categoria']:<20} {r['score_value']:>5}  {r['severidade']:<16} {r['score_fallback'] or '-'}")
    print("\nResumo (grupos mutuamente exclusivos: críticos + revisão + adequados + falhas = total)")
    for chave, valor in resumo.items():
        print(f"  {chave}: {valor}")


def salvar(resultados, resumo, carimbo):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    caminho_csv = PASTA_RESULTADOS / f"avaliacao_{carimbo}.csv"
    campos = ["id", "categoria", "intencao", "pergunta", "resposta", "judge_score", "score_value",
              "status", "severidade", "simple_score", "resposta_fallback", "score_fallback"]
    with open(caminho_csv, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        for r in resultados:
            escritor.writerow({**r, "simple_score": json.dumps(r["simple_score"], ensure_ascii=False)})
    caminho_json = PASTA_RESULTADOS / f"resumo_{carimbo}.json"
    caminho_json.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho_csv, caminho_json


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Avalia as respostas do assistente com LLM-as-Judge.")
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
            langfuse, criar_cliente_openai(), modelo, carregar_dataset(), args.amostra, f"avaliacao-{carimbo}",
        )
    finally:
        langfuse.flush()

    imprimir(resultados, resumo)
    print("\nArquivos:", *salvar(resultados, resumo, carimbo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
