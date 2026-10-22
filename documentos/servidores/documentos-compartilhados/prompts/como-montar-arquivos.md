---
titulo: Como montar arquivos
tipo: outros
tags: [guia]
origem: 8000
---
# Como montar arquivos

## Para que serve esta página

A página **Diretrizes** é o lugar onde ficam guardados, em arquivos de texto, os **prompts** (o que se pede a uma IA) e os **glossários** (o que cada termo e cada caixa significa). Ela **guarda e organiza**: não escreve nada sozinha, não chama IA e não publica nada em lugar nenhum. Salvar é só gravar o arquivo.

O uso principal: para cada conjunto de cards há um arquivo **Como montar os cards de…** que ensina a IA a montar os cards daquele conjunto. Quem monta o pedido junta a **informação bruta** (em qualquer formato) com o guia do conjunto, e a IA devolve o **JSON** que o programa transforma nos cards.

## O bloco do início

Todo arquivo pode começar por um bloco entre duas linhas `---`, com o título, o tipo e as tags. Você não precisa digitar isso: a tela monta o bloco a partir dos campos **Título**, **Tipo** e **Tags**.

## Os tipos

- **Prompt:** um pedido, ou um pedaço de pedido, para uma IA.
- **Glossário:** a explicação de termos, caixas e limites.
- **Outros:** qualquer outro texto, como este.

Sem escolher, o tipo é **Outros**.

## As tags

Tags são palavras para achar o arquivo depois (por exemplo, `noticias` e `ia`). Maiúscula e acento não importam: `Notícias` e `noticias` são a mesma tag. Cada arquivo aceita até 20 tags.

## Citar outro arquivo

Para citar outro arquivo, escreva um link Markdown com o **nome exato** dele: o texto entre colchetes e, entre parênteses, o nome com `.md` (veja o prompt de Notícias, que cita o guia de Notícias assim). Em **Ver resultado** o link abre aquele arquivo; se o arquivo não existir, o link aparece marcado como "arquivo não encontrado". Ao **renomear** um arquivo, o programa mostra quem o cita e oferece atualizar os links.

## Ver resultado

O botão **Ver resultado** mostra o texto já formatado (títulos, listas, tabelas e código). **Voltar a editar** devolve a caixa com o seu texto, mesmo sem salvar. Os botões acima da caixa (**Título**, **Negrito**, **Itálico**, **Lista**, **Link** e **Código**) colocam a marca do Markdown para você.

## Onde ficam os arquivos

Na pasta `diretrizes/` do espaço de trabalho, um arquivo `.md` por texto. Para levar tudo a outro computador, copie essa pasta. Depois de salvos, estes arquivos são **seus**: o programa não os recria nem os sobrescreve, e, se você apagar um, ele não volta. Para refazer o guia de um conjunto a partir do catálogo, use **Gerar guia de um conjunto** na lista (ele cria um arquivo novo, nunca sobrescreve).
