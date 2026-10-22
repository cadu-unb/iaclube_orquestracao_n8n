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

Situação: a pasta tem os seis arquivos que a 8000 já trazia, os dois estilos de imagem dos fluxos e os **23 prompts de imagem do catálogo da 7000** (migrados na fase 0A, sem apagar o `prompts.json` de lá).

---

## Quais arquivos os fluxos do n8n usam de verdade

*(Conferido nos fluxos de `workflows/` e na ponte em 2026-10-22, antes da fase H do MVP 1.9.1.)*

**Em uma frase:** hoje o n8n lê **só dois** dos 31 arquivos, `estilo-noticias.md` e `estilo-dicionario.md`. Os outros 29 existem para as telas **Prompts** (portas 8000 e 7000) e para você; nenhum fluxo os lê. O resto do que guia a IA nos fluxos (a personalidade da marca, as regras de cada conjunto e o guia da imagem de cada agente) **ainda está escrito dentro dos nós do n8n**: isso muda na fase H (veja o fim desta página).

| Arquivo(s) | Quem usa de verdade | Quando |
|---|---|---|
| `estilo-noticias.md` | **n8n**, fluxo Notícias | toda execução com imagens |
| `estilo-dicionario.md` | **n8n**, fluxo Dicionário | toda execução com imagens |
| os 23 prompts de imagem (`lobo_guara_*`, `passarinho_*`, `teste_*` etc.) | **porta 7000**, campo «Tipo de imagem» | quando você gera uma imagem à mão na 7000 |
| `como-montar-cards-*.md` (4), `como-montar-arquivos.md`, `prompt-noticias.md` | **você**, pela tela Prompts da 8000 | quando você cola o guia numa IA para montar cards à mão |

### Como o n8n lê um documento (vale para os dois estilos)

1. O nó **Configuração** do fluxo guarda o **nome** do documento (`estilo_documento`, sem `.md`). É o único lugar para trocar de estilo.
2. O nó **Validar entrada** confere o nome (letras, números, hífen e sublinhado, até 64).
3. O nó **Ler estilo** pede o texto à **ponte** (`GET /documentos/<nome>`, só leitura, com o token da ponte). A ponte lê o arquivo **do disco naquele momento**: o que você salvou na tela Prompts vale na **próxima execução**, sem abrir o n8n e sem reimportar nada.
4. Só **depois** de o estilo ser lido é que o fluxo sobe o gerador de imagens (a 7000). O nó **Montar pedidos de imagem** pega a cena de cada imagem, escrita pela IA do fluxo (`prompt_imagem`), e acrescenta o estilo no fim: **`cena, estilo`**. O pedido vai ao gerador já com esse texto inteiro.
5. **Se der errado**, o fluxo para antes de gastar tempo com imagens: arquivo que não existe, ponte fora do ar ou documento vazio viram o comentário de falha no card do Trello, com o nome do arquivo e o motivo. Nada de imagem fora do estilo sai por engano.

**Por que um estilo à parte:** é ele que deixa as imagens de uma mesma edição com a **mesma cara** (paleta, traço, enquadramento, «sem texto, sem logos»). A cena muda a cada notícia; o estilo é igual para todas. Separar os dois permite o designer ajustar o estilo numa tela simples.

### Para os cards de Notícias IA (`completo/noticias-completo`, sexta 15h)

Ordem dentro do fluxo:

1. Lê os feeds RSS, tira o que já foi publicado, a IA escolhe 4 a 6 notícias e escreve cada card **e a cena de cada imagem** (`prompt_imagem`, em inglês). *Nenhum documento é lido nesta etapa:* as instruções da IA estão no próprio nó **AI Agent - Noticias**.
2. Cria o card no Trello e grava a memória.
3. Monta a entrada dos cards: capa, índice (até 6 notícias), um card **com imagem** por notícia e encerramento. O nome do documento de estilo vem da Configuração: **`estilo-noticias`**.
4. **Lê `estilo-noticias.md`** pela ponte (passos 1 a 5 acima).
5. Sobe o gerador, gera **uma imagem por notícia** (`cena, estilo`), desliga o gerador, sobe o gerenciador (8000), monta os cards com as imagens e comenta o resultado no card do Trello.

