# workflows/: os fluxos do n8n

Aqui ficam os fluxos que produzem os carrosséis do IA Clube (**Notícias IA**, **Dicionário IA** e **Hands on**). Todos se importam no n8n em **Workflows → Import from File**.

## Como a pasta está organizada

```
workflows/
├── completo/                            fluxos que fazem tudo: texto pela IA → arte → card no Trello
│   ├── noticias-completo.workflow.json
│   ├── dicionario-completo.workflow.json
│   └── hands_on-completo.workflow.json
├── noticias-1-texto.workflow.json       só o texto das Notícias (RSS → IA → Trello)
├── noticias-2-arte.workflow.json        só a arte das Notícias, a partir de um arquivo de entradas/
├── dicionario-v1.json                   só o texto do Dicionário IA
├── hands_on-v1.json                     só o texto do Hands on
└── README.md
```

- **`completo/`** são os que você usa no dia a dia: um fluxo por conjunto de cards, do texto até a pasta de PNG.
- **Fora de `completo/`** ficam as peças soltas: o fluxo de **texto** (o que já existia antes da arte) e, só para as Notícias, o fluxo de **arte** separado. Cada `completo` foi montado a partir da peça de texto do mesmo conjunto.

| Conjunto | Só o texto | Só a arte | Completo | Dispara | Imagens geradas |
|---|---|---|---|---|---|
| Notícias IA | `noticias-1-texto` | `noticias-2-arte` | `completo/noticias-completo` | sexta 15h | uma por notícia (4 a 6) |
| Dicionário IA | `dicionario-v1` | (não há) | `completo/dicionario-completo` | segunda 15h | 2 |
| Hands on | `hands_on-v1` | (não há) | `completo/hands_on-completo` | quarta 15h | nenhuma |

Os `completo` também têm o botão **Executar agora**. Todos usam a mesma **ponte** (`scripts/ponte.py`) e sobem/desligam os mesmos servidores: rode **um fluxo de cada vez** (os horários agendados já caem em dias diferentes). A memória de cada conjunto é uma Data Table própria: `noticias_ia`, `dicionario_ia` e `tarefas_ia`.

## O que cada fluxo faz

**Notícias**
1. **`noticias-1-texto`**: lê os feeds RSS, tira o que já foi publicado, a IA escolhe e escreve as notícias, cria o card no Trello e grava a memória.
2. **`noticias-2-arte`**: parte de um arquivo de `entradas/` (cards + prompts de imagem), gera as imagens no `iaclube_geracao_local` e monta os cards no `iaclube_n8n`. Gatilho manual.
3. **`completo/noticias-completo`**: o texto do `noticias-1-texto` (com a IA escrevendo também o prompt de cada imagem) + a arte do `noticias-2-arte`. Cards: capa, índice (até 6 notícias), um por notícia (com imagem), encerramento.

**Dicionário**
4. **`dicionario-v1`**: a IA escolhe um termo que a página ainda não explicou, escreve os slides, cria o card no Trello e grava o termo na memória.
5. **`completo/dicionario-completo`**: o `dicionario-v1` + a arte. Os 7 slides viram os 7 cards `dict-v1`: capa, definição, 2 com imagem, texto, texto com início fino, encerramento.

**Hands on**
6. **`hands_on-v1`**: a IA (com busca na web) escolhe uma tarefa chata do dia a dia, escreve o passo a passo, cria o card no Trello e grava a tarefa na memória.
7. **`completo/hands_on-completo`**: o `hands_on-v1` + a arte. Gancho → `capa`; contexto → `texto-titulo-grande`; cada passo → `passo-a-passo` (numerado sozinho: "Passo 1", "Passo 2"…); os **dois últimos** slides de desenvolvimento (o cuidado e o resultado) → `texto-titulo-compacto`; CTA → `encerramento`. **Não tem imagens**, então não usa o gerador de imagens: só sobe o gerenciador, produz os cards e o desliga.

### Como um `completo` junta as duas partes

