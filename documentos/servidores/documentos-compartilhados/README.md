# Documentos compartilhados

Esta pasta é lida e gravada pelas **duas aplicações do IA Clube** e pelo **n8n**:

- a porta **8000** (gerenciador de carrosséis, repositório `iaclube_n8n`);
- a porta **7000** (gerador de imagens, repositório `iaclube_geracao_local`);
- a ponte e os fluxos do n8n deste repositório.

Os documentos ficam em [`prompts/`](prompts/): arquivos `.md` (prompts, glossários, prompts de imagem e outros), mais o `.tags.json`. **Não ponha nada além disso dentro de `prompts/`**: o que não for documento seria listado pelas telas.

**Como cada arquivo é lido** (nome, cabeçalho, tipo, categoria, links, gravação) está no contrato `docs/contratos/17-documentos-compartilhados.md` do `iaclube_n8n`. Para as aplicações usarem esta pasta, aponte `IACLUBE_DOCUMENTOS` para o caminho **absoluto** de `prompts/`.

**Uma pasta só, ligada por padrão (MVP 1.9.1, fase 0A):** os dois servidores usam esta pasta **sozinhos** quando sobem por `scripts/servidor.sh` ou pela ponte (a variável `IACLUBE_DOCUMENTOS` é definida ali). Quem sobe um servidor à mão define a variável, como acima. Sem a pasta ligada, as duas telas **avisam** em vez de mostrar só o catálogo próprio.

**Origem:** cada documento tem a chave `origem` no cabeçalho (`8000`, `7000` ou `outro`): quem **criou** o arquivo. Onde se edita não importa.

**Versionada aqui:** depois de criar ou editar documentos nas telas, **faça o commit neste repositório** (os programas nunca rodam `git`). As cópias `.bak` e os `.tmp` ficam de fora (`.gitignore`).

Situação: a pasta tem os seis arquivos que a 8000 já trazia, os dois estilos de imagem dos fluxos, os dois **guias de imagem dos agentes** (fase H do 1.9.1), os dois **prompts de reserva das imagens** (fase I do 1.9.2) e os **23 prompts de imagem do catálogo da 7000** (migrados na fase 0A, sem apagar o `prompts.json` de lá). **Tudo o que guia a geração de imagem está aqui**, categorizado e com a tag **Imagem**: na tela Prompts, filtre por essa tag e veja os 29 de uma vez (inventário em `iaclube_n8n/_plan/.report/mvp-1.9.2/fase-I_inventario-de-prompts-de-imagem.md`).

---

## Quais arquivos os fluxos do n8n usam de verdade

*(Atualizado em 2026-10-25, fase I do MVP 1.9.2.)*

**Em uma frase:** o n8n lê **seis** dos 35 arquivos: os dois **estilos** das imagens (`estilo-noticias.md` e `estilo-dicionario.md`), os dois **guias de imagem dos agentes** (`guia-de-imagem-noticias.md` e `guia-de-imagem-dicionario.md`) e os dois **prompts de reserva das imagens** (`prompt-de-reserva-noticias.md` e `prompt-de-reserva-dicionario.md`). **Você os edita na tela Prompts** (porta 8000 ou 7000) e o **próximo disparo** do fluxo já usa o texto novo, **sem abrir o n8n**. Os outros 29 existem para as telas Prompts e para você; nenhum fluxo os lê. O resto do que guia a IA (a personalidade da marca, as regras de cada conjunto) **ainda está escrito dentro dos nós** do n8n.

| Arquivo(s) | Quem usa de verdade | O que é |
|---|---|---|
| `estilo-noticias.md` | **n8n**, fluxo Notícias | o estilo que se acrescenta ao fim de **toda imagem** (paleta, traço, "sem texto") |
| `estilo-dicionario.md` | **n8n**, fluxo Dicionário | o mesmo, para o Dicionário |
| `guia-de-imagem-noticias.md` | **n8n**, fluxo Notícias | **o que a IA lê para escrever a cena de cada imagem** (a seção «A IMAGEM DE CADA NOTICIA» do agente) |
| `guia-de-imagem-dicionario.md` | **n8n**, fluxo Dicionário | o mesmo, para os dois slides com imagem (a seção «AS IMAGENS» do agente) |
| `prompt-de-reserva-noticias.md` | **n8n**, fluxo Notícias | o começo da cena de uma imagem **quando a IA não escreveu a cena** (`an editorial illustration about artificial intelligence news,` + o rótulo da notícia); sai igual ao de antes |
| `prompt-de-reserva-dicionario.md` | **n8n**, fluxo Dicionário | o mesmo, para o Dicionário (`a simple friendly editorial illustration that explains the artificial intelligence concept:` + o termo) |
| os 23 prompts de imagem (`lobo_guara_*`, `passarinho_*`, `teste_*` etc.) | **porta 7000**, campo «Tipo de imagem» | quando você gera uma imagem à mão na 7000 |
| `como-montar-cards-*.md` (4), `como-montar-arquivos.md`, `prompt-noticias.md` | **você**, pela tela Prompts da 8000 | quando você cola o guia numa IA para montar cards à mão |

### Como o n8n lê um documento

