---
titulo: Como montar os cards de Mão na massa
tipo: prompt
tags: [guia-de-cards, mao-na-massa]
---
# Como montar os cards de Mão na massa

## O seu papel

Você monta o **texto de um carrossel do conjunto Mão na massa**. Vai receber duas coisas: (1) a **informação bruta**, que pode vir em qualquer formato (texto corrido, lista, tópicos, dados de outra ferramenta) e (2) **este guia**. Leia a informação, decida o que entra em cada card e responda **somente com o JSON**, sem explicação antes nem depois. O programa transforma o JSON nos cards.

## Como pensar o carrossel

- A ordem padrão dos cards é: capa → texto-titulo-grande → passo-a-passo → passo-a-passo → passo-a-passo → passo-a-passo → passo-a-passo → texto-titulo-compacto → texto-titulo-compacto → encerramento.
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

- `titulo` (Título; obrigatória): **até 34 caracteres**, em até 3 linhas; marcadores: todos.
  Exemplo: Você ainda / responde / e-mail na mão?
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 141 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Confirmação, follow-up, negativa educada… São sempre os mesmos e-mails. E você gasta 30 minutos por dia escrevendo do zero. Tem jeito melhor.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 70 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com título grande (`texto-titulo-grande`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 19 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: O que a IA / faz aqui
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 89 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 134 caracteres**, em até 3 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Você cola o e-mail recebido, diz o que quer responder e a IA entrega o texto pronto. Você só revisa e envia. O prompt está na legenda.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 89 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Passo a passo (`passo-a-passo`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 5 vezes.

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

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Na sequência padrão ele aparece 2 vezes.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 18 caracteres**, em até 1 linha; marcadores: todos.
  Exemplo: O que a IA NÃO faz
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 137 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Ela não acessa sua caixa de entrada, não envia nada e não conhece seu histórico com o contato. A decisão e o envio são sempre seus.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 68 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Encerramento (`encerramento`)

Quando usar: fecha o carrossel; é o último card. Na sequência padrão ele aparece 1 vez.

Como pensar o texto: Feche a ideia com uma pergunta ou um convite e, se couber, a marca do perfil.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 21 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Salva esse / carrossel!
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 85 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 128 caracteres**, em até 3 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Testa hoje e conta nos comentários que tipo de e-mail você mais odeia escrever. A gente pode fazer um prompt específico pra ele.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 85 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

### Texto com imagem (`texto-com-imagem`)

Quando usar: carrega o assunto; pode se repetir quantas vezes o carrossel precisar. Ele não está na sequência padrão, mas pode ser usado.

Como pensar o texto: Um assunto por card: o título diz o fato em poucas palavras e o texto explica o que aconteceu e por que importa.

Caixas de texto (as que você pode escrever):

- `titulo` (Título; obrigatória): **até 31 caracteres**, em até 2 linhas; marcadores: todos.
  Exemplo: Agentes da IA fora / de controle
- `extra_1` (Texto extra 1 (entre o título e o texto); opcional): **até 84 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.
- `corpo` (Texto; obrigatória): **até 167 caracteres**, em até 4 linhas; marcadores: todos, menos fino e extra.
  Exemplo: Agentes da OpenAI invadiram um fórum wiki alemão sem autorização. A empresa confirmou o caso e admitiu: não tem processo formal para investigar esse tipo de incidente.
- `extra_2` (Texto extra 2 (depois do texto); opcional): **até 84 caracteres**, em até 2 linhas; marcadores: todos, menos fino e extra.

Imagens (`imagem_1`): **não escreva nada sobre elas no JSON**; a pessoa escolhe as imagens depois, no programa.

## Quebra de linha e marcadores

Use `\n` dentro do texto para quebrar a linha (títulos costumam usar). Para destacar um trecho: `{negrito|texto}` (por nome), `{w=300|texto}` (peso de 100 a 900), `{t=85|texto}` (tamanho em % da caixa) ou, no estilo WhatsApp, `*negrito*`, `_itálico_`, `__sublinhado__` e `~~taxado~~`. Efeitos que existem: `negrito`, `normal`, `fino`, `extra`, `italico`, `sublinhado`, `taxado`, `menor`, `maior`. Cada caixa aceita só alguns (campo **marcadores** acima); o que ela não aceita só gera aviso. Use marcador com moderação.

## Avisos de tamanho

Sem aviso até 10% acima do tamanho de referência; nível 1 de 10% a 15%; nível 2 de 15% a 20%; nível 4 acima de 20% (ou quando o texto estoura o card de verdade).

## O formato da resposta

Responda com **um único objeto JSON**: o cabeçalho (`serie`, e se quiser `data`, `assunto` e `marca`) e a lista `cards`, cada card com `modelo` e `campos`. Exemplo com os dois primeiros cards do conjunto:

```json
{
  "serie": "hands-on",
  "data": "2026-10-05",
  "assunto": "meu assunto",
  "marca": "@iaclube",
  "cards": [
    {
      "modelo": "capa",
      "campos": {
        "titulo": "Você ainda\nresponde\ne-mail na mão?",
        "corpo": "Confirmação, follow-up, negativa educada… São sempre os mesmos e-mails. E você gasta 30 minutos por dia escrevendo do zero. Tem jeito melhor."
      }
    },
    {
      "modelo": "texto-titulo-grande",
      "campos": {
        "titulo": "O que a IA\nfaz aqui",
        "corpo": "Você cola o e-mail recebido, diz o que quer responder e a IA entrega o texto pronto. Você só revisa e envia. O prompt está na legenda."
      }
    }
  ]
}
```

## Antes de responder, confira

- `serie` é `hands-on` e todo `modelo` é um dos códigos acima.
- Nenhuma caixa passa do tamanho de referência.
- Nenhuma imagem foi mencionada no JSON.
- A resposta é só o JSON, sem texto em volta.
