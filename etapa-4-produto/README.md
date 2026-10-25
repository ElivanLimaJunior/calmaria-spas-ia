# Etapa 4 — Estratégia de produto com IA

> **Pergunta-chave:** que produto de recomendação a Calmaria deve construir, para quem, com quais dados, e como colocá-lo no ar sem colocar clientes e marca em risco?

## Arquivos

| Entregável | Arquivo | Observação |
|---|---|---|
| AI Project Canvas (Problema, Dados, IA, Experiência) | [ai_project_canvas.csv](ai_project_canvas.csv) · aba "AI Project Canvas" de [estrategia_produto.xlsx](estrategia_produto.xlsx) | 26 itens; cada um marcado como **Conhecido, Hipótese, Meta ou A coletar** |
| Matriz CSD (≥ 4 por coluna) | [matriz_csd.csv](matriz_csd.csv) · aba "Matriz CSD" | 5 certezas, 5 suposições, 6 dúvidas, cada uma com "como validar" |
| Proto-persona | [proto_persona.md](proto_persona.md) | Elementos fictícios marcados; 6 hipóteses de validação |
| Rollout e monitoramento | [rollout_monitoramento.md](rollout_monitoramento.md) | Shadow → 1 → 5 → 10 → 20 → 100%; métricas diária, semanal, mensal e trimestral; ciclo de degradação; NSM |
| Síntese executiva | [sintese_executiva.md](sintese_executiva.md) | 1–2 páginas; resultados da avaliação ⏳ a preencher |
| Gerador das planilhas | [gerar_planilhas.py](gerar_planilhas.py) | Fonte de verdade do canvas e da CSD |

## Decisões desta etapa
- **Classificação do tipo de informação em todo o canvas:** é o que o enunciado pede ("não invente métricas observadas") e evita que uma meta seja lida como resultado.
- **Metas do rollout como "propostas":** valores como "críticos ≤ 10%" e "p95 ≤ 5 s" são pontos de partida para o Comitê, a recalibrar com a linha de base do shadow mode.
- **NSM com sessão concluída**, e não clique ou agendamento, para não premiar recomendações que o cliente cancela.

## Importar no Google Sheets e no Miro
- **Sheets:** [sheets.new](https://sheets.new) → **Arquivo → Importar → Upload** → `estrategia_produto.xlsx` → **Substituir planilha**.
- **Miro (opcional):** a Matriz CSD pode virar um quadro com três colunas. Copie as linhas do CSV, cole no Miro (cada linha vira um *sticky note*) e arraste para a coluna certa.

### Regenerar as planilhas
```powershell
.venv\Scripts\python etapa-4-produto\gerar_planilhas.py
```
