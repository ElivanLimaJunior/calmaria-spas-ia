# Política de Uso Responsável de Inteligência Artificial — Calmaria Spas

| | |
|---|---|
| **Versão** | 1.0 (proposta para aprovação) |
| **Aprovação** | Comitê de Governança de IA *(pendente)* |
| **Dono da política** | Comitê de Governança de IA |
| **Revisão** | Anual, ou antes se houver mudança legal, incidente relevante ou nova categoria de uso |

> **Em uma frase:** na Calmaria, a IA ajuda as pessoas a cuidarem do seu bem-estar, mas **não substitui profissionais**, **não decide sozinha sobre saúde** e **sempre tem um responsável humano**.

---

## 1. Objetivo
Definir regras simples e verificáveis para que todas as áreas da Calmaria Spas usem, comprem ou desenvolvam soluções de IA de forma segura, transparente, justa e de acordo com a lei, protegendo clientes, colaboradores e a marca.

## 2. Escopo
Vale para:
- todas as soluções de IA da empresa, desenvolvidas internamente ou contratadas (ex.: assistente virtual, recomendação, análise de sentimento, precificação);
- ferramentas de IA generativa usadas no dia a dia (ex.: ChatGPT para redigir textos);
- todos os colaboradores, terceirizados e fornecedores que atuem em nome da Calmaria.

Toda solução de IA deve estar registrada no **[inventário](inventario_solucoes_ia.csv)**. Se não está no inventário, não pode estar em produção.

## 3. O que entendemos por IA
Qualquer sistema que gera conteúdo, recomenda, classifica ou decide a partir de dados com algum grau de autonomia, incluindo modelos de linguagem (LLMs) acessados por API.

## 4. Princípios

| Princípio | O que significa na Calmaria | Como verificamos |
|---|---|---|
| **Transparência** | O cliente sabe quando fala com uma IA e pode pedir um atendente humano a qualquer momento. | Aviso visível no chat; opção "falar com atendente" testada antes de cada fase de rollout. |
| **Equidade** | Clientes com o mesmo pedido recebem tratamento equivalente, independentemente de gênero, idade ou perfil. Benefícios por perfil (ex.: desconto VIP) seguem regras comerciais documentadas, aplicadas pelo sistema e não "decididas" pela IA. | Testes com a mesma pergunta variando o perfil; comparação de scores entre grupos. |
| **Accountability (responsabilização)** | Toda solução tem um **dono** nomeado que responde por ela. "A IA errou" nunca é uma explicação aceitável. | Campo "Dono" obrigatório no inventário; registro das decisões de aprovação. |
| **Privacidade** | Coletamos o mínimo necessário. Dados de saúde só quando indispensáveis, com base legal definida e proteção reforçada. | RIPD para soluções de risco Alto; mascaramento de dados sensíveis nos registros (traces). |
| **Segurança** | Ninguém insere segredos, senhas ou dados de clientes em ferramentas não aprovadas. Soluções resistem a usos maliciosos (ex.: tentar "convencer" o assistente a dar desconto). | Lista de ferramentas aprovadas; testes de *red team* antes de produção. |
| **Supervisão humana** | Em saúde, reclamações graves e ações que mudam algo para o cliente (cancelar, cobrar), um humano participa. | Regras de transbordo documentadas e testadas; revisão humana dos casos críticos da avaliação automática. |
| **Confiabilidade** | Medimos a qualidade das respostas continuamente e temos plano B quando ela cai. | Avaliação automatizada, thresholds e fallback (Etapa 3); monitoramento (Etapa 4). |

## 5. Usos

### 5.1 Usos aceitáveis ✅
- Responder dúvidas sobre tratamentos, preços e políticas **com base no catálogo oficial**.
- Sugerir tratamentos de bem-estar e explicar por que foram sugeridos.
- Ajudar o cliente a **solicitar** agendamento, remarcação ou cancelamento, que são confirmados pelo sistema de agenda ou por um atendente.
- Resumir e classificar avaliações e reclamações para a equipe de qualidade.
- Apoiar colaboradores na escrita de textos, sempre com revisão humana antes de publicar.

### 5.2 Usos condicionados ⚠️ (só com aprovação do Comitê)
- Qualquer uso de **dados de saúde** (gestação, alergias, lesões, doenças).
- Personalização de preço por cliente.
- Uso de resultados de IA para avaliar **colaboradores**.
- Ações automáticas que alterem agendamentos ou cobranças.
- Envio de dados de clientes a um novo fornecedor de IA.

### 5.3 Usos proibidos ⛔
- **Diagnosticar, prescrever ou dar aconselhamento médico.** Em relatos de dor intensa, reação alérgica, lesão, gestação de risco ou qualquer situação potencialmente urgente, a IA orienta a procurar atendimento profissional ou médico e transfere para um humano.
- Prometer resultados ("resultados garantidos", "cura", "elimina") ou atribuir efeitos terapêuticos não comprovados aos tratamentos.
- Afirmar que uma ação foi executada (ex.: "cancelamento realizado") quando a IA não tem integração para executá-la.
- Inventar preços, horários, políticas ou descontos que não estejam nas fontes oficiais.
- Explorar vulnerabilidades emocionais para vender (ex.: pressionar cliente que relatou estresse intenso a comprar pacotes).
- Inserir dados pessoais de clientes em ferramentas de IA não aprovadas.