Arquivo usado: **`estilo-noticias.md`** (azul e amarelo quente, formas simples, enquadramento largo, sem texto).

> O fluxo de arte avulso `noticias-2-arte` (gatilho manual) faz o mesmo a partir de um arquivo de `entradas/`. O nome do estilo vem do campo `estilo_documento` desse arquivo (`exemplo-noticias-10.json` usa `estilo-noticias`). Se o campo não existir, o fluxo usa o `estilo_comum` escrito no próprio arquivo, como antes do MVP 1.9.

### Para os cards de Dicionário IA (`completo/dicionario-completo`, segunda 15h)

1. A IA escolhe um termo que a página ainda não explicou e escreve os 7 slides, **dois deles com a cena de uma imagem**. *Nenhum documento é lido nesta etapa* (as instruções estão no nó **AI Agent - Dicionario**).
2. Cria o card no Trello e grava o termo na memória.
3. Monta os 7 cards `dict-v1`. O estilo vem da Configuração: **`estilo-dicionario`**.
4. **Lê `estilo-dicionario.md`** pela ponte e continua como nas Notícias: gera **2 imagens** (`cena, estilo`) e monta os cards.

Arquivo usado: **`estilo-dicionario.md`** (vermelho-alaranjado e azul-marinho sobre fundo off-white, formas simples, sem texto).

### Para os cards de «Mão na massa» (`completo/hands_on-completo`, quarta 15h)

**Nenhum arquivo desta pasta.** Hoje esse fluxo não gera imagens: não sobe o gerador, não pede nenhum documento à ponte e só produz os cards no gerenciador. (O catálogo **permite** card com imagem no Mão na massa, o modelo `texto-com-imagem`; é o fluxo que ainda não o usa. Está no `A-FAZER.md`, item 2.) O texto é escrito pela IA com as instruções que estão dentro do nó **AI Agent - Mao na Massa**.

O arquivo `como-montar-cards-hands-on.md` existe para a tela Prompts da 8000, mas **o fluxo não o lê**.

### Para as imagens geradas à mão na porta 7000

Os **23 prompts de imagem** (um por assunto e estilo, mais os testes `teste_16x16`, `teste_32x32` e `teste_64x64`) aparecem no campo «Tipo de imagem» da tela de geração da 7000. **O n8n não usa nenhum deles**: o fluxo manda ao gerador só o texto montado (`cena, estilo`), não o nome de um prompt. Os dois estilos também aparecem na 7000 (marcados `uso: sufixo`, para somar a uma cena).

### Para montar cards à mão (tela Prompts da 8000)

`como-montar-cards-news.md`, `como-montar-cards-dict-v1.md`, `como-montar-cards-dict-v2.md`, `como-montar-cards-hands-on.md`, `prompt-noticias.md` e `como-montar-arquivos.md` são **guias para você colar numa IA** (ou ler) quando monta cards sem o n8n. São textos **separados** dos que os agentes do n8n usam: mudar um deles **não muda** o que o fluxo faz.

### O que ainda mora dentro do n8n (e muda na fase H)

Os agentes dos três fluxos têm todo o seu prompt escrito dentro do nó, **inclusive a parte que ensina a IA a escrever a cena de cada imagem** («A IMAGEM DE CADA NOTICIA» nas Notícias e «AS IMAGENS» no Dicionário). Hoje, para o designer mudar esse guia, é preciso abrir o n8n. A **fase H** do MVP 1.9.1 do `iaclube_n8n` move esse trecho para dois documentos desta pasta (`guia-de-imagem-noticias.md` e `guia-de-imagem-dicionario.md`) lidos pela ponte do mesmo jeito que os estilos; quando isso acontecer, esta página será atualizada. Detalhes em `A-FAZER.md`, item 2b.
