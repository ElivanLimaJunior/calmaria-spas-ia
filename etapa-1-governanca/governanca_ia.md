# Governança de IA — Calmaria Spas

> Visão geral da governança: inventário das soluções, como o risco é classificado e o que é obrigação legal × boa prática. Os outros documentos da etapa detalham cada peça:
> [política de uso responsável](politica_uso_responsavel.md) · [matriz de riscos do assistente](matriz_riscos.md) · [fluxo de aprovação](fluxo_aprovacao.md).

**Aviso:** este material é um exercício de governança. As leituras sobre LGPD, CDC e AI Act são indicativas e **não substituem parecer jurídico**. Nenhuma solução aqui é declarada "em conformidade".

---

## 1. Inventário de soluções de IA

Fonte: [inventario_solucoes_ia.csv](inventario_solucoes_ia.csv) (aba **Inventário** em [governanca_calmaria.xlsx](governanca_calmaria.xlsx)). Resumo:

| ID | Solução | Área demandante | Dados utilizados | Público impactado | Risco (interno) | Status |
|---|---|---|---|---|---|---|
| IA-01 | Assistente virtual de recomendação (LLM) | Experiência do Cliente / Atendimento | Pergunta em texto livre, perfil do cliente, catálogo | Todos os clientes do canal digital | **Alto** (14) | Em produção (piloto) · em reavaliação |
| IA-02 | Sistema de recomendação híbrido | Produto / Marketing | Histórico de agendamentos, perfil, avaliações, catálogo | Clientes logados | **Médio** (10) | Proposta (Etapa 4) |
| IA-03 | Análise de sentimento de avaliações | Qualidade / Operações | Texto e nota das avaliações | Clientes e funcionários citados | **Médio** (7 + piso) | Em desenvolvimento |
| IA-04 | Precificação dinâmica | Financeiro / Comercial | Ocupação, vendas, sazonalidade (e perfil, se personalizada) | Todos os clientes | **Alto** (13) | Ideia em avaliação |
| IA-05 | Avaliador automático (LLM-as-Judge) | Engenharia de IA | Perguntas e respostas do assistente | Equipe interna (clientes indiretamente) | **Médio** (8 + piso) | Em desenvolvimento (Etapa 3) |

> A IA-05 não estava entre as quatro do enunciado. Entrou porque o próprio projeto a cria na Etapa 3, e uma ferramenta que decide fallback automático também precisa estar inventariada.

A planilha completa traz ainda: finalidade, papel do humano, pontuação por critério, regras de piso aplicadas, justificativa, leitura indicativa no AI Act, dono (*accountable*) e periodicidade de reavaliação.

## 2. Critérios de classificação de risco

Fonte: [criterios_risco.csv](criterios_risco.csv). Cada solução recebe de 1 a 3 pontos em cinco critérios:

| Critério | Pergunta | 1 · Baixo | 2 · Médio | 3 · Alto |
|---|---|---|---|---|
| **C1 Dados** | Que tipo de dado trata? | Sem dados pessoais | Dados pessoais comuns | Dados sensíveis ou texto livre que pode contê-los |
| **C2 Impacto** | Pior efeito de um erro sobre pessoas? | Incômodo interno | Experiência ruim, perda pequena e reversível | Dano físico, discriminação, efeito sobre direitos |
| **C3 Autonomia** | Um humano revisa antes do efeito? | Sempre revisa | Atua só, mas o efeito é uma sugestão | Atua só e o efeito é aplicado |
| **C4 Exposição** | Quem vê, em que volume? | Interno, poucas pessoas | Clientes, volume limitado | Todos os clientes, canal principal |
| **C5 Reversibilidade** | Quão fácil desfazer? | Trivial | Exige contato ou estorno | Difícil ou impossível |

**Regra:** soma de 5 a 15 → **5–7 Baixo · 8–11 Médio · 12–15 Alto**. Em seguida aplicam-se **regras de piso**, que só elevam o nível:

| Regra de piso | Nível mínimo | Por quê |
|---|---|---|
| Dado sensível enviado a fornecedor externo | Médio | A LGPD dá proteção reforçada a dados de saúde (art. 11) e a transferência ao exterior tem regras próprias (art. 33). |
| Pode afetar a integridade física | Alto | No contexto de bem-estar, uma indicação errada para gestante ou pessoa com alergia não é só "experiência ruim". |
| Usado para avaliar ou decidir sobre funcionários | Alto | Uso próximo ao das categorias de alto risco do AI Act (Anexo III, emprego) e sensível do ponto de vista trabalhista. |
| Prática proibida (manipulação, exploração de vulnerabilidade) | Inaceitável | Não se implanta. Referência: art. 5º do AI Act. |

**Por que soma + piso e não só a soma?** A soma resume vários fatores, mas pode "diluir" um fator grave: a análise de sentimento (IA-03) soma 7, que seria Baixo, embora trate texto que pode conter dado de saúde. O piso impede que um critério crítico seja compensado por outros baixos.

**Por que não usar só o "pior critério"?** Quase tudo viraria Alto (qualquer solução que toca texto do cliente), e a classificação deixaria de priorizar. A combinação soma + piso é um meio-termo explicável.

