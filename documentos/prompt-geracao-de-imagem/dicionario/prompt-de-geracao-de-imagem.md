# Prompt de geração de imagem: Dicionário

Visão geral e a resposta curta: [prompt-de-geracao-de-imagem.md](../prompt-de-geracao-de-imagem.md).

O Dicionário (`completo/dicionario-completo`) gera **2 imagens por post**, uma para cada card com imagem do conjunto `dict-v1`. O prompt de cada uma é `cena, estilo`: a **cena** é escrita pela IA do texto e o **estilo** é um texto fixo do fluxo.

| Slide de desenvolvimento | Card | Imagem |
|---|---|---|
| 1º (a analogia do dia a dia) | `texto-com-imagem-1` | sim |
| 2º (como funciona por dentro) | `texto-com-imagem-2` | sim |
| 3º e 4º | `texto` e `texto-com-inicio-fino` | não (só texto) |

Os outros cards (capa, definição, encerramento) também não têm imagem.

## O estilo fixo

> flat vector editorial illustration, bold simple shapes, soft gradients, vivid red-orange and deep navy palette on a warm off-white background, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark

- Fica em [`workflows/completo/dicionario-completo.workflow.json`](../../../workflows/completo/dicionario-completo.workflow.json): nó **Configuração**, campo `estilo_comum`.
- Tamanho: 624 × 416 (`largura` e `altura`), cerca de 4 minutos por imagem.
- Foi escrito por Claude em 20/10 a partir das cores do card do Dicionário (fundo `#f2f2f1`, texto `#0e1626`, acento `#e63415`). É a versão "vermelho e azul-marinho" do estilo das Notícias (que usa azul e amarelo). Não vem do catálogo do gerador.

## A cena, escrita pela IA

A IA que escreve o texto recebe, dentro do prompt dela, esta instrução (trecho exato do nó **AI Agent - Dicionario**):

```
AS IMAGENS
Os dois primeiros slides de desenvolvimento levam uma ilustracao, criada por um
gerador de imagens local a partir do campo "prompt_imagem". Escreva esse campo assim:
- em INGLES: o gerador de imagens entende ingles bem melhor
- uma cena concreta e simples que mostre a ideia do slide por metafora visual:
  objetos, lugar e clima (no 1o slide, a analogia do dia a dia; no 2o, o
  funcionamento). Exemplo: "a small desk with only a few papers fitting on it,
  an older paper sliding off the edge, calm studious mood"
- sem texto, letras, numeros, logotipos nem nome de empresa, marca ou produto:
  o gerador escreve mal e nao deve imitar marca
- sem pessoas reais e sem rostos reconheciveis
- nao descreva estilo de arte, cores nem enquadramento: a automacao acrescenta
  sozinha o estilo visual da pagina, igual para todas as imagens
- entre 60 e 300 caracteres, e uma cena diferente para cada imagem
Os outros slides nao levam "prompt_imagem".
```

- **Modelo:** `OpenAI Chat Model` (gpt-5.4-pro, limite de 8000 tokens de saída). É o único modelo ligado nesse fluxo.
- **Conferência:** o nó **Parse** avisa se um dos dois primeiros slides de desenvolvimento vier sem `prompt_imagem` ou com mais de 300 caracteres. O aviso aparece no card do Trello.
- **Se a IA não mandar a cena:** o nó **Montar entrada dos cards** usa `a simple friendly editorial illustration that explains the artificial intelligence concept: ` + o termo.
- **Nome do arquivo gerado:** `dicionario-<termo>-1` e `dicionario-<termo>-2`.
- **Onde ver a cena escrita pela IA:** no card do Trello, na seção `## PROMPTS DE IMAGEM`.

## Execução real: Mixture of Experts (MoE), 20/10 às 14:32

Os dois prompts finais, como estão gravados nas imagens (`20261020-143258-dicionario_mixture_of_experts_moe_1.png` e `_2.png`). Em cada um, a **cena** é o que vem antes de `flat vector editorial illustration` e o resto é o estilo fixo.

1. > a hospital corridor with many treatment room doors, one sealed folder on a rolling cart rolling toward a single open room while the other rooms stay closed, clean organized atmosphere, flat vector editorial illustration, bold simple shapes, soft gradients, vivid red-orange and deep navy palette on a warm off-white background, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark
2. > a machine room with many connected modules and wires, only a few modules glowing and sending signals into one shared output channel, the other modules dim and inactive, flat vector editorial illustration, bold simple shapes, soft gradients, vivid red-orange and deep navy palette on a warm off-white background, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark

Parâmetros do motor nas duas: 8 passos, CFG 1,0, semente 42, 624 × 416.

## Onde mudar

| Quero mudar… | Onde |
|---|---|
| o estilo das imagens | `estilo_comum` na **Configuração** do `dicionario-completo` |
| como a IA escreve a cena | o trecho acima, no nó **AI Agent - Dicionario** |
| o tamanho | `largura` e `altura` na **Configuração** (múltiplos de 16) |