**Parte 1 (texto)** é o fluxo de texto do conjunto, com o prompt da IA ajustado aos limites de caracteres dos cards do gerenciador (bem menores que os dos fluxos de texto) e, nos conjuntos com imagem, com um `prompt_imagem` por slide. Um nó **Montar …** (`Montar entrada dos cards`, ou `Montar pedido de produção` no Hands on) transforma os slides nos cards do conjunto. **Parte 2 (arte)** gera as imagens (se houver), pede os cards ao gerenciador e comenta no card do Trello a pasta com o resultado. Se a arte falhar, o texto **já está no Trello** e o comentário de falha traz o JSON para refazer: nas Notícias e no Dicionário, para rodar só a arte (`noticias-2-arte`); no Hands on, para colar na tela do gerenciador (ou rodar o fluxo de novo).

No nó **Configuração** de cada `completo`: o endereço e o token da ponte, a `serie`, o `tipo` (nome da pasta de saída), a `marca` e, quando há imagens, o `estilo_documento` (o nome de um documento da pasta compartilhada, lido pela ponte: o **texto** do estilo não está mais no fluxo) e o tamanho delas. Notícias também tem `noticias_min`/`noticias_max` (padrão 4 a 6; com mais de 6 o Índice sai, porque o modelo tem 6 itens).

## Ordem de inserção

Catálogo de **quando** cada fluxo entrou nesta pasta e **quem** o criou. Datas e horários em 2026 (fuso -03:00), tirados da data dos arquivos no disco e do histórico do git. O que não dá para saber com certeza está marcado.

> O número no nome do arquivo (`1-texto`, `2-arte`) é a **ordem do pipeline** (primeiro o texto, depois a arte), não a ordem em que os arquivos foram criados. A ordem de criação é a da tabela abaixo.

| # | Arquivo hoje | Nome original | Quem criou | Entrou na pasta | Commit |
|---|---|---|---|---|---|
| 1 | `noticias-2-arte.workflow.json` | `noticias-10-cards.workflow.json` | **Claude** | 19/10, ~12:19 (nota 1) | `1866c5d` (12:35) |
| 2 | `noticias-1-texto.workflow.json` | `texto-de-noticias.json` | **Você** | 19/10, ~13:52 | `648d4ce` (17:55) |
| 3 | `completo/noticias-completo.workflow.json` | `noticias-completo.workflow.json` | **Claude** | 19/10, ~17:49 | `648d4ce` (17:55) |
| 4 | `dicionario-v1.json` | (nasceu com este nome) | **Você** | 20/10, ~13:57 | `dee8e95` |
| 5 | `completo/dicionario-completo.workflow.json` | `dicionario-completo.workflow.json` | **Claude** | 20/10, ~14:11 | `dee8e95` |
| 6 | `hands_on-v1.json` | (nasceu com este nome) | **Você** | 20/10, ~15:09 | ainda não commitado |
| 7 | `completo/hands_on-completo.workflow.json` | (nasceu com este nome) | **Claude** | 20/10, ~15:13 | ainda não commitado |

A pasta `completo/` foi criada em 20/10 às ~15:09; os fluxos 3 e 5 estavam em `workflows/` e foram movidos para lá (nota 4).

## O `.json` de instruções (para corrigir um card depois)

Os fluxos de arte (`noticias-2-arte` e os três `completo`) pedem ao gerenciador `exportacao.instrucoes: true`. Com isso, na pasta dos PNG (`~/Imagens/iaclube_n8n/<tipo>/<data_hora>/`) fica também o `<data>_<conjunto>_<assunto>_instrucoes.json`: o **mesmo arquivo** que a tela do gerenciador gera ao exportar. Para corrigir um detalhe de formatação, abra a tela do gerenciador e use **Abrir a partir de instruções** com esse arquivo; ajuste e exporte de novo.

O caminho do arquivo aparece no comentário que o fluxo deixa no card do Trello (os três `completo`) e na saída do último nó (`instrucoes`). O `.json` **não** entra na lista `arquivos` (que só tem as imagens). A pasta de saída de cada conjunto é o `tipo` da Configuração: `noticias`, `dicionario` e `hands-on`.

**Exige o gerenciador atualizado.** A opção `exportacao.instrucoes` foi acrescentada ao `iaclube_n8n` em 20/10/2026 (antes a API não a aceitava: o pedido dava `422 pedido_invalido`). Se o gerenciador estiver de pé desde antes disso, reinicie-o; os fluxos o sobem e o desligam a cada execução, então basta rodar de novo.

