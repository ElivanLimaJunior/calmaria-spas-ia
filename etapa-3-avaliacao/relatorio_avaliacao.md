# Relatório de avaliação automatizada — Assistente Calmaria Spas

> ⏳ **Execução pendente.** Todos os campos `___` devem ser preenchidos com a saída real de `src/avaliar_intencoes.py` e `src/avaliar_respostas.py` (arquivos em `resultados/`). **Não preencha com estimativas.** Se um campo não puder ser obtido, escreva "não disponível" e o motivo.

## 1. Execução

| Campo | Valor |
|---|---|
| Data da execução | ___ |
| Modelo (`OPENAI_MODEL`) | ___ |
| Versões dos prompts (commit do Git) | ___ |
| Amostra | 10 primeiras linhas de `dados/calmaria_interacoes.csv` (ids 1–10; cobrem as 6 intenções) |
| Session IDs no Langfuse | intenção: `intencoes-___` · respostas: `avaliacao-___` |
| Arquivos gerados | `resultados/intencoes____.csv` · `resultados/avaliacao____.csv` · `resultados/resumo____.json` |
| Custo total (soma do Langfuse) | ___ |

## 2. Classificação de intenção

| Métrica | Valor |
|---|---|
| Linhas classificadas | ___ / 10 |
| Acertos (score = 1) | ___ |
| Acurácia | ___ |
| Saídas inválidas (fora das 7 categorias) | ___ |
| Previsões `others` | ___ |
| Falhas técnicas | ___ |

**Erros encontrados** (copie do CSV):

| id | Pergunta | Esperado | Previsto | Hipótese para o erro |
|---|---|---|---|---|
| ___ | ___ | ___ | ___ | ___ |

> Interpretação: com 10 exemplos, cada erro vale 10 pontos percentuais de acurácia. O resultado indica tendência, não precisão estatística.

## 3. Score simples

| Métrica | Valor |
|---|---|
| Respostas com `is_long = True` (> 200 caracteres) | ___ / 10 |
| Comprimento médio gerado × esperado | ___ × ___ |
| `mentions_expected = True` | ___ / 10 |

> Leitura obrigatória: as respostas esperadas do dataset têm **no máximo 156 caracteres** (verificado), então `is_long` indica respostas **mais longas que o padrão da equipe**, não necessariamente piores. `mentions_expected` tende a ser `True` porque palavras curtas ("a", "o") estão entre as 5 primeiras (ver o teste `test_limitacao_palavra_curta_casa_com_qualquer_resposta`).

## 4. LLM-as-Judge

| Métrica | Valor |
|---|---|
| Avaliações válidas | ___ / 10 |
| **Score médio** (só avaliações válidas) | ___ |
| Score médio contando falhas como 0 (leitura literal do enunciado) | ___ |
| Distribuição das notas 1 · 2 · 3 · 4 · 5 | ___ · ___ · ___ · ___ · ___ |
| Falhas de parsing | ___ |
| Falhas técnicas | ___ |

## 5. Casos prioritários e fallback

| Grupo (mutuamente exclusivos) | Quantidade |
|---|---|
| Críticos (nota ≤ 2) | ___ |
| Revisão (nota = 3) | ___ |
| Adequados (nota ≥ 4) | ___ |
| Falhas de avaliação | ___ |
| **Total** (deve ser 10) | ___ |
| Revisão no sentido do enunciado (nota ≤ 3 = críticos + nota 3) | ___ |
| Fallbacks aplicados | ___ |
| Fallbacks que melhoraram a nota | ___ |
| Score médio após o fallback | ___ |
| Categorias mais frequentes nos críticos (`Counter`) | ___ |

**Casos críticos:**

| id | Categoria | Nota original | Motivo do juiz | Nota após fallback | Revisão humana concorda? |
|---|---|---|---|---|---|
| ___ | ___ | ___ | ___ | ___ | ___ |

## 6. Calibração do juiz (recomendado)
Leia as 10 respostas e dê a sua própria nota de 1 a 5, sem olhar a do juiz.

| Métrica | Valor |
|---|---|
| Casos em que juiz e humano concordam exatamente | ___ / 10 |
| Casos com diferença ≥ 2 pontos | ___ |

Se houver muitas diferenças ≥ 2, ajuste a rubrica de [juiz_calmaria.md](../prompts/juiz_calmaria.md) antes de confiar no score médio.

## 7. Conclusões
- ___
- ___

## 8. Limitações desta avaliação
- Amostra de 10 linhas: não representa os 50 casos nem a produção.
- O juiz é um LLM: pode ter viés (preferir respostas longas, ser complacente com o próprio estilo).
- As respostas de referência contêm ações e horários que o assistente não pode garantir (ids 3, 5, 9); a rubrica orienta o juiz a não penalizar quem só registra a solicitação.
- Temperatura 0 no juiz reduz a variação, mas não garante resultados idênticos entre execuções.
