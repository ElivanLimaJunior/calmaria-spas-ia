# Etapa 2 — Instrumentação e observabilidade com Langfuse

> **Pergunta-chave:** quando o assistente der uma resposta ruim, como descobrimos **qual pergunta**, **qual prompt**, **qual modelo**, **quanto tempo**, **quantos tokens** e **qual resposta** produziram aquele resultado?

**Status:** ✅ código implementado e testado offline · ⏳ **execução real pendente** (o `.env` está sem credenciais, por decisão do projeto; ver [DECISOES.md](../DECISOES.md#d2)). Nenhum trace, custo ou captura de tela deste documento é real; o que existe é o passo a passo para você gerar e verificar.

## Arquivos

| Entregável | Arquivo |
|---|---|
| Ambiente (Python 3.10+, venv, dependências, variáveis) | [requirements.txt](../requirements.txt) · [.env.example](../.env.example) · [.gitignore](../.gitignore) · seção "Como executar" abaixo |
| Validação da conexão (`get_client()` + `auth_check()`) | [src/verificar_conexao.py](../src/verificar_conexao.py) |
| Pipeline instrumentado | [src/pipeline_assistente.py](../src/pipeline_assistente.py) |
| Inicialização do Langfuse e máscara de PII | [src/observabilidade.py](../src/observabilidade.py) |
| Chamada ao modelo (integração Langfuse-OpenAI) | [src/llm.py](../src/llm.py) |
| Prompt principal, baseline e improved | [prompts/assistente_calmaria.md](../prompts/assistente_calmaria.md) · [assistente_baseline.md](../prompts/assistente_baseline.md) · [assistente_improved.md](../prompts/assistente_improved.md) |
| `PROMPT_FILES` e configurações | [src/config.py](../src/config.py) |
| Testes da hierarquia de spans (sem rede) | [tests/test_hierarquia_spans.py](../tests/test_hierarquia_spans.py) |
| Evidências da execução real | [evidencias/](evidencias/) ⏳ |

## O que é registrado (um trace por interação)

```text
assistente-recomendacao-pipeline   [span raiz]   input: id + versões · output: pergunta + respostas
│                                                user_id, session_id, tags, metadata (propagados)
├── load-dataset                   [span]        output: nº de linhas e colunas
├── preprocessing                  [span]        input: pergunta original · output: após strip()
│                                                metadata: comprimento_pergunta
└── prompt-<versão>                [span]        version = baseline | improved | calmaria
    ├── load-prompt                [span]        output: arquivo e nº de caracteres
    └── resposta-<versão>          [generation]  criada pela integração langfuse.openai:
                                                 modelo, parâmetros, mensagens, resposta,
                                                 tokens, custo estimado e latência
```

| Atributo | Valor | Por quê |
|---|---|---|
| `session_id` | `pipeline-AAAAMMDD-HHMMSS` | Agrupa todos os traces de uma execução na aba **Sessions** |
| `user_id` | `cliente-<id>` | Pseudônimo **sintético**: o dataset não tem cliente real e não usamos dado identificável |
| `tags` | `calmaria`, `assistente`, `etapa-2` + versões | Filtrar na lista de traces |
| `metadata` | `categoria`, `perfil_cliente` | Comparar comportamento por categoria e perfil |
| `version` (span `prompt-*`) | nome da versão do prompt | Identificar o prompt em cada ramo |
| `metadata` da generation | `prompt_version` | Filtrar generations por versão |

A hierarquia acima foi **verificada de verdade** com um exportador OpenTelemetry em memória (sem rede): ver `test_hierarquia_pipeline_assistente`. O teste não cobre a generation, porque o cliente falso não passa pela integração `langfuse.openai`.

## Como executar

```powershell
# 1. Ambiente (Python 3.10+; testado em 3.14)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Credenciais: preencha o .env (já existe, vazio; modelo em .env.example)
#    OPENAI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL

# 3. Verificar ambiente e autenticação no Langfuse (não chama a OpenAI)
python src\verificar_conexao.py

# 4. Rodar o pipeline
python src\pipeline_assistente.py                          # id 1, prompt assistente_calmaria.md
python src\pipeline_assistente.py --comparar               # baseline x improved no mesmo trace
python src\pipeline_assistente.py --comparar --id 1 --quantidade 10   # 10 interações (20 chamadas)
```

**Custo:** cada interação com `--comparar` faz 2 chamadas ao modelo. Comece com uma só.

**Onde pegar as chaves:** Langfuse Cloud → crie um projeto → **Settings → API Keys → Create new API keys**. `LANGFUSE_BASE_URL` depende da região escolhida ao criar a conta: `https://cloud.langfuse.com` (EU) ou `https://us.cloud.langfuse.com` (US). Se a região estiver errada, o `auth_check()` falha.

## Como verificar na interface do Langfuse

| O que conferir | Onde clicar | O que você deve ver | Se não aparecer |
|---|---|---|---|
| **Trace** | **Tracing → Traces**, filtre *Name* = `assistente-recomendacao-pipeline` | Uma linha por interação executada, com input e output | Espere de 15 a 30 s (a ingestão é assíncrona) e recarregue; confira se o script imprimiu "Sessão no Langfuse" (o `flush()` rodou) |
| **Hierarquia** | Abra o trace → painel da árvore à esquerda | A árvore da seção anterior | Spans soltos em outro trace indicam span criado fora do `with` do pai |
| **Generation e modelo** | Clique em `resposta-<versão>` | Tipo **GENERATION**, *Model* = valor de `OPENAI_MODEL`, mensagens system e user | Se não houver generation, o import usado foi `openai.OpenAI` em vez de `langfuse.openai.OpenAI` |
| **Tokens e custo** | Mesma generation → *Usage* e *Cost*; na lista de traces, colunas *Tokens* e *Cost* | Tokens de input e output; custo **estimado** pelo Langfuse a partir da tabela de preços do modelo | Custo vazio: o modelo não está na tabela de preços do Langfuse (os tokens continuam aparecendo) |
| **Latência** | Coluna *Latency* do trace e de cada observação | A maior parte do tempo está na generation | — |
| **Metadata e atributos** | Trace → abas *Metadata*; topo do trace mostra *User* e *Session*; `preprocessing` → metadata | `categoria`, `perfil_cliente`, `comprimento_pergunta`, `user_id`, `session_id`, tags | Atributos só valem para observações criadas **dentro** do `propagate_attributes` |
| **Sessão** | **Tracing → Sessions** → `pipeline-…` | Todos os traces da execução em sequência | — |
| **Baseline × improved** | Abra um trace do `--comparar` e compare `prompt-baseline` e `prompt-improved` lado a lado; ou, em **Observations**, filtre *Name* = `resposta-baseline` e depois `resposta-improved` e compare tamanho, tokens e latência | O improved tende a seguir a estrutura acolhimento → resposta → próximo passo (**hipótese a verificar**) | — |

Depois de verificar, salve as capturas em [evidencias/](evidencias/) e atualize a tabela de status no [ENTREGA.md](../ENTREGA.md).

## Mudanças da SDK v3 para a v5 (por que o código difere das aulas)

Verificado em 2026-10-25 por inspeção da `langfuse==5.0.4` instalada:

| Na v3 (materiais mais antigos) | Na v5 (este projeto) |
|---|---|
| `langfuse.start_as_current_span(name=...)` | `langfuse.start_as_current_observation(name=..., as_type="span")` |
| `langfuse.start_as_current_generation(...)` | `start_as_current_observation(as_type="generation")`, ou automático via `langfuse.openai` |
| `span.update_trace(user_id=..., session_id=..., tags=...)` | `with propagate_attributes(user_id=..., session_id=..., tags=..., metadata=...)` |
| Input e output do trace definidos à parte | Ficam na **observação raiz**: `raiz.update(output=...)` |
| `LANGFUSE_HOST` | `LANGFUSE_BASE_URL` (`HOST` ainda funciona, mas está depreciado) |
| `get_client()`, `flush()`, `auth_check()`, `from langfuse.openai import OpenAI` | Iguais |

## Segurança e dados nos traces
- Segredos ficam só no `.env` (ignorado pelo Git). Nenhum script imprime valores de chave, apenas os **nomes** das variáveis que faltam.
- `Langfuse(mask=mascarar_dados_sensiveis)` troca e-mail, CPF e telefone por `[EMAIL]`, `[CPF]` e `[TELEFONE]` **antes** do envio.
- **Termos de saúde não são mascarados** (ver [DECISOES.md](../DECISOES.md#d6)): o risco R01 continua aberto e depende de decisão do Encarregado sobre retenção e acesso.
- O `user_id` é um pseudônimo sintético.

## Limitações
- A execução real não foi feita: não há traces, tokens nem custos para relatar.
- O assistente não tem acesso ao catálogo nem à agenda, então preços e horários na resposta seriam inventados (risco R04). O prompt improved mitiga isso orientando a não afirmar o que não sabe.
- `load-dataset` lê o CSV a cada trace. Isso foi feito para que cada trace seja autossuficiente; com 50 linhas, o custo é desprezível.
- O span `load-dataset` é criado antes do `propagate_attributes` (precisa do dataset para saber a categoria), então não carrega user e session nos próprios atributos. O trace como um todo carrega, porque eles ficam na raiz.