## O que o designer edita sem abrir o n8n: o estilo, o guia de imagem e o prompt de reserva (MVP 1.9, 1.9.1 e 1.9.2)

Dois tipos de documento da pasta compartilhada com as portas 8000 e 7000 (`documentos/servidores/documentos-compartilhados/prompts/`) guiam a geração de imagem, e **os dois se editam na tela Prompts**; o disparo seguinte do fluxo já usa o texto novo, **sem abrir o n8n e sem reimportar nada**:

| Documento | Fluxo | O que é |
|---|---|---|
| `guia-de-imagem-noticias.md` | Notícias (`completo/noticias-completo`) | o que a **IA lê para escrever a cena** de cada imagem (`prompt_imagem`): em inglês, cena simples, sem texto nem marca, sem pessoas reais |
| `guia-de-imagem-dicionario.md` | Dicionário (`completo/dicionario-completo`) | o mesmo, para os dois slides com imagem |
| `prompt-de-reserva-noticias.md` | Notícias | o começo da cena de uma imagem **quando a IA não escreveu a cena** (`prompt_imagem` vazio); o rótulo da notícia vem depois |
| `prompt-de-reserva-dicionario.md` | Dicionário | o mesmo, para o Dicionário (o termo vem depois) |
| `estilo-noticias.md` | Notícias (e a arte avulsa) | o **estilo** acrescentado ao fim de toda imagem (paleta, traço, "sem texto") |
| `estilo-dicionario.md` | Dicionário | o mesmo, para o Dicionário |

- **O guia é lido no começo do fluxo.** O nó **Ler guia de imagem** busca o documento pela ponte (`GET /documentos/<nome>`, só leitura, com o mesmo token); o **Validar guia de imagem** confere que ele **não está vazio** e **não tem `{{` nem `}}`** (o n8n entenderia como expressão); e o prompt do agente traz, no lugar onde a seção estava escrita, `{{ $('Ler guia de imagem').first().json.corpo.trim() }}`. Com o texto como está, o prompt do agente é **idêntico byte a byte** ao de antes. **Se algo falhar** (ponte fora do ar, arquivo ausente, vazio, com `{{ }}`), o fluxo **para antes de gastar a IA** e diz **qual documento** (nó **Guia de imagem não lido** ou o erro do **Validar guia de imagem**).
- **O prompt de reserva (1.9.2)** é lido logo depois do guia, pelo nó **Ler prompt de reserva** (conferido pelo **Validar prompt de reserva**, com a mesma falha clara: o nó **Prompt de reserva não lido** diz qual documento). O nó **Montar entrada dos cards** o usa **só** quando uma imagem fica sem cena da IA: antes o texto estava escrito dentro do nó; o prompt final é **idêntico byte a byte** ao de antes (provado por teste).
- **O estilo** continua sendo lido pelo nó **Ler estilo**, depois do texto pronto: o **Montar pedidos de imagem** acrescenta o estilo no fim da cena (`cena, estilo`); o prompt final continua idêntico ao de antes.
- **O fluxo Hands on não tem imagens**: não usa nenhum desses documentos.
- **Onde editar:** abra `/prompts` na porta 8000 (ou 7000), procure `guia-de-imagem-…`, `prompt-de-reserva-…` ou `estilo-…` (tag **n8n**; ou filtre pela tag **Imagem** para ver tudo o que guia imagem), edite e salve. Faça o **commit** neste repositório depois (os programas nunca rodam `git`).

## Endereços do gerenciador (MVP 1.9.1)

A API do gerenciador (porta 8000) mora em **`/api/v1/`**. Os fluxos chamam, pela ponte, `/gerenciador/api/v1/saude` e `/gerenciador/api/v1/integracao/producao`. A ponte **aceita só** os endereços `/api/v1/{saude,integracao/{producao,validar,conjuntos,prompt}}` do gerenciador e **traduz os antigos** (`/gerenciador/saude`, `/gerenciador/integracao/…`) para os novos, então um fluxo que você ainda não reimportou **continua funcionando**; o gerenciador não aceita mais os antigos na raiz (`/saude` fica, só para o Docker).
