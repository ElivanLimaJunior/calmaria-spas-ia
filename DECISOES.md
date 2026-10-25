# Registro de decisões do projeto

Decisões tomadas onde o enunciado é ambíguo, inconsistente ou deixa escolhas em aberto. Cada uma aponta o contexto, a alternativa escolhida e o porquê.

<a id="d1"></a>
## D1 — Langfuse SDK v5 (e não a v3 das aulas)
- **Contexto:** em 2026-10-25 a versão atual era a `langfuse 5.0.4`. Os materiais com `start_as_current_span` e `update_trace` são da v3.
- **Verificação:** inspecionei a SDK instalada. `start_as_current_span` **não existe** na v5; o equivalente é `start_as_current_observation(as_type="span")`. Atributos de trace vão por `propagate_attributes()`, e o input e o output do trace ficam na observação raiz. `LANGFUSE_HOST` está depreciado em favor de `LANGFUSE_BASE_URL`.
- **Decisão:** usar a v5 (escolha do autor do projeto), com tabela de equivalência v3 → v5 no [README da Etapa 2](etapa-2-observabilidade/README.md#mudanças-da-sdk-v3-para-a-v5-por-que-o-código-difere-das-aulas).

<a id="d2"></a>
## D2 — Sem execução com LLM nesta entrega
- **Contexto:** o projeto foi entregue com `.env` vazio, por decisão do autor.
- **Decisão:** todo o código que chama OpenAI e Langfuse está pronto. O que não depende de rede foi **executado de verdade**: validação do dataset, geração das planilhas, funções de score e parsing, fluxo completo com cliente falso e hierarquia de spans capturada em memória. Relatório e síntese têm campos ⏳ a preencher. **Nenhum resultado de modelo foi inventado.**

<a id="d3"></a>
## D3 — Ambiente
- Python 3.14.0. Versões fixadas no [requirements.txt](requirements.txt): langfuse 5.0.4, openai 3.37.0, pandas 3.1.0, python-dotenv 1.2.4, openpyxl 3.1.5 e pytest 9.1.1, todas instaladas sem erro em 2026-10-25. Nenhum framework extra (sem LangChain): a integração `langfuse.openai` basta, e cada dependência a mais é um risco de fornecedor (R10).

<a id="d4"></a>
## D4 — Estudos fora do Git
- Mesma escolha dos Níveis 1 e 2: `estudos/` está no `.gitignore`. A estrutura segue o padrão `1-entendimento` / `2-conhecimento` / `3-para-estudar` por etapa, mais os arquivos transversais pedidos (mapa, integração, revisão, glossário).

<a id="d5"></a>
## D5 — Classificação de risco interna × AI Act
- **Enunciado:** "considere o contexto europeu do AI Act quando pertinente, sem aplicar classificações jurídicas automaticamente".
- **Decisão:** a classificação de risco é **interna** (soma de 5 critérios + regras de piso, calculada em código). O AI Act aparece como "leitura indicativa" em coluna separada, com o aviso de que não é parecer jurídico e de que só se aplica se houver uso no mercado europeu.

<a id="d6"></a>
## D6 — O que é mascarado nos traces
- **Decisão:** `Langfuse(mask=...)` mascara **identificadores diretos** (e-mail, CPF, telefone). **Termos de saúde não são mascarados**, porque o juiz e a revisão humana precisam ver "estou grávida" para avaliar se a resposta foi segura.
- **Consequência:** o risco R01 continua **aberto**. A mitigação passa por retenção curta, acesso restrito ao Langfuse e decisão do Encarregado.

<a id="d7"></a>
## D7 — Contagem dos grupos, falhas e média
- **Enunciado:** "revisão" = score ≤ 3; "crítico" = score ≤ 2; falha de parsing → score 0. Lido literalmente, todo crítico também é revisão, e toda falha de parsing vira "crítico".
- **Decisão:**
  1. Grupos **mutuamente exclusivos**: crítico (1–2), revisão (3), adequado (4–5), falha de avaliação (parsing ou técnica). A soma dá o total.
  2. O número "≤ 3" do enunciado aparece à parte (`revisao_total_score_ate_3`).
  3. O **score médio** usa só avaliações válidas. A média com falhas como 0 também é impressa, rotulada.
  4. Falha de parsing **não** dispara fallback por padrão (`REGENERAR_EM_FALHA_DE_AVALIACAO = False`), porque não é evidência de resposta ruim; vai para revisão humana.
- **Por quê:** tratar "o juiz não respondeu no formato" como "a resposta foi péssima" distorce a média e gasta chamadas à toa.

<a id="d8"></a>
## D8 — Amostra de 10 linhas
- **Decisão:** as **10 primeiras linhas** (`df.head(10)`), as mesmas para intenção e juiz. São reprodutíveis e cobrem as 6 intenções do dataset (verificado em `test_amostra_de_10_cobre_as_6_intencoes_do_dataset`).

<a id="d9"></a>
## D9 — Um trace por interação; user e session
- `pipeline_assistente.py` cria **um trace por interação**, com `load-dataset` dentro de cada trace (autossuficiente). `user_id = cliente-<id>` é um **pseudônimo sintético**, e `session_id` agrupa a execução. Nos scripts de avaliação, um trace por execução, com um span por linha.

<a id="d10"></a>
## D10 — Papel de cada prompt
- `assistente_calmaria.md`: prompt "atual" do assistente, usado no pipeline padrão e **avaliado** na Etapa 3.
- `assistente_baseline.md`: versão genérica, só para comparação.
- `assistente_improved.md`: versão melhorada, usada na comparação e no **fallback** dos casos críticos.

<a id="d11"></a>
## D11 — `mentions_expected` literal
- Implementado exatamente como pede o enunciado (alguma das 5 primeiras palavras aparece como trecho da resposta, em minúsculas). A limitação de que palavras curtas como "a" quase sempre casam está **documentada e testada**, e uma versão melhorada fica como exercício nos estudos.

<a id="d12"></a>
## D12 — Juiz não penaliza "registrar a solicitação"
- Várias respostas de referência afirmam ações ("cancelamento realizado") ou horários que o assistente não tem como garantir. A rubrica do juiz orienta a **não** penalizar a resposta que apenas registra a solicitação. Sem isso, o juiz premiaria o comportamento arriscado (R05).

<a id="d13"></a>
## D13 — Modelo e temperaturas
- `OPENAI_MODEL` com padrão `gpt-4o-mini` (barato e o mesmo dos níveis anteriores). Temperatura 0,3 no assistente e 0,0 no classificador e no juiz, para reduzir a variação na avaliação.
