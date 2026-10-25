# Matriz de riscos — Assistente virtual (IA-01)

Fonte de dados: [matriz_riscos.csv](matriz_riscos.csv) (aba **Matriz de riscos** e **Mapa de calor** em [governanca_calmaria.xlsx](governanca_calmaria.xlsx)). Este documento explica a escala e resume a matriz. O detalhamento completo de cada risco (cenário, mitigação, contingência, indicador e responsável) está no CSV.

## Escala

| Nota | Probabilidade | Impacto |
|---|---|---|
| 1 | Rara: não se espera que ocorra | Desprezível: ninguém percebe |
| 2 | Improvável: pode ocorrer raramente | Menor: incômodo, corrigido no mesmo atendimento |
| 3 | Possível: deve ocorrer algumas vezes por mês | Moderado: reclamação, retrabalho, pequena perda financeira |
| 4 | Provável: deve ocorrer toda semana | Grave: dano à confiança, exposição de dado, risco legal concreto |
| 5 | Quase certa: já ocorre ou ocorrerá com frequência | Severo: dano à saúde do cliente, sanção, crise de reputação |

**Nível = Probabilidade × Impacto** → 1–4 **Baixo** · 5–9 **Médio** · 10–14 **Alto** · 15–25 **Crítico** (calculado por `classificar_risco()` em [gerar_planilhas.py](gerar_planilhas.py)).

> ⚠️ **As notas de probabilidade são estimativas qualitativas**, feitas a partir do enunciado (que relata respostas genéricas e inconsistentes) e da leitura do dataset. Não são frequências medidas. Depois da Etapa 3 (avaliação) e do monitoramento da Etapa 4, devem ser recalibradas com dados reais.

## Resumo

| ID | Categoria | Risco | Evidência no dataset (ids) | P | I | Nível | Responsável |
|---|---|---|---|---|---|---|---|
| R01 | Dados | Dados sensíveis de saúde no texto livre | 21, 34, 43, 46 | 4 | 4 | **16 Crítico** | Encarregado(a) de Dados |
| R02 | Legal | Base legal e transferência internacional | Todas | 3 | 4 | **12 Alto** | Jurídico + Encarregado(a) |
| R03 | Operacional | Recomendação inadequada para condição de saúde | 34, 43, 46 | 3 | 5 | **15 Crítico** | Coordenação Técnica de Terapias |
| R04 | Reputacional | Alucinação de preço, política ou disponibilidade | 3, 5, 9, 13, 18, 19 | 4 | 3 | **12 Alto** | Product Owner do Assistente |
| R05 | Operacional | Afirmar ação executada sem integração | 5, 15, 21, 27, 33 | 4 | 4 | **16 Crítico** | Product Owner do Assistente |
| R06 | Reputacional | Respostas genéricas, inconsistentes ou frias | 6, 16, 22, 28, 34, 39, 46 | 5 | 3 | **15 Crítico** | Product Owner do Assistente |
| R07 | Legal | Viés e tratamento desigual | 18, 35 | 3 | 3 | **9 Médio** | Comitê de Governança de IA |
| R08 | Legal | Promessas de resultado e alegações de saúde | 4, 23, 26, 32 | 4 | 3 | **12 Alto** | Jurídico |
| R09 | Dados | Prompt injection e uso indevido | — | 3 | 3 | **9 Médio** | Segurança da Informação |
| R10 | Operacional | Dependência de fornecedores | — | 3 | 3 | **9 Médio** | Engenharia de IA |
| R11 | Operacional | Avaliação automática enganosa | — | 3 | 3 | **9 Médio** | Engenharia de IA |

Cobertura: Dados (R01, R09), Legal (R02, R07, R08), Operacional (R03, R05, R10, R11), Reputacional (R04, R06).

## Mapa de calor

| Impacto ↓ / Probabilidade → | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | | | R03 | | |
| **4** | | | R02 | R01, R05 | |
| **3** | | | R07, R09, R10, R11 | R04, R08 | R06 |
| **2** | | | | | |
| **1** | | | | | |

## Mitigações dos riscos críticos (resumo)

| Risco | Mitigação principal | Onde o projeto trata |
|---|---|---|
| R01 Dados sensíveis | Aviso no chat, mascaramento antes de gravar o trace, retenção curta, acesso restrito ao Langfuse | Política §6; Etapa 2 (o que vai para o trace) |
| R03 Recomendação para condição de saúde | Prompt manda encaminhar (sem recomendar) em casos de saúde, gestação, alergia e lesão; contraindicações validadas pela Coordenação Técnica | Prompts da Etapa 2; critério de segurança no juiz (Etapa 3) |
| R05 Ação sem integração | O assistente apenas **registra a solicitação** e informa que a confirmação virá pelo sistema | Prompt improved (Etapa 2) |
| R06 Respostas genéricas | Prompt improved, comparação baseline × improved, LLM-as-Judge, fallback | Etapas 2 e 3 |

## O que este dataset revela (leitura manual, ids citados)

1. **As próprias respostas esperadas contêm riscos.** Os ids 5, 15, 21, 27 e 33 afirmam que o cancelamento foi feito ("realizado", "cancelado"), e os ids 3, 9, 13, 19, 25, 31, 38 e 49 oferecem horários específicos. Um assistente que só tem acesso a um LLM não consegue fazer nada disso de verdade. Se ele imitar a resposta esperada, comete R04 e R05. Na Etapa 3 isso tem uma consequência: **uma nota alta por "parecer com a esperada" pode premiar um comportamento arriscado.**
2. **O id 43 merece atenção:** a resposta esperada indica massagem a uma gestante no terceiro trimestre. Ela pode ser adequada, mas é exatamente o tipo de recomendação que precisa de validação da Coordenação Técnica (R03).
3. **O id 34 é o padrão de referência para saúde:** a resposta esperada manda procurar atendimento médico e registra o incidente.

## Regras de tratamento por nível
| Nível | Tratamento |
|---|---|
| Crítico | **Bloqueia** a expansão do rollout até a mitigação estar implementada e verificada. |
| Alto | Mitigação com prazo e dono, obrigatória antes de chegar a 100% dos usuários. |
| Médio | Monitorar o indicador; mitigar se o indicador piorar. |
| Baixo | Aceitar e registrar. |
