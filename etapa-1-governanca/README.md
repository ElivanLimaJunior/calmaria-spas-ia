# Etapa 1 — Governança de IA

> **Pergunta-chave:** como a Calmaria Spas sabe quais IAs usa, quanto risco cada uma traz, quem responde por elas e o que precisa acontecer antes de uma nova solução chegar aos clientes?

## Arquivos

| Entregável do enunciado | Arquivo | Observação |
|---|---|---|
| Inventário de soluções de IA (≥ 4) | [inventario_solucoes_ia.csv](inventario_solucoes_ia.csv) · aba "Inventário" de [governanca_calmaria.xlsx](governanca_calmaria.xlsx) | 5 soluções: as 4 do enunciado + o próprio avaliador LLM-as-Judge |
| Critérios de classificação de risco; obrigação legal × boa prática; AI Act | [governanca_ia.md](governanca_ia.md) · [criterios_risco.csv](criterios_risco.csv) | Soma de 5 critérios + regras de piso |
| Política de uso responsável | [politica_uso_responsavel.md](politica_uso_responsavel.md) | Inclui os papéis de IA champion, equipe de dados e governança |
| Matriz de riscos (≥ 6) | [matriz_riscos.csv](matriz_riscos.csv) · [matriz_riscos.md](matriz_riscos.md) · abas "Matriz de riscos" e "Mapa de calor" | 11 riscos nas 4 categorias, com evidências do dataset |
| Fluxo de aprovação | [fluxo_aprovacao.md](fluxo_aprovacao.md) | Mermaid + tabela de critérios de bloqueio |
| Gerador das planilhas | [gerar_planilhas.py](gerar_planilhas.py) | Fonte de verdade: calcula as classificações |

## Decisões desta etapa
- **Classificação calculada, não digitada:** `classificar_solucao()` e `classificar_risco()` aplicam as regras documentadas. Mudou uma nota? Rode o script e a planilha se atualiza sem contradições.
- **Quinta solução no inventário (IA-05, juiz):** a ferramenta que decide fallback também precisa de governança.
- **Classificação interna separada do AI Act:** o AI Act só se aplica no contexto europeu. A planilha traz uma "leitura indicativa" e nunca afirma conformidade ([DECISOES.md](../DECISOES.md#d5)).
- **Probabilidades são estimativas:** estão marcadas como tal, para recalibrar com os dados da Etapa 3 e do monitoramento.

## O que fazer manualmente

### Importar no Google Sheets
1. Acesse [sheets.new](https://sheets.new).
2. **Arquivo → Importar → Upload** → `governanca_calmaria.xlsx` → **Substituir planilha**. As 4 abas são criadas.
3. As cores da coluna de classificação vêm do `.xlsx`. Se quiser regras dinâmicas, use **Formatar → Formatação condicional**.

> Alternativa: importe cada CSV com **Inserir nova(s) página(s)**.

### Regenerar as planilhas
```powershell
.venv\Scripts\python etapa-1-governanca\gerar_planilhas.py
```
