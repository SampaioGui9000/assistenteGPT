# Etapa 1 — Planejamento do assistente "Hermex Prazos"

## 1. Problema a ser resolvido
Cada pessoa da equipe comercial informa prazos de entrega diferentes, o que gera expectativas irreais e reclamações. Os dados confirmam o efeito: a correlação entre a nota NPS e os dias do pedido até a entrega é de -0,94 (ver `06_analise_dados.md`). O assistente padroniza a resposta: dado o estado de destino, devolve o prazo estimado a partir de **uma única tabela oficial**.

## 2. Critérios de resposta
| Critério | Definição |
|---|---|
| Estado de destino | Sigla, nome do estado ou capital; se faltar, o assistente pergunta |
| Região | Derivada do estado (Sudeste, Sul, Centro-Oeste, Nordeste, Norte) |
| Tipo de frete | Somente frete padrão; expresso = "sem dados" |
| Prazo | Mínimo e máximo, em dias úteis |

## 3. Formato de saída
Tabela com as colunas **Estado | Região | Prazo mínimo | Prazo máximo | Observações**, seguida do aviso de que o prazo é uma estimativa.

## 4. Tabela única de prazos (decisão de projeto)
O enunciado traz duas versões (etapa 1: SP 2–4 e Norte/Nordeste 8–15; etapa 4: Sudeste 2–5, Nordeste 6–12, Norte 8–16). Adotamos **a tabela da etapa 4** no GPT, no Notion e no dashboard:

| Região | Prazo (dias úteis) |
|---|---|
| Sudeste | 2–5 |
| Sul | 3–6 |
| Centro-Oeste | 4–7 |
| Nordeste | 6–12 |
| Norte | 8–16 |

## 5. Matriz CSD
| Tipo | Item | Como será tratado nas instruções do GPT |
|---|---|---|
| **Certeza** | Os estados pertencem a 5 regiões e cada região tem faixa de prazo na tabela acima | Entra como regra fixa na seção "Tabela de prazos"; a resposta usa só esses números |
| **Certeza** | O prazo mínimo e o máximo são sempre informados juntos | Colunas obrigatórias no formato de saída |
| **Certeza** | Em média, o transporte (envio → recebimento) fica dentro da faixa de cada região nos dados de abril/2025 (100% dos 60 pedidos) | Sustenta o uso da tabela como estimativa de transporte |
| **Suposição** | A faixa de prazo conta a partir da postagem (envio), não do pedido | O aviso diz "estimativa"; cada resposta lembra que o prazo depende da postagem. **Validar com a liderança** |
| **Suposição** | Dias úteis (a base de dados mede dias corridos) | Assistente sempre escreve "dias úteis"; validar a conversão |
| **Suposição** | Norte e Nordeste concentram o risco de atraso | Campo "Observações" recomenda alinhar expectativa e acompanhar o rastreio |
| **Dúvida** | A empresa oferece frete expresso? Para quais regiões? | Assistente responde "não possuo dados" e encaminha à liderança. Nunca inventa |
| **Dúvida** | Há prazo diferenciado para capitais × interior? | Fora do escopo: não diferencia; avisa que é prazo por estado |
| **Dúvida** | Como o prazo muda em feriados, Black Friday ou greves? | Aviso de "sujeito a variações"; sem números extras |
| **Dúvida** | Quanto tempo leva do pedido à postagem? (nos dados: média de 3 dias, até 5–6 no Norte/Nordeste) | Não entra na resposta; registrado como pendência para a liderança |

## 6. Briefing completo
O briefing (personalidade, tarefa com cadeia de pensamento de 5 etapas numeradas, formato de saída, cuidados e exemplos) está em **`briefing_gpt_hermex_prazos.txt`**, pronto para colar no campo *Instruções* do GPT.

## 7. Configuração do GPT (passo a passo no ChatGPT)
1. ChatGPT → *Explorar GPTs* → *Criar*, aba **Configurar**.
2. **Nome:** Hermex Prazos.
3. **Descrição:** Assistente logístico da Hermex Log que informa o prazo estimado de entrega por estado, com base na tabela oficial da empresa.
4. **Instruções:** cole todo o conteúdo de `briefing_gpt_hermex_prazos.txt`.
5. **Quebra-gelos:**
   - Qual o prazo para entrega em Salvador?
   - Compare os prazos de SP, PR e AM.
   - Qual o prazo para o Norte do país?
   - Vocês têm frete expresso para o Nordeste?
6. **Recursos:** desmarque *Geração de imagens* e *Canvas/quadro branco*; deixe *Busca na web* desmarcada (para evitar que o GPT use prazos externos); *Interpretador de código* desmarcado.
7. Salvar como "Apenas eu" ou "Qualquer pessoa com o link".

## 8. Roteiro de testes (preencher com o resultado obtido)
> Os resultados abaixo são o **comportamento esperado**. Não executei o GPT por você; cole a resposta real na coluna "Obtido".

| # | Entrada | Resultado esperado | Obtido | Seguiu os 5 passos? | Formato OK? |
|---|---|---|---|---|---|
| 1 | "Prazo para São Paulo?" | SP · Sudeste · 2 · 5 dias úteis + aviso | | | |
| 2 | "Quanto tempo para entregar em Salvador?" | BA · Nordeste · 6 · 12 dias úteis + obs. de rastreio | | | |
| 3 | "E para Manaus?" | AM · Norte · 8 · 16 dias úteis + obs. de alinhar expectativa | | | |
| 4 | "Tem frete expresso para o AM?" | Diz que não tem dados de expresso; informa o padrão | | | |
| 5 | "Prazo para Lisboa" | Recusa: só atende Brasil | | | |
| 6 | "Quero entregar no Nordeste" (sem estado) | Pergunta a UF | | | |

**Critérios de avaliação:** (a) a resposta traz a tabela com as 5 colunas; (b) os números batem com a tabela; (c) não promete prazo; (d) mostra o aviso de estimativa; (e) não inventa dados para casos sem informação.

**Se falhar:** formato não seguido → reforçar "Formato de saída (obrigatório)"; prazo inventado → manter o cuidado "Responda SOMENTE com base...", já incluído; resposta genérica → conferir o passo 2 (verificar a região) e os exemplos.