As classificações são **calculadas** por `classificar_solucao()` em [gerar_planilhas.py](gerar_planilhas.py), nunca digitadas.

### O que a classificação muda na prática
| Nível | Exigências antes de produção | Reavaliação |
|---|---|---|
| Baixo | Ficha no inventário + dono definido | Anual |
| Médio | + avaliação técnica, análise de privacidade simplificada, monitoramento básico | Semestral |
| Alto | + RIPD, matriz de riscos própria, aprovação do Comitê, rollout gradual, monitoramento contínuo | Trimestral e a cada mudança de modelo ou prompt |
| Inaceitável | Não avança | — |

## 3. Obrigação legal × boa prática

Uma confusão comum é tratar tudo como "exigência da lei". Separar as duas coisas ajuda a priorizar e a não prometer conformidade que não foi avaliada.

| Tema | Obrigação legal (Brasil) | Boa prática de governança (não exigida por lei) |
|---|---|---|
| Dados pessoais e sensíveis | LGPD: princípios (art. 6º), bases legais (art. 7º; art. 11 para sensíveis), direitos do titular (art. 18), segurança (art. 46), comunicação de incidente (art. 48) | Mascarar dados sensíveis antes de gravar traces; retenção curta no Langfuse |
| Relatório de impacto | A ANPD pode exigir o RIPD (art. 38); é a principal evidência para tratamento de alto risco | Fazer o RIPD por padrão para toda solução classificada como Alto |
| Encarregado | Indicar encarregado (art. 41), salvo as dispensas previstas pela ANPD para agentes de pequeno porte | Incluir o encarregado no Comitê de Governança de IA |
| Decisão automatizada | Direito de pedir revisão de decisões tomadas só com base em tratamento automatizado (art. 20) | Explicar ao cliente por que um tratamento foi recomendado |
| Transferência internacional | Regras do art. 33 (ao usar OpenAI e Langfuse Cloud fora do Brasil) | Preferir região ou auto-hospedagem que reduza a transferência |
| Consumidor | CDC: informação clara de preço e características (art. 6º, III; art. 31), proibição de publicidade enganosa (art. 37) | Lista de alegações permitidas aprovada pelo Jurídico |
| Transparência sobre IA | Sem lei geral de IA vigente no Brasil na data deste documento (o PL 2338/2023 tramitava no Congresso; confira o status atual) | Avisar que o cliente fala com uma IA e oferecer atendente humano |
| Inventário, comitê, IA champion, matriz de riscos | — | Todos são práticas de governança (ex.: NIST AI RMF, ISO/IEC 42001), não exigências legais diretas |

### E o AI Act europeu?
O Regulamento (UE) 2024/1689 (AI Act) **só se aplica se a Calmaria colocar sistemas de IA no mercado da UE ou se o resultado do sistema for usado na UE**. Mesmo sem obrigação, ele é útil como referência porque organiza o risco em camadas:

| Camada do AI Act | Exemplo | Leitura indicativa para a Calmaria |
|---|---|---|
| Práticas proibidas (art. 5º) | Manipulação que explora vulnerabilidades | Nenhuma solução do inventário deveria se enquadrar; a regra de piso "Inaceitável" reflete isso |
| Alto risco (art. 6º + Anexo III) | Emprego, crédito, acesso a serviços essenciais | Nenhuma, a priori. Atenção à IA-03 se usada para avaliar terapeutas |
| Obrigações de transparência (art. 50) | Chatbots devem informar que a pessoa interage com IA | IA-01 |
| Risco mínimo | Filtros, recomendações comuns | IA-02, IA-04, IA-05 (o risco da IA-04 é sobretudo de consumidor, não de AI Act) |

Os enquadramentos acima **não** são classificações jurídicas: dependem de onde e como cada sistema é usado, e a classificação interna (seção 2) é independente deles.

## 4. Governança de dados × governança de IA

| | Governança de dados | Governança de IA |
|---|---|---|
| Pergunta central | "Este dado é correto, seguro, de quem é e quem pode usar?" | "Este sistema decide ou recomenda de forma segura, justa e explicável?" |
| Objeto | Dados: catálogo, qualidade, linhagem, acesso, retenção | Modelos, prompts, decisões, comportamento em produção |
| Riscos típicos | Vazamento, dado desatualizado, acesso indevido | Alucinação, viés, recomendação perigosa, dependência de fornecedor |
| Artefatos | Dicionário de dados, política de retenção, RIPD | Inventário de IA, matriz de riscos, avaliação, traces, fluxo de aprovação |
| Na Calmaria | Quem pode ver as perguntas dos clientes no Langfuse; por quanto tempo ficam lá | Se o assistente deve recomendar algo a uma gestante; qual score dispara fallback |

As duas se sobrepõem: o risco R01 (dado de saúde nos traces) é ao mesmo tempo de dados e de IA. A governança de IA **depende** da de dados, mas a de dados sozinha não cobre o comportamento do modelo.

## 5. Papéis

Definidos na [política](politica_uso_responsavel.md#8-papéis-e-responsabilidades): Comitê de Governança de IA, IA Champion, Equipe de Dados e IA, Encarregado(a) de Dados (DPO), Jurídico, Segurança da Informação, Coordenação Técnica de Terapias e Dono da solução.
