# Etapa 3 — Avaliação automatizada

> **Pergunta-chave:** como saber, sem ler cada resposta à mão, se o assistente entende o pedido do cliente e responde bem, e o que fazer automaticamente quando ele responde mal?

**Status:** ✅ código implementado e testado offline (46 testes passando) · ⏳ **execução real pendente** (sem credenciais). O [relatório](relatorio_avaliacao.md) tem os campos prontos para os resultados reais.

## Arquivos

| Entregável | Arquivo |
|---|---|
| Prompt de classificação (7 categorias, incluindo `others`) | [prompts/classificar_intencao.md](../prompts/classificar_intencao.md) |
| Avaliação de intenção (10 linhas, score binário, spans) | [src/avaliar_intencoes.py](../src/avaliar_intencoes.py) |
| `simple_score`, parsing do juiz, severidade, resumo | [src/scoring.py](../src/scoring.py) |
| Prompt do juiz (`SCORE: X \| REASON: ...`) | [prompts/juiz_calmaria.md](../prompts/juiz_calmaria.md) |
| LLM-as-Judge, thresholds, `analyze-priority-cases`, fallback | [src/avaliar_respostas.py](../src/avaliar_respostas.py) |
| Testes | [tests/test_scoring.py](../tests/test_scoring.py) · [tests/test_fluxo_offline.py](../tests/test_fluxo_offline.py) · [tests/test_hierarquia_spans.py](../tests/test_hierarquia_spans.py) |
| Relatório de avaliação | [relatorio_avaliacao.md](relatorio_avaliacao.md) ⏳ |
| Saídas da execução (CSV e JSON) | `resultados/`, criada pelos scripts ⏳ |

## Como executar
```powershell
python src\avaliar_intencoes.py            # 10 chamadas (1 por linha)
python src\avaliar_respostas.py            # 20 chamadas + 2 por caso crítico (geração + juiz)
python -m pytest                           # testes (não chamam API)
```

## Hierarquia dos traces

```text
avaliacao-intencoes-pipeline
└── intencao-<id>
    ├── predict-intent             span → classificar-intencao [generation]
    └── evaluate-intent            evaluator · score "intent_match" (1/0)

avaliacao-respostas-pipeline
├── avaliacao-<id>                 (loop principal, uma por linha)
│   ├── gerar-resposta             generation
│   ├── simple-score               span · output: length, expected_length, is_long, mentions_expected
│   └── llm-judge                  evaluator · output: judge_score (texto), score_value (número), status
│       └── juiz                   generation
└── analyze-priority-cases         (FORA do loop)
    └── fallback-<id>              (só casos críticos)
        ├── resposta-fallback      generation (assistente_improved.md + pergunta original)
        ├── llm-judge → juiz       nova avaliação
        └── fallback-applied       event
```
A hierarquia de `avaliacao-respostas-pipeline` foi verificada com exportador em memória (`test_hierarquia_avaliacao_com_fallback`).

## Regras de decisão

| Situação | `status` | `score_value` | Severidade | Ação |
|---|---|---|---|---|
| Juiz respondeu no formato, nota 4–5 | `ok` | 4–5 | `adequado` | Nenhuma |
| Nota 3 | `ok` | 3 | `revisao` | Fila de revisão humana |
| Nota 1–2 | `ok` | 1–2 | `critico` | **Fallback** com o prompt improved + nova avaliação |
| Juiz respondeu fora do formato | `falha_parsing` | 0 | `falha_avaliacao` | Erro no span; revisão humana; **não** conta na média |
| API falhou (timeout, erro, vazio) | `falha_tecnica` | 0 | `falha_avaliacao` | Erro no span; reprocessar mais tarde |

`SCORE_THRESHOLD_REVIEW = 3` e `SCORE_THRESHOLD_FALLBACK = 2`, em [config.py](../src/config.py).

**Contagem sem ambiguidade:** `críticos + revisão (só nota 3) + adequados + falhas = total avaliado`. O "revisão" do enunciado (nota ≤ 3) aparece à parte como `revisao_total_score_ate_3` (= críticos + nota 3). Ver [DECISOES.md](../DECISOES.md#d7).