## 6. Dados em soluções de IA
1. **Minimização:** a solução recebe só os dados de que precisa. O assistente não precisa de nome completo, CPF ou telefone para recomendar um tratamento.
2. **Dados sensíveis:** dados de saúde têm proteção reforçada (LGPD, art. 11). Sempre que possível, são mascarados antes de serem registrados em ferramentas de observabilidade.
3. **Fornecedores:** só fornecedores aprovados, com contrato que trate de proteção de dados e transferência internacional.
4. **Retenção:** registros de conversas e traces têm prazo de retenção definido pelo Encarregado. Não se guardam "para sempre".
5. **Direitos dos titulares:** pedidos de acesso, correção ou exclusão são atendidos pelo canal do Encarregado, incluindo dados guardados em ferramentas de IA.

## 7. Aprovação de novas soluções
Nenhuma solução de IA entra em produção sem passar pelo **[fluxo de aprovação](fluxo_aprovacao.md)**:

1. **Proposta**, registrada no inventário pelo IA Champion da área.
2. **Checklist documental.**
3. **Classificação de risco**, conforme os [critérios](governanca_ia.md#2-critérios-de-classificação-de-risco).
4. **Avaliação técnica e de segurança.**
5. **Análise de privacidade e riscos.**
6. **Decisão do Comitê.**
7. **Implantação controlada e monitoramento.**
8. **Reavaliação periódica.**

O rigor de cada passo depende do nível de risco. Soluções de risco Baixo têm um caminho simplificado.

**Mudanças também passam pelo fluxo.** Trocar o modelo, alterar o prompt principal, incluir um novo tipo de dado ou mudar a finalidade exige reavaliação.

## 8. Papéis e responsabilidades

| Papel | Quem é | Responsabilidades |
|---|---|---|
| **Comitê de Governança de IA** | Diretoria de Operações (preside), Encarregado(a), Jurídico, Segurança da Informação, líder de Dados e IA, Coordenação Técnica de Terapias | Aprovar a política; aprovar ou reprovar soluções de risco Médio e Alto; decidir sobre usos condicionados; acompanhar incidentes e indicadores. |
| **IA Champion** | Um(a) colaborador(a) de cada área de negócio (ex.: Atendimento, Marketing), com tempo reservado para o papel | Ser a ponte entre a área e a governança; registrar propostas no inventário; disseminar a política; coletar feedback de quem usa a IA; primeiro ponto de contato para dúvidas e incidentes da área. |
| **Equipe de Dados e IA** | Engenharia de IA, Ciência de Dados, MLOps | Desenvolver e instrumentar as soluções; avaliar a qualidade (testes, LLM-as-Judge, thresholds); manter a observabilidade (Langfuse); operar fallback e rollout; documentar modelos, prompts e versões. |
| **Encarregado(a) de Dados (DPO)** | Indicado(a) conforme a LGPD | Validar base legal e minimização; conduzir o RIPD; definir retenção; ser canal com titulares e ANPD. |
| **Jurídico** | — | Contratos com fornecedores; alegações permitidas; direito do consumidor. |
| **Segurança da Informação** | — | Gestão de credenciais e acessos; testes de *red team*; resposta a incidentes de segurança. |
| **Coordenação Técnica de Terapias** | Profissional responsável pelos protocolos de tratamento | Validar contraindicações e o que a IA pode ou não recomendar em situações de saúde. |
| **Dono da solução** | Ex.: Product Owner do Assistente | Responder pela solução no dia a dia (*accountable*); acompanhar métricas; acionar reavaliação quando houver mudança ou degradação. |

## 9. Monitoramento e incidentes
- Toda solução de risco Médio ou Alto tem **indicadores de monitoramento** definidos (ver [matriz de riscos](matriz_riscos.md) e o plano de rollout da Etapa 4).
- **É incidente de IA:** resposta que coloque em risco a saúde do cliente, exposição de dado pessoal, promessa indevida que gere reclamação formal, comportamento discriminatório ou indisponibilidade prolongada.
- **Qualquer colaborador** que perceber um incidente comunica o IA Champion da área ou a Segurança da Informação no mesmo dia.
- O dono da solução pode **suspender** a solução (voltar ao atendimento humano) sem esperar o Comitê. Na dúvida, desliga-se primeiro e analisa-se depois.

## 10. Capacitação
Quem usa ou desenvolve IA faz uma capacitação básica sobre esta política: o que pode e o que não pode, dados sensíveis e como reportar incidentes. Para a equipe de Dados e IA, a capacitação inclui avaliação, observabilidade e segurança de LLMs.

## 11. Descumprimento
O uso em desacordo com esta política é tratado conforme as normas internas. Soluções fora do inventário são suspensas até a regularização.

---
*Esta política é um documento de governança interna e não substitui análise jurídica sobre a LGPD, o CDC ou outras normas aplicáveis.*
