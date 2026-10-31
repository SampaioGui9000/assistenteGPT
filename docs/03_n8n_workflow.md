# Etapa 3 — Workflow n8n "Hermex — NPS Automação"

> **Importante:** o arquivo `n8n/hermex_nps_automacao.json` foi gerado sem acesso ao seu n8n e **não foi executado**. Importe (*Workflows → Import from file*), reconecte as credenciais e teste conforme a seção 5. Ajustes de versão dos nós são normais.

## 1. Preparação (Sheets e Forms)
1. Em `pesquisa_satisfacao` (Google Sheets), importe `data/pesquisa_satisfacao.csv` (*Arquivo → Importar → Substituir a planilha*). Confirme as datas como data e `nota_nps` como número.
2. Crie o Google Forms **"Hermex Log — Pesquisa de Satisfação"** com 3 campos: *ID do Pedido* (resposta curta), *Nota NPS (0-10)* (escala linear 0–10) e *Comentário* (parágrafo).
3. Aba *Respostas* → ícone do Sheets → **Selecionar planilha existente** → `pesquisa_satisfacao`. Isso cria a aba "Respostas do formulário 1".

## 2. Estrutura do workflow
| # | Nó | Função |
|---|---|---|
| 1 | Google Sheets Trigger | Dispara quando uma linha é adicionada em "Respostas do formulário 1" |
| 2 | Edit Fields (Set) | Padroniza `id_pedido`, `nota` (número) e `comentario` |
| 3 | Google Sheets (Get Row) | Busca nome e e-mail do cliente em `pesquisa_satisfacao` pelo `id_pedido` |
| 4 | IF | `nota < 7` → verdadeiro = detrator |
| 5 | HTTP Request (Gemini) | Classifica o comentário (só no caminho do detrator) |
| 6 | Edit Fields (Set) | Valida que a resposta é uma das 5 categorias; senão, "Outro" |
| 7 | Gmail | Notifica o pós-vendas (cliente, nota, categoria, comentário) |
| 8 | Gmail | Caminho falso: agradecimento ao cliente |

**Por que o nó 3 existe:** o Forms só coleta ID do pedido, nota e comentário, então nome e e-mail vêm da planilha, pelo `id_pedido`. Isso também resolve a lacuna do handoff (só P001–P030).

## 3. Decisão sobre o limiar de detrator
O enunciado pede `nota < 6`, mas o dashboard define detrator como `nota < 7` (padrão do NPS: 0 a 6). Com `< 6`, as notas 6 não receberiam nenhum e-mail nem tratamento (4 pedidos na base: P014, P026, P031, P047). O workflow usa **`< 7`** para ficar consistente. Para seguir o enunciado ao pé da letra, troque o valor 7 por 6 no nó IF e anote no README.

## 4. Configuração dos nós
**Credenciais:** Google (OAuth2) para Sheets, Sheets Trigger e Gmail; para o Gemini, crie uma credencial *Header Auth* com nome `x-goog-api-key` e valor igual à chave do AI Studio.

**Gatilho:** *Poll* a cada minuto. Envie uma resposta de teste pelo Forms e use **Pin Data** na saída do gatilho.

**Prompt do Gemini** (já no JSON):
```
Você classifica comentários de clientes de uma empresa de logística.
Classifique o comentário abaixo em UMA das categorias: Atraso, Defeito, Atendimento, Embalagem, Outro.
Responda APENAS com uma das seguintes palavras: Atraso, Defeito, Atendimento, Embalagem, Outro.
Nenhuma explicação adicional, sem pontuação.

Comentário: {{ comentário }}
```
Configuração: `temperature: 0` e `maxOutputTokens: 20`. O nó 6 faz a validação e trata respostas inesperadas como "Outro". Confira na documentação do Google se o modelo `gemini-2.5-flash` ainda está disponível; senão, troque o nome na URL.

**E-mail ao pós-vendas** (assunto e corpo, com expressões dinâmicas):
```
Assunto: [NPS] Detrator: {{$json['cliente']}} — {{$json['categoria']}}
Cliente: {{ cliente }} | Pedido: {{ id_pedido }}
Nota NPS: {{ nota }}
Categoria (IA): {{ categoria }}
Comentário original: {{ comentario }}
Aviso: a categoria foi sugerida por IA; valide antes de agir.
```
(No JSON importado, as expressões usam `$('Nó').item.json.campo`, necessárias porque os dados vêm de nós diferentes. Equivalem à sintaxe `{{$json['campo']}}` quando o campo está no nó imediatamente anterior.)

**E-mail ao cliente (caminho falso):**
```
Assunto: Obrigado pelo seu feedback, {{ cliente }}!
Olá, {{ cliente }}! Obrigado por avaliar sua experiência com a Hermex Log (nota {{ nota }}). Seu feedback nos ajuda a melhorar nossas entregas. Equipe Hermex Log
```
Troque `posvendas@exemplo.com` pelo e-mail real da equipe.

## 5. Plano de testes
Para não escrever para clientes reais, no Forms use IDs de pedido cujo e-mail na planilha seja de teste (ex.: troque o e-mail de P001 e P002 por endereços do TempEmail.org).

| Cenário | Entrada no Forms | Resultado esperado |
|---|---|---|
| Detrator | P004 · nota 2 · "Atraso absurdo de mais de 10 dias e ninguém informou nada" | IF verdadeiro → Gemini retorna **Atraso** → e-mail ao pós-vendas com Diego Rocha, 2, Atraso e o comentário |
| Promotor | P001 · nota 10 · "Entrega perfeita" | IF falso → e-mail de agradecimento a Ana Souza |
| Nota 6 | P014 · nota 6 · "Sem comunicação de rastreio" | IF verdadeiro (com `< 7`) → provavelmente **Atendimento** |
| Resposta inesperada | Comentário vazio | Categoria "Outro" (validação do nó 6) |

Preencha ao testar: *execução OK? e-mail recebido? categoria correta?* A classificação de referência dos 31 detratores está em `data/detratores_classificacao_referencia.csv` para comparar com o Gemini.

## 6. Troubleshooting (do enunciado + notas do projeto)
- Gatilho esperando para sempre: só dispara com **nova linha**; envie outra resposta pelo Forms.
- Gemini devolve frases: reforce "Responda APENAS..."; o nó de validação já trata o resto como "Outro".
- E-mail sem dados dinâmicos: confira se o campo começa com `=` (modo *Expression*), se o nó anterior executou e se o nome do campo está idêntico (acentos e espaços do Forms: "Nota NPS (0-10)", "Comentário").
- Busca do cliente vazia: o `id_pedido` digitado no Forms precisa existir em `pesquisa_satisfacao` (P001–P060).
- Limitação conhecida: o Gemini vê só um comentário por vez e escolhe uma categoria, enquanto vários dos 31 comentários de detratores citam mais de um problema (ex.: defeito e atraso). Uma extensão futura é permitir múltiplas categorias.
