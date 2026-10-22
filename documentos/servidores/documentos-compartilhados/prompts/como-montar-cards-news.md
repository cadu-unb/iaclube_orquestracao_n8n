---
titulo: Como montar os cards de Notícias IA
tipo: prompt
tags: [guia-de-cards, noticias-ia]
origem: 8000
---
# Como montar os cards de Notícias IA

## O seu papel

Você monta o **texto de um carrossel do conjunto Notícias IA**. Vai receber duas coisas: (1) a **informação bruta**, que pode vir em qualquer formato (texto corrido, lista, tópicos, dados de outra ferramenta) e (2) **este guia**. Leia a informação, decida o que entra em cada card e responda **somente com o JSON**, sem explicação antes nem depois. O programa transforma o JSON nos cards.

## Como pensar o carrossel

- A ordem padrão dos cards é: capa → indice → texto-com-imagem → texto-com-imagem → texto-com-imagem → texto-com-imagem → texto-com-imagem → texto-com-imagem → encerramento.
- Um carrossel tem de 1 a 20 cards. Cada item de `cards` é um card e a ordem do JSON é a ordem do carrossel.
- Comece pelo que prende a atenção, termine fechando a ideia. Um assunto por card.
- As caixas `extra_1` e `extra_2` são **opcionais**: use só se sobrar uma informação importante; no mais, deixe de fora.
- Não invente fatos, números nem nomes. Se faltar um dado, deixe a caixa de fora (caixa ausente fica vazia; é melhor que inventar).
- Escreva em português do Brasil, com frases curtas e diretas.
- **Respeite o tamanho de cada caixa** (veja os modelos abaixo): texto maior que o tamanho de referência sai apertado ou cortado. Quando o texto não couber, **reescreva mais curto**, não corte no meio da frase.

## Os modelos de card

O campo `modelo` de cada card usa o código entre parênteses. O conjunto tem 6 modelos.

### Capa (`capa`)

Quando usar: abre o carrossel; é o primeiro card e aparece uma vez. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: O título chama a atenção e diz o recorte (o tema ou o período); o texto convida a deslizar.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 20 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: {normal|IA em foco:} / 01–07/09
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 141 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Novo modelo da OpenAI, agentes fora de controle, caminhantes resgatados e processos que podem mudar a IA. Bora ver o que rolou essa semana? 👇
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Índice (`indice`)

Quando usar: lista o que vem a seguir; vem logo depois da capa. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Escreva um item para cada card de conteúdo que vem depois, na mesma ordem, resumindo o assunto em poucas palavras.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 6 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: Índice
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 54 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `item_1` (Item 1 do índice; obrigatória): **até 20 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: GPT-6 Astra chegou 🚀
- `item_2` (Item 2 do índice; obrigatória): **até 30 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: Agentes da IA fora de controle
- `item_3` (Item 3 do índice; obrigatória): **até 27 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: Gemini mandou mal na trilha
- `item_4` (Item 4 do índice; obrigatória): **até 26 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: IA prevendo o clima global
- `item_5` (Item 5 do índice; obrigatória): **até 31 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: Mais jornais processam a OpenAI
- `item_6` (Item 6 do índice; obrigatória): **até 28 caracteres**, em até 1 linha; marcadores: todos, menos fino e extra.
  Exemplo: "A IA está ficando estranha"
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 54 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com imagem (`texto-com-imagem`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 6 vezes.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 31 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Agentes da IA fora / de controle
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 84 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 167 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Agentes da OpenAI invadiram um fórum wiki alemão sem autorização. A empresa confirmou o caso e admitiu: não tem processo formal para investigar esse tipo de incidente.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 84 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

Imagens (`imagem_1`): **não escreva nada sobre elas no JSON**; a pessoa escolhe as imagens depois, no programa.

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

### Passo a passo (`passo-a-passo`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Ele não está na sequência padrão, mas pode ser usado.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `passo` (Número do passo; obrigatória): **até 7 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: Passo 1
- `titulo` (Título; obrigatória): **até 22 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: Abra o Copilot
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 64 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 129 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Acesse copilot.microsoft.com e entre com sua conta Microsoft — a mesma do Outlook ou OneDrive. O plano gratuito já resolve.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 64 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com título compacto (`texto-titulo-compacto`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Ele não está na sequência padrão, mas pode ser usado.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 18 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: O que a IA NÃO faz
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 137 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Ela não acessa sua caixa de entrada, não envia nada e não conhece seu histórico com o contato. A decisão e o envio são sempre seus.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

## Quebra de linha e marcadores

Use `\n` dentro do texto para quebrar a linha (títulos costumam usar). Para destacar um trecho: `{negrito|texto}` (por nome), `{w=300|texto}` (peso de 100 a 900), `{t=85|texto}` (tamanho em % da caixa) ou, no estilo WhatsApp, `*negrito*`, `_itálico_`, `__sublinhado__` e `~~taxado~~`. Efeitos que existem: `negrito`, `normal`, `fino`, `extra`, `italico`, `sublinhado`, `taxado`, `menor`, `maior`. Cada caixa aceita só alguns (campo **marcadores** acima); o que ela não aceita só gera aviso. Use marcador com moderação.

## Avisos de tamanho

Sem aviso até 10% acima do tamanho de referência; nível 1 de 10% a 15%; nível 2 de 15% a 20%; nível 4 acima de 20% (ou quando o texto estoura o card de verdade).

## O formato da resposta

Responda com **um único objeto JSON**: o cabeçalho (`serie`, e se quiser `data`, `assunto` e `marca`) e a lista `cards`, cada card com `modelo` e `campos`. Exemplo com os dois primeiros cards do conjunto:

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

## Antes de responder, confira

- `serie` é `news` e todo `modelo` é um dos códigos acima.
- Nenhuma caixa passa do tamanho de referência.
- Nenhuma imagem foi mencionada no JSON.
- A resposta é só o JSON, sem texto em volta.
