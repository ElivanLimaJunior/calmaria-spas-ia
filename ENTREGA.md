# Mapa da entrega

Cada entregável do enunciado → arquivo que o atende. Legenda: ✅ concluído · ⏳ pendente (depende de credenciais) · 🖐️ ação manual fora do repositório.

> **Estado em 2026-10-25:** as 4 etapas estão implementadas. A execução com OpenAI e Langfuse está ⏳ pendente (`.env` sem credenciais, [D2](DECISOES.md#d2)).

## Etapa 1 — Governança ✅

| Entregável | Arquivo | Status |
|---|---|---|
| Inventário (≥ 4 soluções: nome, área, dados, risco, público, status) | [etapa-1-governanca/inventario_solucoes_ia.csv](etapa-1-governanca/inventario_solucoes_ia.csv) · [governanca_calmaria.xlsx](etapa-1-governanca/governanca_calmaria.xlsx) | ✅ 5 soluções · 🖐️ importar no Sheets |
| Critérios de risco; legal × boa prática; AI Act | [etapa-1-governanca/governanca_ia.md](etapa-1-governanca/governanca_ia.md) · [criterios_risco.csv](etapa-1-governanca/criterios_risco.csv) | ✅ |
| Política de uso responsável (objetivo, escopo, princípios, usos, aprovação, papéis) | [etapa-1-governanca/politica_uso_responsavel.md](etapa-1-governanca/politica_uso_responsavel.md) | ✅ |
| Matriz de riscos (≥ 6; operacional, reputacional, legal, dados) | [etapa-1-governanca/matriz_riscos.csv](etapa-1-governanca/matriz_riscos.csv) · [matriz_riscos.md](etapa-1-governanca/matriz_riscos.md) | ✅ 11 riscos |
| Fluxo de aprovação com critérios de bloqueio | [etapa-1-governanca/fluxo_aprovacao.md](etapa-1-governanca/fluxo_aprovacao.md) | ✅ Mermaid |

## Etapa 2 — Instrumentação e observabilidade ✅ código · ⏳ execução

| Entregável | Arquivo | Status |
|---|---|---|
| Ambiente: Python 3.10+, venv, dependências, `.env.example`, `.gitignore` | [requirements.txt](requirements.txt) · [.env.example](.env.example) · [.gitignore](.gitignore) · [README](README.md) (seções Instalação e Configuração) | ✅ |
| Validação da conexão (`get_client()`) | [src/verificar_conexao.py](src/verificar_conexao.py) | ✅ código · ⏳ `auth_check()` real |
| Pipeline: trace, `load-dataset`, `preprocessing` (strip + comprimento), `load-prompt`, generation, input/output, session/user/tags/metadata, `flush()` | [src/pipeline_assistente.py](src/pipeline_assistente.py) | ✅ hierarquia verificada em memória · ⏳ trace real |
| Prompts baseline e improved + `PROMPT_FILES` | [prompts/](prompts/) · [src/config.py](src/config.py) | ✅ |
| Guia de verificação no Langfuse | [etapa-2-observabilidade/README.md](etapa-2-observabilidade/README.md) | ✅ |
| Evidências (capturas) | [etapa-2-observabilidade/evidencias/](etapa-2-observabilidade/evidencias/) | ⏳ |

## Etapa 3 — Avaliação automatizada ✅ código · ⏳ execução

| Entregável | Arquivo | Status |
|---|---|---|
| Prompt de intenção (7 categorias com `others`) | [prompts/classificar_intencao.md](prompts/classificar_intencao.md) | ✅ |
| 10 linhas, `predicted_intent` × `intencao`, score binário, spans | [src/avaliar_intencoes.py](src/avaliar_intencoes.py) | ✅ código · ⏳ resultados |
| `simple_score` (length, expected_length, is_long, mentions_expected) | [src/scoring.py](src/scoring.py) | ✅ testado |
| Prompt do juiz (1–5, `SCORE: X \| REASON: ...`) | [prompts/juiz_calmaria.md](prompts/juiz_calmaria.md) | ✅ |
| judge_input, judge_score + score_value, `try/except`, fallback 0 | [src/avaliar_respostas.py](src/avaliar_respostas.py) · [src/scoring.py](src/scoring.py) | ✅ testado |
| Thresholds 3 e 2, `analyze-priority-cases` fora do loop, fallback com improved, evento `fallback-applied`, resumo com `Counter` | [src/avaliar_respostas.py](src/avaliar_respostas.py) | ✅ hierarquia verificada · ⏳ resultados |
| Relatório de avaliação | [etapa-3-avaliacao/relatorio_avaliacao.md](etapa-3-avaliacao/relatorio_avaliacao.md) | ⏳ campos a preencher |

## Etapa 4 — Estratégia de produto ✅

| Entregável | Arquivo | Status |
|---|---|---|
| AI Project Canvas (4 pilares) | [etapa-4-produto/ai_project_canvas.csv](etapa-4-produto/ai_project_canvas.csv) · [estrategia_produto.xlsx](etapa-4-produto/estrategia_produto.xlsx) | ✅ · 🖐️ importar no Sheets |
| Matriz CSD (≥ 4 por coluna) | [etapa-4-produto/matriz_csd.csv](etapa-4-produto/matriz_csd.csv) | ✅ 5 · 5 · 6 |
| Proto-persona com hipóteses | [etapa-4-produto/proto_persona.md](etapa-4-produto/proto_persona.md) | ✅ |
| Rollout 1→5→10→20→100%, shadow, métricas por frequência, ciclo de degradação | [etapa-4-produto/rollout_monitoramento.md](etapa-4-produto/rollout_monitoramento.md) | ✅ |
| Síntese executiva | [etapa-4-produto/sintese_executiva.md](etapa-4-produto/sintese_executiva.md) | ✅ estrutura · ⏳ números da avaliação |

## Checklist de validação (resultados reais de 2026-10-25)

| # | Verificação | Como | Resultado |
|---|---|---|---|
| 1 | Dataset íntegro | `tests/test_dataset.py` + inspeção com pandas | ✅ 50 × 6, ids 1–50 únicos, 0 nulos, 0 perguntas duplicadas, 6 intenções |
| 2 | Amostra de 10 cobre as 6 intenções | `test_amostra_de_10_cobre_as_6_intencoes_do_dataset` | ✅ |
| 3 | `simple_score` conforme a definição | `tests/test_scoring.py` (5 testes) | ✅ |
| 4 | Parsing do juiz: válidos, inválidos, fora da escala, decimal, vazio | `tests/test_scoring.py` | ✅ |
| 5 | Thresholds e severidade nos limites (1, 2, 3, 4, 5) | `test_classificar_severidade_limites` | ✅ |
| 6 | Falhas separadas das notas baixas; grupos somam o total | `test_falha_nao_e_tratada_como_nota_baixa`, `test_resumo_grupos_somam_o_total` | ✅ |
| 7 | Fluxo completo de avaliação com fallback, falha de parsing e falha técnica | `tests/test_fluxo_offline.py` (cliente falso) | ✅ |
| 8 | Hierarquia de spans do pipeline e da avaliação | `tests/test_hierarquia_spans.py` (exportador OTel em memória) | ✅ |
| 9 | Máscara de PII | `test_mascara_remove_identificadores` | ✅ |
| 10 | Scripts sem credenciais param com mensagem clara | Execução manual dos 4 scripts | ✅ listam as variáveis faltantes; nenhum stack trace |
| 11 | Planilhas consistentes | Geração + contagem de colunas por linha | ✅ |
| 12 | **Suíte completa** | `python -m pytest` | ✅ **46 passed** (também em ordem invertida dos módulos de fluxo) |
| 13 | Autenticação no Langfuse | `verificar_conexao.py` com chaves | ⏳ |
| 14 | Generation automática com modelo, tokens e custo | Interface do Langfuse | ⏳ |
| 15 | Resultados reais da avaliação | `avaliar_intencoes.py` e `avaliar_respostas.py` | ⏳ |
| 16 | Diagramas Mermaid renderizam | Abrir no GitHub ou no mermaid.live | ⏳ não renderizados neste ambiente (sintaxe revisada manualmente) |

## Ações manuais 🖐️
- [ ] Preencher o `.env` e rodar os itens 13 a 15.
- [ ] Preencher [relatorio_avaliacao.md](etapa-3-avaliacao/relatorio_avaliacao.md) e a seção 4 da [síntese](etapa-4-produto/sintese_executiva.md).
- [ ] Salvar as capturas em [evidencias/](etapa-2-observabilidade/evidencias/).
- [ ] Importar os `.xlsx` no Google Sheets.
- [ ] Criar o repositório no GitHub e fazer o primeiro commit (o projeto ainda não é um repositório Git).
