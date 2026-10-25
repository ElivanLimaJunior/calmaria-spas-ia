# Calmaria Spas — Assistente virtual: diagnóstico e plano de evolução

**Para:** Diretoria · **Data:** 2026-10-25 · **Status:** proposta. Os resultados de avaliação estão **pendentes de execução** (campos ⏳).

---

## 1. Diagnóstico
O assistente virtual que recomenda tratamentos está em produção (piloto) com três problemas: **recomendações genéricas**, **respostas inconsistentes** e **nenhuma visibilidade** do que ele responde. Na prática, não sabíamos se ele ajuda ou atrapalha a venda.

A análise do projeto encontrou, além disso, quatro riscos **críticos**:
- **Dados de saúde** chegam pelo chat e vão para fornecedores externos (R01).
- O assistente pode **recomendar tratamento a quem relatou alergia, lesão ou gestação** (R03).
- Ele pode **afirmar que cancelou ou agendou** sem ter acesso à agenda (R05).
- As respostas são **genéricas e frias**, inclusive em reclamações (R06).

## 2. Governança
- **Inventário** com 5 soluções de IA e classificação de risco: o assistente e a precificação dinâmica são **Alto**.
- **Política de uso responsável**: a IA não dá conselho médico, não promete resultados, não executa ações sem integração e sempre oferece atendente humano.
- **Fluxo de aprovação** com critérios de bloqueio: **nenhuma expansão do assistente até mitigar os 4 riscos críticos**.
- **Papéis**: Comitê de Governança de IA, IA Champions nas áreas, Equipe de Dados e IA, Encarregado(a) de Dados.

## 3. Observabilidade (o que passamos a enxergar)
Cada conversa vira um **trace** no Langfuse com: pergunta, versão do prompt, modelo, resposta, **tempo de resposta, tokens e custo**. Isso permite responder "o que o cliente recebeu e por quê?" e comparar versões de prompt (genérico × melhorado) lado a lado.

| Indicador | Valor |
|---|---|
| Latência média por resposta | ⏳ ___ |
| Custo médio por interação | ⏳ ___ |

## 4. Avaliação automatizada (resultados)

| Indicador (amostra de 10 interações) | Valor |
|---|---|
| Acurácia na identificação da intenção do cliente | ⏳ ___ |
| Nota média das respostas (juiz automático, 1 a 5) | ⏳ ___ |
| Casos críticos (nota ≤ 2) | ⏳ ___ |
| Casos para revisão (nota 3) | ⏳ ___ |
| Casos adequados (nota ≥ 4) | ⏳ ___ |
| Fallbacks aplicados · melhoraram a nota | ⏳ ___ · ___ |
| Categorias com mais casos críticos | ⏳ ___ |

> Preencher com o [relatório de avaliação](../etapa-3-avaliacao/relatorio_avaliacao.md). Com 10 casos, os números indicam tendência, não precisão.

**Como funciona:** um segundo modelo ("juiz") dá nota de 1 a 5 a cada resposta. Nota ≤ 3 vai para revisão humana. Nota ≤ 2 é **crítica**: o sistema regenera a resposta com o prompt melhorado e reavalia. Falhas técnicas são contadas à parte, para não confundir "sistema fora do ar" com "resposta ruim".

## 5. Proposta de evolução do produto
**Recomendação híbrida:**
1. **Regras de segurança** primeiro: em casos de saúde, o assistente encaminha e não recomenda.
2. **Catálogo oficial** como fonte de preço e duração, sem invenções.
3. Para **clientes novos** (40% das interações analisadas), recomendação por popularidade e perfil do tratamento.
4. Para **recorrentes**, uso do histórico.

O LLM entende o pedido e explica a sugestão em linguagem acolhedora, com **próximo passo claro**.

Experiência: aviso de que é uma IA, botão "falar com atendente", 👍/👎 em cada sugestão e "por que esta sugestão?".

## 6. Rollout
**Shadow mode (1–2 semanas, nenhum cliente vê) → 1% → 5% → 10% → 20% → 100%.**

Cada fase só avança se cumprir as metas propostas:
- nota média ≥ versão atual;
- críticos ≤ 10%;
- zero incidentes de saúde;
- erro técnico < 2%;
- tempo de resposta ≤ 5 s.

Qualquer incidente de saúde ou de dados provoca **rollback imediato**. A partir de 20%, um **teste A/B** compara a conversão com e sem a nova versão.

## 7. Como mediremos o valor
**North Star Metric:** *agendamentos concluídos por semana originados de recomendações do assistente.*

| Dimensão | Como a NSM se conecta |
|---|---|
| **Receita** | NSM × ticket médio, comparado ao grupo sem IA → receita incremental (trimestral) |
| **Retenção** | % de clientes novos que voltam em até 90 dias após a primeira recomendação |
| **Satisfação** | Nota pós-sessão dos tratamentos recomendados + 👍/👎 no chat |

Linha de base atual de conversão: ⏳ **não existe dado**. Levantar no sistema de agendamento antes do rollout.

## 8. Decisões pedidas à Diretoria
1. Aprovar a **política de uso responsável** e a criação do **Comitê de Governança de IA**.
2. Autorizar o **RIPD** e a revisão dos contratos com os fornecedores (OpenAI, Langfuse).
3. Priorizar a **integração com o catálogo e a agenda** (sem ela, os riscos R04 e R05 continuam).
4. Aprovar o **plano de rollout**, com as metas propostas como critérios de avanço.
