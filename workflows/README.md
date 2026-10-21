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

## O estilo das imagens: um documento (MVP 1.9)

O texto que se acrescenta ao fim de todo prompt de imagem (o `estilo_comum` de antes) agora é um **documento** da pasta de documentos compartilhada com as portas 8000 e 7000: `estilo-noticias.md` e `estilo-dicionario.md`, em `documentos/servidores/documentos-compartilhados/prompts/`. Nos três fluxos de arte, o nó **Ler estilo** busca o texto pela ponte (`GET /documentos/<nome>`, só leitura, com o mesmo token) e o **Montar pedidos de imagem** o usa; o prompt final continua `cena, estilo`, **idêntico** ao de antes.

- **Configuração** (`noticias-completo` e `dicionario-completo`): `estilo_documento: 'estilo-noticias'` (ou `'estilo-dicionario'`). Para trocar o estilo, troque o **texto do documento** (pela tela Prompts ou no arquivo), não o fluxo.
- **`noticias-2-arte`:** o arquivo de `entradas/` traz `estilo_documento` no lugar de `estilo_comum`. Um arquivo antigo, com `estilo_comum` (o texto), continua valendo; os dois juntos dão erro de validação.
- **Se a ponte não conseguir ler o documento** (ponte desligada, documento inexistente, nome errado, pasta ausente), o fluxo **para antes de subir o gerador**, com uma mensagem que diz qual documento (`Não foi possível ler o documento de estilo «…»`). Não existe texto de reserva escondido.
- A ponte aponta para a pasta compartilhada por padrão; outra pasta: `python3 scripts/ponte.py --pasta-documentos /caminho`. Reinicie a ponte depois de atualizar o `ponte.py`.

## Onde fica o token da ponte

Os fluxos que geram arte (`noticias-2-arte` e os três `completo`) falam com a ponte e mandam o token em todo pedido. Ele está **num lugar só por fluxo**: o nó **Configuração**, na **linha 7** do código dele:

```js
  token_ponte: 'COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA',
```

**Para trocar, no n8n (jeito normal):** abra o fluxo → clique duas vezes no nó **Configuração** → na linha 7, troque só o texto entre as aspas simples → salve. Faça isso em cada fluxo de arte que você usa.

**Se preferir editar o arquivo `.json`:** o código do nó é uma string de uma linha só, então o token não está numa linha própria. Procure por `token_ponte:` (ou vá à linha do `"jsCode"` do nó Configuração: 49 no `noticias-2-arte`, 89 no `noticias-completo` e no `dicionario-completo`, 88 no `hands_on-completo`). Depois importe o arquivo de novo no n8n.

**De onde vem o token:** a ponte mostra o token ao subir (`Token (cabeçalho X-Ponte-Token): ...`) e o guarda em `~/.config/iaclube-orquestracao/ponte.token`. Ele só muda se esse arquivo for apagado ou se a ponte subir com `--token` ou com a variável `IACLUBE_PONTE_TOKEN`. Se o fluxo falhar com `401` / `nao_autorizado`, o token do nó não confere com o da ponte.

**Cuidado com o repositório:** trocar o token no n8n **não** altera os arquivos desta pasta. Se você exportar o fluxo de novo do n8n para cá, o token novo vai junto para o arquivo; tire-o (volte ao texto `COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`) antes de commitar ou publicar.

## A marca dos cards

O texto do cabeçalho dos cards vem de `marca` no nó **Configuração** (os três `completo`) ou de `entrada.marca` no arquivo de `entradas/` (`noticias-2-arte`). O padrão é `@iaclube.help` (antes `@iaclube`). Exige o gerenciador que aceita essa marca (acrescentada ao `iaclube_n8n` em 20/10/2026); com um gerenciador mais antigo o pedido dá `422 entrada_invalida`. Os textos dos encerramentos ("…toda semana no @iaclube…") não mudaram.

## Notas

1. **`noticias-2-arte` (antes `noticias-10-cards`).** Foi montado por Claude na sessão de **18/10/2026**, no outro usuário do computador (`yuri-santos`), conforme o [RELATORIO.md](../RELATORIO.md). A hora exata em que foi criado lá **não dá para saber**. O que existe é a hora em que chegou a esta pasta: todos os arquivos do repositório (este fluxo, `entradas/`, `scripts/`) têm o mesmo instante, 12:19:11, então vieram juntos numa cópia. O primeiro commit (`begin`, 12:35) é só a foto desse estado inicial.
2. **`noticias-1-texto` (antes `texto-de-noticias.json`)**, **`dicionario-v1`** e **`hands_on-v1`** são exportações do **seu** n8n: o `instanceId`, as credenciais (Anthropic, OpenAI, Trello; no Hands on também a busca na web, `Header Auth account`) e as Data Tables são do seu ambiente. Claude **não escreveu** esses fluxos. No `noticias-1-texto`, em 19/10 às ~17:53, só **renomeou** o arquivo e **acrescentou o campo `name`** (o export não trazia nome). O `dicionario-v1` foi alterado às ~14:05 e o `hands_on-v1` às ~15:10, depois de entrarem na pasta; não sei por quem nem o quê, e Claude não mexeu neles.
3. **Os três `completo` foram criados por Claude** a partir da peça de texto do conjunto (a sua) e dos nós de arte do primeiro `completo`: `noticias-completo` em 19/10 (~17:49), `dicionario-completo` em 20/10 (~14:11) e `hands_on-completo` em 20/10 (~15:13). Em cada um, o que mudou no prompt da IA foram os limites de caracteres (agora os dos cards do gerenciador, bem menores), o `prompt_imagem` (onde há imagem) e, no Hands on, a função dos dois últimos slides de desenvolvimento; o resto do texto do prompt é o seu. Os nós de código foram testados numa simulação com dados de mentira, e os pedidos gerados foram produzidos de verdade num gerenciador local (cards desenhados no Chromium, sem avisos). **Nenhum foi importado nem rodado no n8n de verdade.**
4. **A pasta `completo/`** foi criada por você em 20/10 (~15:09): os arquivos `noticias-completo` e `dicionario-completo` foram movidos de `workflows/` para ela (o conteúdo não mudou). Claude criou o `hands_on-completo` já dentro dela.
5. **Autor do commit.** O git mostra `cadu-unb_linux` em todos os commits porque foi a conta que commitou; não indica quem escreveu cada fluxo.
6. **Tokens no histórico.** `noticias-2-arte` e `noticias-completo` trazem o token da ponte escrito no nó **Configuração** (já no histórico do git); tire-o antes de publicar o repositório. `dicionario-completo` e `hands_on-completo` vêm com o token em branco (`COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`) e ele precisa ser colado ao importar.
