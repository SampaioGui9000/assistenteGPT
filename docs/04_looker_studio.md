# Etapa 4 (parte 1) — Dashboard no Looker Studio

> Não tenho acesso ao seu Looker Studio, então este guia descreve a construção passo a passo e traz os **valores esperados** (calculados em `scripts/analise.py`) para você validar o dashboard.

## 1. Fonte de dados
*Criar → Fonte de dados → Google Sheets* → planilha `pesquisa_satisfacao` → aba principal (dados do CSV, **não** a aba de respostas do Forms). Ajuste os tipos:

| Campo | Tipo |
|---|---|
| `estado` | Geográfico → **Subdivisão do país (nível 1)** (valores em sigla de 2 letras; se o mapa não reconhecer, teste "Endereço" ou use o nome completo do estado) |
| `data_pedido`, `data_envio`, `data_recebimento` | Data (AAAA-MM-DD) |
| `nota_nps` | Número |

Dica: o Looker pode tratar siglas como "SP" e "PA" sem problemas, mas o país precisa estar definido como Brasil no gráfico de mapa (Zona geográfica: Brasil).

## 2. Campos calculados
| Campo | Fórmula | Observações |
|---|---|---|
| Promotores | `IF(nota_nps > 8, 1, 0)` | notas 9 e 10 |
| Detratores | `IF(nota_nps < 7, 1, 0)` | notas 0 a 6 |
| NPS | `(SUM(Promotores)/COUNT(nota_nps)) - (SUM(Detratores)/COUNT(nota_nps))` | Formatar como **Porcentagem**; agregação "Automática" (sem soma extra) |
| Dias até envio | `DATE_DIFF(data_envio, data_pedido)` | usar com agregação **Média** |
| Dias até entrega | `DATE_DIFF(data_recebimento, data_pedido)` | usar com agregação **Média** |

Se `DATE_DIFF` reclamar de argumentos, verifique se os campos são do tipo Data e use `DATETIME_DIFF`/`DATE_DIFF(data_fim, data_inicio)` conforme a versão do Looker.

## 3. Visualizações
| # | Visualização | Configuração |
|---|---|---|
| a | **Scorecards** (3) | NPS (porcentagem); soma de Promotores; soma de Detratores |
| b | **Mapa do Brasil** (mapa de preenchimento) | Dimensão: `estado`; métrica: média de `nota_nps` (NPS médio por estado); cores: gradiente do **vermelho** (valor mínimo) ao **azul** (valor máximo) |
| c | **Barras** | Dimensão: `estado`; métrica: média de Dias até entrega; ordenar decrescente |
| d | **Tabela** | `estado`, contagem de respostas (`id_pedido` Count), NPS, média de Dias até envio, média de Dias até entrega; formatação condicional (NPS em vermelho se < 0) |

Extras sugeridos: controle de filtro por **estado** e por intervalo de `data_pedido`; texto de título "Hermex Log — NPS e SLA de entrega".

*Sobre o mapa:* "NPS médio por estado" pode ser lido de duas formas. O enunciado fala de NPS médio; use o campo calculado **NPS** no mapa se preferir a métrica oficial, ou a média da nota. Documente a escolha no README.

## 4. Valores esperados para validação
**Scorecards (total, 60 respostas):** NPS **-26,7%** · Promotores **15** · Detratores **31**.

Por estado (NPS = métrica calculada; dias = média do pedido até o evento):

| Estado | Respostas | NPS | Dias até envio | Dias até entrega |
|---|---|---|---|---|
| SP | 13 | 92,3% | 2,0 | 4,1 |
| SC | 4 | 50,0% | 2,0 | 5,0 |
| PR | 4 | 25,0% | 2,0 | 5,0 |
| GO | 3 | -33,3% | 3,0 | 7,0 |
| MG | 5 | -40,0% | 2,0 | 5,8 |
| RJ | 6 | -50,0% | 2,2 | 6,0 |
| RS | 4 | -100% | 3,0 | 8,0 |
| BA | 5 | -100% | 4,0 | 11,8 |
| CE | 4 | -100% | 4,0 | 11,8 |
| PE | 4 | -100% | 4,0 | 11,8 |
| MA | 2 | -100% | 5,0 | 14,0 |
| PA | 3 | -100% | 5,0 | 14,7 |
| AM | 3 | -100% | 5,3 | 15,7 |

(A tabela completa está em `06_analise_dados.md`. Se os números do seu dashboard diferirem, revise o tipo dos campos e a agregação.)

## 5. Como ler o dashboard (insights)
- **O NPS cai junto com o prazo:** correlação de -0,94 entre nota e dias até a entrega; com entrega em até 5 dias o NPS é +62,5%, e acima de 8 dias é -100%.
- **Sudeste e Sul não escapam:** RJ, MG e RS têm NPS negativo com 6–8 dias. Nos dados, o prazo do Sudeste (2–5 dias) foi ultrapassado em 8 dos 24 pedidos, contando a partir do pedido.
- **Norte e Nordeste:** 21 respostas, **zero promotores**, e 100% dos clientes nessas regiões foram detratores.
- **O tempo até o envio importa:** 3 dias em média, 4–5 dias no Norte/Nordeste. Isso consome o prazo antes de o pedido sair.
