---
titulo: Prompt de Notícias IA
tipo: prompt
tags: [noticias, ia]
---
# Prompt de Notícias IA

Você vai receber **notícias sobre inteligência artificial**, em qualquer formato (texto corrido, lista, tópicos ou dados de outra ferramenta), e deve montar o **texto de um carrossel**. Responda **somente com o JSON**, sem explicação antes nem depois.

## O que fazer

1. Leia toda a informação e separe de três a seis assuntos que mereçam um card cada. Ignore o que for repetido ou sem fonte.
2. Monte os cards seguindo, **à risca**, o [guia de Notícias IA](como-montar-cards-news.md): ele diz quais modelos existem, quanto cabe em cada caixa e como é o formato do JSON.
3. Use sempre `"serie": "news"`.
4. Não invente fatos, números nem nomes. Se faltar um dado, deixe a caixa de fora.
5. O JSON **não leva imagens**: elas são escolhidas depois, no programa.

## Exemplo de resposta

```json
{
  "serie": "news",
  "data": "2026-10-05",
  "assunto": "meu assunto",
  "marca": "@iaclube",
  "cards": [
    {
      "modelo": "capa",
      "campos": {
        "titulo": "{normal|IA em foco:}\n01–07/09",
        "corpo": "Novo modelo da OpenAI, agentes fora de controle, caminhantes resgatados e processos que podem mudar a IA. Bora ver o que rolou essa semana? 👇"
      }
    },
    {
      "modelo": "indice",
      "campos": {
        "titulo": "Índice",
        "item_1": "GPT-6 Astra chegou 🚀",
        "item_2": "Agentes da IA fora de controle",
        "item_3": "Gemini mandou mal na trilha",
        "item_4": "IA prevendo o clima global",
        "item_5": "Mais jornais processam a OpenAI",
        "item_6": "\"A IA está ficando estranha\""
      }
    }
  ]
}
```
