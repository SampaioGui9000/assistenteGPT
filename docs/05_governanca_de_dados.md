# Governança de Dados — Base de Conhecimento da Hermex Log

## (a) Responsáveis pela atualização (lógica RACI)
Papéis: **R** atualiza o conteúdo; **A** aprova e responde pela versão publicada; **C** é consultado; **I** é informado. Cada base tem um único A.

| Base no Notion | Vendas | Pós-Vendas | Liderança | N8N / Chatbot |
|---|---|---|---|---|
| Política de Devolução | C | R | A | I |
| Processo de Reembolso | C | R | A | I |
| SLA de Entrega por Região | R | C | A | I |

*Regras:* o N8N e o futuro chatbot só **consomem**; nenhuma resposta do chatbot altera a base. Mudanças só valem depois da aprovação da Liderança, e a data da última revisão aparece no topo de cada página.

*Observação:* no SLA, Vendas é R porque aplica os prazos no dia a dia e percebe as divergências primeiro. A tabela numérica precisa ser alterada em **um só lugar** (Notion) e replicada no GPT "Hermex Prazos".

## (b) Frequência de revisão
| Base | Revisão ordinária | Revisão extra (gatilho) |
|---|---|---|
| Política de Devolução | Trimestral | Mudança de lei, de política comercial ou aumento de reclamações de devolução |
| Processo de Reembolso | Trimestral | Troca de meio de pagamento/gateway ou de prazo contratado |
| SLA de Entrega por Região | **Mensal** | Mudança de transportadora, greve, alta temporada (Black Friday/Natal), queda de NPS regional |
| Planilha de NPS e dashboards | Semanal (conferência de dados) | Falha do workflow |

## (c) Riscos de uma base desatualizada
- **Respostas incorretas do chatbot:** o bot afirma um prazo de devolução ou de reembolso que já mudou. O cliente age com base nisso e reclama, abre disputa ou pede indenização.
- **Alucinação e falsa autoridade:** o modelo de linguagem preenche lacunas com o que parece plausível. Quando o texto é antigo, ele repete o erro com a mesma confiança. Em uma base com dados contraditórios (duas tabelas de prazo diferentes, como no enunciado deste projeto), o bot escolhe uma sem avisar.
- **Expectativa irreal de prazo:** no nosso diagnóstico, a correlação entre nota e dias até a entrega é -0,94; um bot que promete prazo menor que o real piora o NPS.
- **Risco jurídico e financeiro:** promessas sobre reembolso ou devolução que a empresa não cumpre.
- **Perda de confiança interna:** a equipe para de consultar a base, que é o problema que o projeto quer resolver.
- **Mitigações:** data de revisão visível; responsável nomeado; uma única fonte de verdade por assunto; teste mensal com 10 perguntas-padrão ao chatbot; o bot deve dizer "não sei" e encaminhar ao pós-vendas quando não houver fonte.

## (d) Por que dados semânticos funcionam melhor para LLMs que dados operacionais brutos
1. **Contexto e significado:** uma linha `P004,BA,2025-04-06,2025-04-14,2` não diz o que é prazo, o que é bom ou o que fazer. Um parágrafo como "o prazo para o Nordeste é de 6 a 12 dias úteis" já traz a regra, a unidade e a condição.
2. **Linguagem natural é o formato nativo do modelo:** o LLM é treinado para interpretar texto; ele não "calcula" planilhas com segurança.
3. **Recuperação por chunks (RAG):** ao vetorizar, cada bloco do Notion vira um chunk. Parágrafos coesos e autocontidos geram chunks com sentido; células soltas geram vetores ruidosos.
4. **Rastreabilidade e explicação:** o bot pode citar a página usada ("conforme a Política de Devolução"), o que permite auditar a resposta.
5. **Menos alucinação:** com a regra escrita, o modelo reproduz o texto em vez de inferir.

*Papel dos dados brutos:* continuam essenciais para medir (dashboard, NPS, SLA). O ecossistema ideal usa **os dois**: os números sustentam a decisão da liderança e o texto interpretado alimenta os agentes. Os insights da análise (ex.: "Norte e Nordeste concentram o NPS negativo") devem virar texto na base para que um chatbot possa usá-los.
