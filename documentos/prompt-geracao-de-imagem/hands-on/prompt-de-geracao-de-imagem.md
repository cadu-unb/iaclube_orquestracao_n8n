# Prompt de geração de imagem: Hands on

Visão geral e a resposta curta: [prompt-de-geracao-de-imagem.md](../prompt-de-geracao-de-imagem.md).

**O Hands on não gera imagens.** Não existe prompt de imagem nesse conjunto, nem para o gerador local nem para uma IA externa.

## Por quê

Os cards do conjunto `hands-on` são só texto: `capa`, `texto-titulo-grande`, `passo-a-passo`, `texto-titulo-compacto` e `encerramento`. Nenhum deles tem espaço para imagem (o catálogo do gerenciador não lista nenhuma máscara `imagem_*` neles).

O que existe é um modelo **emprestado** das Notícias, `texto-com-imagem` (aprovado em 12/10 no `iaclube_n8n`), que poderia ser usado num carrossel Hands on. O fluxo `completo/hands_on-completo` **não o usa**.

## O que isso significa no fluxo

[`workflows/completo/hands_on-completo.workflow.json`](../../../workflows/completo/hands_on-completo.workflow.json):

- não tem os nós do gerador de imagens (sobe só o gerenciador de carrosséis, produz os cards e o desliga);
- o prompt da IA do texto **não** pede `prompt_imagem`;
- não há `estilo_documento` na **Configuração**, nem tamanho de imagem.

## Não confundir com o "prompt pronto" do post

Os posts de Hands on trazem um **prompt de texto** para os leitores copiarem (o campo `prompt_exemplo`, que vai na legenda e na seção `## PROMPT PRONTO` do card do Trello). Ele ensina a usar uma ferramenta de IA e **não tem relação** com geração de imagem.

## Se um dia o Hands on tiver imagens

Nada disso foi feito. O caminho seria:

1. escolher quais cards ganham imagem (usando o modelo emprestado `texto-com-imagem`);
2. pedir `prompt_imagem` à IA, como no Dicionário (veja [dicionario/](../dicionario/prompt-de-geracao-de-imagem.md));
3. copiar para o fluxo os nós do gerador de imagens do `dicionario-completo`;
4. criar um documento de estilo do Hands on (`estilo-hands-on.md`, na pasta compartilhada) e o `estilo_documento` dele (a cor de acento do conjunto é o amarelo `#fbbb20`).
