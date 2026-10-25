# Proto-persona — Camila, a cliente que quer desacelerar

> ⚠️ **Proto-persona é uma hipótese, não uma pesquisa.** Foi construída a partir do enunciado, do dataset e de suposições do time, **sem entrevistas com clientes reais**. Nome, idade, profissão e história são **fictícios e ilustrativos**. Cada característica relevante está marcada com o grau de evidência e precisa ser validada (seção final).

Legenda: 🟢 apoiado no dataset ou no enunciado · 🟡 hipótese plausível · 🔴 pura suposição (validar antes de usar em decisão)

---

| | |
|---|---|
| **Nome (fictício)** | Camila Rocha |
| **Idade** | 36 anos 🔴 |
| **Ocupação** | Analista de RH em empresa de médio porte 🔴 |
| **Cidade** | Capital, mora a 20 minutos de uma unidade 🔴 |
| **Relação com a Calmaria** | Cliente **nova**: nunca fez um tratamento no spa 🟢 (perfil "novo" é o mais frequente no dataset: 20 de 50) |
| **Canal** | Chat do site, pelo celular 🟡 |
| **Fluência digital** | **Alta** para apps do dia a dia (banco, delivery, agendamentos); **baixa paciência** para chatbots que não entendem 🟡 |

> **"Eu sei que preciso desacelerar, mas não sei por onde começar, e não quero gastar com o tratamento errado."**

## História
Camila trabalha muitas horas e tem sentido tensão nos ombros e dificuldade para relaxar 🟡 (dores e estresse aparecem nos ids 1 e 35). Uma amiga indicou a Calmaria. Ela abriu o chat à noite, depois do trabalho, e perguntou "estou muito estressada, o que vocês recomendam?". Recebeu uma lista genérica de cinco tratamentos sem preço nem explicação 🟢 (problema relatado no enunciado: "recomendações genéricas"). Ficou sem saber qual escolher, fechou o chat e não agendou 🔴.

## Objetivos
- Encontrar **um** tratamento adequado ao que sente, sem precisar entender a diferença entre dez opções 🟡.
- Saber **preço e duração** antes de decidir 🟢 (consultar preço é a 2ª intenção mais comum: 9 de 50).
- Agendar num horário que caiba na rotina, sem ligar para ninguém 🟡.

## Necessidades
- Uma recomendação **direta**, com o motivo em uma frase ("indicada para tensão muscular") 🟡.
- **Próximo passo claro** ("posso registrar o pedido de agendamento?") 🟡.
- Segurança: se mencionar algo de saúde, quer ser orientada, não "empurrada" para um pacote 🟡.
- Saber que fala com uma IA e poder chamar uma pessoa se travar 🟡.

## Problemas e frustrações (pain points)
- Respostas genéricas, que não usam o que ela disse 🟢 (enunciado).
- Respostas inconsistentes: perguntou duas vezes e recebeu indicações diferentes 🟢 (enunciado: "inconsistentes").
- Não ter certeza se o agendamento ou o cancelamento foi feito de verdade 🟡 (risco R05 da matriz).
- Medo de escolher algo inadequado para a pele sensível 🔴 (aparece como necessidade no id 17, mas não sabemos se é dela).

## O que o assistente deve fazer por ela
1. Entender a intenção (`recomendar_tratamento`) e a necessidade (estresse, tensão).
2. Indicar no máximo 2 opções, com motivo, preço do catálogo oficial e duração.
3. Oferecer o próximo passo: registrar a solicitação de agendamento.
4. Pedir feedback (👍/👎) para aprender com a resposta.

---

## Hipóteses que precisam de validação com clientes reais

| # | Hipótese | Como validar | Critério de confirmação (proposto) |
|---|---|---|---|
| H1 | O cliente novo é o público que mais se beneficia do assistente | Conversão do chat em agendamento por perfil | Clientes novos com maior ganho de conversão no teste A/B |
| H2 | Clientes novos não sabem escolher entre tratamentos | 5 a 8 entrevistas com quem abriu o chat e não agendou | A maioria cita "não sabia qual escolher" espontaneamente |
| H3 | Preço e duração são decisivos para agendar | Entrevistas + clique em "ver preço" | Preço citado entre os 2 principais fatores |
| H4 | O canal principal é o celular, à noite | Analytics do chat (dispositivo e horário) | Maioria das sessões no mobile após as 18h |
| H5 | Recomendação com motivo gera mais confiança que uma lista | Teste A/B: improved × baseline | Maior conversão e mais 👍 no improved |
| H6 | Clientes aceitam IA quando há opção de humano | Taxa de pedido de atendente e CSAT | CSAT do grupo com IA não inferior ao sem IA |

**Atenção a vieses:** a persona é uma mulher porque o time imaginou assim, não porque o dataset mostra o gênero (ele não tem esse dado). Ao validar, entreviste pessoas de perfis diferentes e não use gênero para personalizar recomendações (ver risco R07).