1. O nó **Configuração** do fluxo guarda o **nome** do documento de **estilo** (`estilo_documento`, sem `.md`); o nome do **guia de imagem** é fixo no fluxo (`guia-de-imagem-noticias` ou `guia-de-imagem-dicionario`).
2. Um nó **Ler …** pede o texto à **ponte** (`GET /documentos/<nome>`, só leitura, com o token da ponte). A ponte lê o arquivo **do disco naquele momento**: o que você salvou vale no **próximo disparo**.
3. **O guia de imagem e o prompt de reserva são lidos logo no começo do fluxo**, antes da IA e antes de qualquer gasto. O guia entra no prompt do agente **no mesmo lugar** onde antes estava escrito; o prompt de reserva só é usado quando a IA deixa uma imagem sem cena (nó **Montar entrada dos cards**). Com o texto como está, o prompt que o agente recebe é **byte a byte o de antes** (provado por teste).
4. **O estilo é lido depois de a IA escrever** e **antes de subir o gerador de imagens**: o nó **Montar pedidos de imagem** pega a cena de cada imagem e acrescenta o estilo no fim (**`cena, estilo`**).
5. **Se der errado**, o fluxo **para** dizendo **qual documento** faltou: arquivo que não existe, ponte fora do ar, documento **vazio** ou com **`{{` ou `}}`** (o n8n entenderia como expressão; **não escreva isso nos guias nem nos prompts de reserva**). Nada incompleto vai à IA. Nos guias, a falha acontece **antes** de existir o card no Trello (por isso é um erro do fluxo); no estilo, depois do texto pronto (por isso vira o comentário de falha do card, com o JSON para refazer a arte).

**Por que separar:** o **guia** ensina a IA a descrever bem uma cena (em inglês, simples, sem texto nem marca, sem pessoas reais); o **estilo** é igual para todas as imagens de uma edição, para elas terem a mesma cara. Os dois são o que o designer mais ajusta, e agora estão num lugar simples.

### Para os cards de Notícias IA (`completo/noticias-completo`, sexta 15h)

1. **Lê `guia-de-imagem-noticias.md` e `prompt-de-reserva-noticias.md`** pela ponte (e confere: não vazios, sem `{{ }}`). Se faltar um, o fluxo para.
2. Lê os feeds RSS, tira o que já foi publicado, a IA escolhe 4 a 6 notícias e escreve cada card **e a cena de cada imagem** (`prompt_imagem`, em inglês), seguindo o guia lido no passo 1. O resto das instruções da IA está no próprio nó **AI Agent - Noticias**.
3. Cria o card no Trello e grava a memória.
4. Monta a entrada dos cards: capa, índice (até 6 notícias), um card **com imagem** por notícia e encerramento. O estilo vem da Configuração: **`estilo-noticias`**.
5. **Lê `estilo-noticias.md`** pela ponte, sobe o gerador, gera **uma imagem por notícia** (`cena, estilo`), desliga o gerador, sobe o gerenciador (8000), monta os cards com as imagens e comenta o resultado no card do Trello.

Arquivos usados: **`guia-de-imagem-noticias.md`**, **`prompt-de-reserva-noticias.md`** e **`estilo-noticias.md`** (azul e amarelo quente, formas simples, enquadramento largo, sem texto).

> O fluxo de arte avulso `noticias-2-arte` (gatilho manual) faz só a parte das imagens a partir de um arquivo de `entradas/`: o nome do estilo vem do campo `estilo_documento` desse arquivo (`exemplo-noticias-10.json` usa `estilo-noticias`). Ele **não** tem agente de IA, então não lê guia de imagem.

### Para os cards de Dicionário IA (`completo/dicionario-completo`, segunda 15h)

1. **Lê `guia-de-imagem-dicionario.md` e `prompt-de-reserva-dicionario.md`** pela ponte (e confere), no começo.
2. A IA escolhe um termo que a página ainda não explicou e escreve os 7 slides, **dois deles com a cena de uma imagem**, seguindo o guia.
3. Cria o card no Trello e grava o termo na memória.
4. Monta os 7 cards `dict-v1`. O estilo vem da Configuração: **`estilo-dicionario`**.
5. **Lê `estilo-dicionario.md`** e continua como nas Notícias: gera **2 imagens** (`cena, estilo`) e monta os cards.

Arquivos usados: **`guia-de-imagem-dicionario.md`**, **`prompt-de-reserva-dicionario.md`** e **`estilo-dicionario.md`** (vermelho-alaranjado e azul-marinho sobre fundo off-white, formas simples, sem texto).

### Para os cards de «Mão na massa» (`completo/hands_on-completo`, quarta 15h)

**Nenhum arquivo desta pasta.** Hoje esse fluxo não gera imagens: não sobe o gerador, não pede nenhum documento à ponte e só produz os cards no gerenciador. (O catálogo **permite** card com imagem no Mão na massa, o modelo `texto-com-imagem`; é o fluxo que ainda não o usa. Está no `A-FAZER.md`, item 2.) O arquivo `como-montar-cards-hands-on.md` existe para a tela Prompts da 8000, mas **o fluxo não o lê**.

### Para as imagens geradas à mão na porta 7000

Os **23 prompts de imagem** (um por assunto e estilo, mais os testes `teste_16x16`, `teste_32x32` e `teste_64x64`) aparecem no campo «Tipo de imagem» da tela de geração da 7000. **O n8n não usa nenhum deles**: o fluxo manda ao gerador só o texto montado (`cena, estilo`), não o nome de um prompt. Os dois estilos também aparecem na 7000 (marcados `uso: sufixo`, para somar a uma cena).

### Para montar cards à mão (tela Prompts da 8000)

`como-montar-cards-news.md`, `como-montar-cards-dict-v1.md`, `como-montar-cards-dict-v2.md`, `como-montar-cards-hands-on.md`, `prompt-noticias.md` e `como-montar-arquivos.md` são **guias para você colar numa IA** (ou ler) quando monta cards sem o n8n. São textos **separados** dos que os agentes do n8n usam: mudar um deles **não muda** o que o fluxo faz.
