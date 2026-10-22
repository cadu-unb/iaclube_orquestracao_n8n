---
titulo: Como montar os cards de Dicionário IA (v2)
tipo: prompt
tags: [guia-de-cards, dicionario-ia-v2]
origem: 8000
---
# Como montar os cards de Dicionário IA (v2)

## O seu papel

Você monta o **texto de um carrossel do conjunto Dicionário IA (v2)**. Vai receber duas coisas: (1) a **informação bruta**, que pode vir em qualquer formato (texto corrido, lista, tópicos, dados de outra ferramenta) e (2) **este guia**. Leia a informação, decida o que entra em cada card e responda **somente com o JSON**, sem explicação antes nem depois. O programa transforma o JSON nos cards.

## Como pensar o carrossel

- A ordem padrão dos cards é: capa → definicao → texto-com-imagem → texto-com-inicio-fino-1 → texto → texto-com-inicio-fino-2 → encerramento.
- Um carrossel tem de 1 a 20 cards. Cada item de `cards` é um card e a ordem do JSON é a ordem do carrossel.
- Comece pelo que prende a atenção, termine fechando a ideia. Um assunto por card.
- As caixas `extra_1` e `extra_2` são **opcionais**: use só se sobrar uma informação importante; no mais, deixe de fora.
- Não invente fatos, números nem nomes. Se faltar um dado, deixe a caixa de fora (caixa ausente fica vazia; é melhor que inventar).
- Escreva em português do Brasil, com frases curtas e diretas.
- **Respeite o tamanho de cada caixa** (veja os modelos abaixo): texto maior que o tamanho de referência sai apertado ou cortado. Quando o texto não couber, **reescreva mais curto**, não corte no meio da frase.

## Os modelos de card

O campo `modelo` de cada card usa o código entre parênteses. O conjunto tem 7 modelos.

### Capa (`capa`)

Quando usar: abre o carrossel; é o primeiro card e aparece uma vez. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: O título chama a atenção e diz o recorte (o tema ou o período); o texto convida a deslizar.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 22 caracteres**, em até 3 linhas; marcadores: todos.
  Exemplo: {leve|A IA pode / te} / esquecer.
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 58 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 87 caracteres**, em até 3 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Em conversa longa, ela pode ignorar instruções certas porque o começo já saiu de vista.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 58 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Definição (frase antes do título) (`definicao`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `antetitulo` (Frase antes do título; obrigatória): **até 6 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: Isso é
- `titulo` (Título; obrigatória): **até 18 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Janela de / contexto
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 76 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 152 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Janela de contexto é o pedaço da conversa que o modelo consegue considerar ao responder. /  / É a área de trabalho mental da IA: se lota, algo fica de fora.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 76 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com imagem (`texto-com-imagem`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 23 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Pensa numa / **mesa pequena**
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 175 caracteres**, em até 5 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Imagina estudar com uma mesa onde só cabem alguns papéis. /  / Para colocar uma folha nova, você tira outra. A IA faz algo parecido com mensagens, instruções e trechos de arquivo.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

Imagens (`imagem_1`): **não escreva nada sobre elas no JSON**; a pessoa escolhe as imagens depois, no programa.

### Texto com início fino 1 (`texto-com-inicio-fino-1`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 32 caracteres**, em até 3 linhas; marcadores: todos.
  Exemplo: {normal|O tamanho} não é / só em mensagens.
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 54 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 163 caracteres**, em até 6 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Essa janela não conta quantas perguntas você fez, e sim tokens: pedaços de texto. /  / Um PDF grande, um código longo ou muitas respostas podem ocupar tudo bem rápido.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 54 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto (`texto`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 26 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: É aqui que o erro / aparece:
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 169 caracteres**, em até 5 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Quando a janela enche, o modelo pode esquecer sua regra inicial, resumir mal um documento ou se contradizer. Parece desatenção, mas muitas vezes é só limite de contexto.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com início fino 2 (`texto-com-inicio-fino-2`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 28 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: {normal|O erro comum é} / empilhar tudo
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 61 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 152 caracteres**, em até 5 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Muita gente joga histórico inteiro, 12 links e um PDF gigante no mesmo prompt. Melhor é resumir, repetir a instrução-chave e dividir a tarefa em etapas.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 61 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Encerramento (`encerramento`)

Quando usar: fecha o carrossel; é o último card. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Feche a ideia com uma pergunta ou um convite e, se couber, a marca do perfil.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 17 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Ficou mais / claro?
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 81 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 122 caracteres**, em até 3 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Se **Janela de contexto** fez sentido agora, tem termo novo toda semana no **@iaclube**. O resto do conteúdo está em iaclube.help.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 81 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

## Quebra de linha e marcadores

Use `\n` dentro do texto para quebrar a linha (títulos costumam usar). Para destacar um trecho: `{negrito|texto}` (por nome), `{w=300|texto}` (peso de 100 a 900), `{t=85|texto}` (tamanho em % da caixa) ou, no estilo WhatsApp, `*negrito*`, `_itálico_`, `__sublinhado__` e `~~taxado~~`. Efeitos que existem: `negrito`, `normal`, `fino`, `extra`, `italico`, `sublinhado`, `taxado`, `menor`, `maior`. Cada caixa aceita só alguns (campo **marcadores** acima); o que ela não aceita só gera aviso. Use marcador com moderação.

## Avisos de tamanho

Sem aviso até 10% acima do tamanho de referência; nível 1 de 10% a 15%; nível 2 de 15% a 20%; nível 4 acima de 20% (ou quando o texto estoura o card de verdade).

## O formato da resposta

Responda com **um único objeto JSON**: o cabeçalho (`serie`, e se quiser `data`, `assunto` e `marca`) e a lista `cards`, cada card com `modelo` e `campos`. Exemplo com os dois primeiros cards do conjunto:

```json
{
  "serie": "dict-v2",
  "data": "2026-10-05",
  "assunto": "meu assunto",
  "marca": "@iaclube",
  "cards": [
    {
      "modelo": "capa",
      "campos": {
        "titulo": "{leve|A IA pode\nte}\nesquecer.",
        "corpo": "Em conversa longa, ela pode ignorar instruções certas porque o começo já saiu de vista."
      }
    },
    {
      "modelo": "definicao",
      "campos": {
        "antetitulo": "Isso é",
        "titulo": "Janela de\ncontexto",
        "corpo": "Janela de contexto é o pedaço da conversa que o modelo consegue considerar ao responder.\n\nÉ a área de trabalho mental da IA: se lota, algo fica de fora."
      }
    }
  ]
}
```

## Antes de responder, confira

- `serie` é `dict-v2` e todo `modelo` é um dos códigos acima.
- Nenhuma caixa passa do tamanho de referência.
- Nenhuma imagem foi mencionada no JSON.
- A resposta é só o JSON, sem texto em volta.
