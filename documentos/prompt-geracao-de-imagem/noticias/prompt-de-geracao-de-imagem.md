# Prompt de geração de imagem: Notícias

Visão geral e a resposta curta: [prompt-de-geracao-de-imagem.md](../prompt-de-geracao-de-imagem.md).

Hoje há **dois caminhos** para as imagens das Notícias. Eles montam o prompt do mesmo jeito (`cena, estilo`); muda quem escreve a **cena**.

| | `noticias-2-arte` | `completo/noticias-completo` |
|---|---|---|
| Quem escreve a cena | uma pessoa, no arquivo [`entradas/exemplo-noticias-10.json`](../../../entradas/exemplo-noticias-10.json) | a IA que escreve o texto (Claude Sonnet 4.6), no campo `prompt_imagem` de cada notícia |
| De onde vem o estilo | `estilo_comum` do mesmo arquivo | `estilo_comum` do nó **Configuração** |
| Imagens | 10 (uma por notícia do arquivo) | uma por notícia escolhida (4 a 6) |
| Já gerou imagens? | **sim**, com os prompts do arquivo: 19/10 (12:57, 13:48, 17:21) e 20/10 (11:48), 10 imagens cada, e 20/10 às 13:54 (2 imagens) | **não**: não há nenhuma imagem com prompt escrito pela IA das Notícias |

## O estilo fixo

O mesmo texto, em dois lugares (se mudar um, mude o outro):

> flat vector editorial illustration, bold simple shapes, soft gradients, blue and warm yellow palette, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark

- Em [`workflows/completo/noticias-completo.workflow.json`](../../../workflows/completo/noticias-completo.workflow.json): nó **Configuração**, campo `estilo_comum`.
- Em [`entradas/exemplo-noticias-10.json`](../../../entradas/exemplo-noticias-10.json): campo `estilo_comum`.
- Tamanho: 624 × 416 (nó **Configuração**: `largura` e `altura`).

Foi escrito por Claude em 18/10, junto com o arquivo de exemplo. Não vem do catálogo do gerador nem de uma regra aprovada.

## Caminho 1: `noticias-2-arte` (prompts escritos à mão)

O arquivo de exemplo tem 10 cenas. Cada uma vira `cena, estilo` e é pedida ao gerador:

| Card | Arquivo | Cena (prompt) |
|---|---|---|
| 2 | `noticia-01-dna` | a glowing double helix of DNA surrounded by floating data panels and a soft scanning beam, scientific discovery mood |
| 3 | `noticia-02-agentes-wiki` | small friendly robot agents wandering out of a fenced garden onto a web of connected pages, a hint of mischief, sense of lost control |
| 4 | `noticia-03-investigacao` | a detective magnifying glass over a tangled circuit board with a question mark shaped cable, investigative mood |
| 5 | `noticia-04-mistral` | a stack of gold coins forming a rising tower beside a stylized European map outline made of circuit lines, investment and sovereignty mood |
| 6 | `noticia-05-premiere` | a video editing timeline with film strips and a sparkling magic wand adding new frames, creative workflow mood |
| 7 | `noticia-06-jornais` | stacked newspapers facing a large balance scale against a glowing server rack, legal dispute mood |
| 8 | `noticia-07-ia-celular` | a smartphone with a small glowing brain chip inside a protective shield, privacy and speed mood |
| 9 | `noticia-08-agentes-trabalho` | a tidy desk with an inbox, a calendar and a helpful robot arm sorting tasks automatically, productive calm mood |
| 10 | `noticia-09-voz` | a sound wave turning into a smooth human silhouette speaking, microphone in front, warm natural voice mood |
| 11 | `noticia-10-energia` | a data center building connected by power lines to a wind turbine and a solar panel, energy demand mood |

Estes são os prompts de **todas** as imagens de Notícias geradas até agora (o texto gravado em cada PNG bate com esta tabela). Exemplo de prompt final, gravado na imagem `noticia_07_ia_celular` (19/10 às 17:21):

> a smartphone with a small glowing brain chip inside a protective shield, privacy and speed mood, flat vector editorial illustration, bold simple shapes, soft gradients, blue and warm yellow palette, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark

## Caminho 2: `noticias-completo` (cena escrita pela IA)

A IA que escreve o texto recebe, dentro do prompt dela, esta instrução sobre a imagem (trecho exato do nó **AI Agent - Noticias**):

```
A IMAGEM DE CADA NOTICIA
Cada card de noticia leva uma ilustracao, criada por um gerador de imagens local
a partir do campo "prompt_imagem". Escreva esse campo assim:
- em INGLES: o gerador de imagens entende ingles bem melhor
- uma cena concreta e simples que represente a noticia por metafora visual:
  objetos, lugar e clima. Exemplo: "a smartphone with a small glowing chip
  inside a protective shield, privacy and speed mood"
- sem texto, letras, numeros, logotipos nem nome de empresa, marca ou produto:
  o gerador escreve mal e nao deve imitar marca
- sem pessoas reais e sem rostos reconheciveis
- nao descreva estilo de arte, cores nem enquadramento: a automacao acrescenta
  sozinha o estilo visual da pagina, igual para todas as imagens
- uma cena diferente para cada noticia
```

- **Modelo:** `Anthropic Chat Model` (claude-sonnet-4-6). O nó `OpenAI Chat Model` (gpt-5.4-pro) está no fluxo, mas **desligado**.
- **Conferência:** o nó **Parse** avisa se faltar `prompt_imagem` ou se passar de 300 caracteres. O aviso aparece no card do Trello.
- **Se a IA não mandar a cena:** o nó **Montar entrada dos cards** usa `an editorial illustration about artificial intelligence news, ` + o rótulo (ou a manchete) da notícia.
- **Nome do arquivo gerado:** `noticia-NN-<rotulo>`.
- **Onde ver a cena escrita pela IA:** no card do Trello, na seção `## PROMPTS DE IMAGEM`.

## Onde mudar

| Quero mudar… | Onde |
|---|---|
| o estilo das imagens | `estilo_comum` na **Configuração** do `noticias-completo` **e** em `entradas/*.json` |
| como a IA escreve a cena | o trecho acima, no nó **AI Agent - Noticias** do `noticias-completo` |
| uma cena específica (caminho 1) | o campo `prompt` do item em `imagens[]` do arquivo de entrada |
| o tamanho | `largura` e `altura` na **Configuração** (múltiplos de 16) |
