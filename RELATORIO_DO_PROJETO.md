# Relatório do Projeto — Calmaria Spas · Assistente de IA governado, observável e avaliado

**Checkpoint Nível 3 — Carreira Especialista em IA (Alura)**

## 1. Resumo
A Calmaria Spas tem um assistente virtual que recomenda tratamentos de bem-estar, mas responde de forma genérica e inconsistente, e não se sabe o que ele faz em produção. O projeto montou as quatro peças que faltavam, ligadas entre si:

1. **Governança.** Inventário de 5 soluções de IA com risco calculado, política de uso responsável, matriz com 11 riscos do assistente (4 críticos) e fluxo de aprovação com critérios de bloqueio.
2. **Observabilidade.** Pipeline instrumentado com Langfuse v5: um trace por interação, com spans de carga, pré-processamento e prompt, a generation do modelo e atributos de sessão, usuário, tags e metadata. Inclui a comparação baseline × improved.
3. **Avaliação.** Classificação de intenção com score binário, score simples heurístico, LLM-as-Judge com parsing robusto, thresholds (3 e 2), análise de casos prioritários fora do loop, fallback com o prompt improved e evento `fallback-applied`.
4. **Produto.** AI Project Canvas, Matriz CSD, proto-persona, plano de rollout com shadow mode e métricas por frequência, North Star Metric e síntese executiva.

**Resultados de modelo:** ⏳ pendentes. A entrega foi feita sem credenciais ([D2](DECISOES.md#d2)). O que foi **medido de verdade** está no [checklist de validação](ENTREGA.md#checklist-de-validação-resultados-reais-de-2026-10-25).

## 2. O que o dataset revelou (verificado)
- 50 interações; 6 intenções (de 6 a 10 exemplos cada); 6 categorias; perfis novo 20, recorrente 19, vip 11.
- As respostas de referência têm **de 72 a 156 caracteres**: nenhuma passa do limite de 200 do `is_long`.
- **As próprias referências contêm comportamentos arriscados para um assistente sem integração:**
  - 5 delas afirmam cancelamentos executados (ids 5, 15, 21, 27, 33);
  - 8 oferecem horários específicos (ids 3, 9, 13, 19, 25, 31, 38, 49).
  
  Isso orientou a rubrica do juiz ([D12](DECISOES.md#d12)) e os riscos R04 e R05.
- Há perguntas com **informação de saúde** (ids 21, 34, 43, 46). A id 34 é o exemplo de resposta segura: encaminha ao atendimento médico.

## 3. Achados técnicos relevantes
- **A SDK do Langfuse mudou de forma incompatível:** `start_as_current_span` não existe na v5, e `LANGFUSE_HOST` foi substituído por `LANGFUSE_BASE_URL`. O código das aulas (v3) não roda sem adaptação ([D1](DECISOES.md#d1)).
- **O Langfuse é um singleton por `public_key`:** um segundo `Langfuse(...)` com a mesma chave reaproveita a configuração do primeiro. Isso foi descoberto quando um teste falhou e é a razão de `inicializar_langfuse()` configurar uma vez e usar `get_client()`.
- **`mentions_expected` é quase sempre verdadeiro** pela definição do enunciado, porque palavras como "a" estão entre as 5 primeiras. Isso está documentado e testado ([D11](DECISOES.md#d11)).

## 4. Pendências
| Pendência | Depende de |
|---|---|
| Executar o pipeline e verificar traces, generation, tokens e custo | Credenciais OpenAI + Langfuse |
| Executar as avaliações e preencher o relatório e a síntese | Idem |
| Calibrar o juiz com notas humanas | Execução + 30 min de revisão manual |
| Capturas de evidência | Execução |
| RIPD, base legal, contratos com fornecedores | Encarregado(a) e Jurídico |
| Importar planilhas no Sheets; criar o repositório Git | Ação manual |

## 5. Limitações
- Amostra de avaliação pequena (10 linhas); serve para mostrar o método, não para tirar conclusões estatísticas.
- O assistente não tem catálogo nem agenda: preços e horários continuam sujeitos a alucinação (R04 e R05) até haver integração.
- Termos de saúde não são mascarados nos traces ([D6](DECISOES.md#d6)): R01 continua aberto.
- O juiz é um LLM e pode ter viés; sem calibração humana, o score médio é indicativo.
- Monitoramento contínuo, A/B, feedback e feature flags estão **documentados, não implementados**.
- Probabilidades da matriz de riscos e metas do rollout são **estimativas e propostas**, a recalibrar com dados reais.

## 6. Próximos passos
1. Rodar as avaliações com credenciais e preencher os campos ⏳.
2. Agendar a avaliação semanal (ex.: GitHub Actions ou cron) sobre uma amostra de traces reais.
3. Integrar o catálogo oficial ao contexto do assistente (RAG ou tabela no prompt).
4. Implementar o feedback 👍/👎 como score no Langfuse.
5. Versionar os prompts no Langfuse Prompt Management e ligá-los às generations (`langfuse_prompt`).
6. Criar a fila de revisão humana para os casos com nota 3.
