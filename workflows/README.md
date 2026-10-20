# workflows/: ordem de inserção dos fluxos

Catálogo de **quando** cada fluxo entrou nesta pasta e **quem** o criou. Datas e horários em 2026 (fuso -03:00), tirados da data dos arquivos no disco e do histórico do git. O que não dá para saber com certeza está marcado.

> O número no nome do arquivo (`1-texto`, `2-arte`) é a **ordem do pipeline** (primeiro o texto, depois a arte), não a ordem em que os arquivos foram criados. A ordem de criação é a da tabela abaixo.

## Ordem de inserção

| # | Arquivo hoje | Nome original | Quem criou | Entrou na pasta | Commit |
|---|---|---|---|---|---|
| 1 | `noticias-2-arte.workflow.json` | `noticias-10-cards.workflow.json` | **Claude** | 19/10, ~12:19 (veja a nota 1) | `1866c5d` (12:35) |
| 2 | `noticias-1-texto.workflow.json` | `texto-de-noticias.json` | **Você** | 19/10, ~13:52 | `648d4ce` (17:55) |
| 3 | `noticias-completo.workflow.json` | (nasceu com este nome) | **Claude** | 19/10, ~17:49 | `648d4ce` (17:55) |
| 4 | `dicionario-v1.json` | (nasceu com este nome) | **Você** | 20/10, ~13:57 | ainda não commitado |
| 5 | `dicionario-completo.workflow.json` | (nasceu com este nome) | **Claude** | 20/10, ~14:11 | ainda não commitado |

## O que cada um faz

1. **`noticias-2-arte`**: parte de um arquivo de `entradas/` (cards + prompts de imagem), gera as imagens no `iaclube_geracao_local` e monta os cards no `iaclube_n8n`. Gatilho manual.
2. **`noticias-1-texto`**: o fluxo de texto que você já tinha: lê os feeds RSS, tira o que já foi publicado (Data Table `noticias_ia`), a IA escolhe e escreve as notícias, cria o card no Trello e grava a memória. Dispara toda sexta às 15h.
3. **`noticias-completo`**: junta os dois. Faz o texto como o `noticias-1-texto` (com a IA escrevendo também o prompt de cada imagem) e entrega a arte como o `noticias-2-arte`.
4. **`dicionario-v1`**: o fluxo de texto do Dicionário IA que você já tinha: a IA escolhe um termo que a página ainda não explicou, escreve os slides, cria o card no Trello e grava o termo na memória (Data Table `dicionario_ia`). Dispara toda segunda às 15h. Sem arte.
5. **`dicionario-completo`**: o `dicionario-v1` + a arte, como o `noticias-completo` faz com as notícias. Os 7 slides viram os 7 cards do conjunto `dict-v1` (capa, definição, 2 com imagem, texto, texto com início fino, encerramento), com **2 imagens** geradas. As imagens saem em `iaclube_n8n/dicionario/`.

## O `.json` de instruções (para corrigir um card depois)

Os três fluxos de arte (`noticias-2-arte`, `noticias-completo`, `dicionario-completo`) pedem ao gerenciador `exportacao.instrucoes: true`. Com isso, na pasta dos PNG (`~/Imagens/iaclube_n8n/<tipo>/<data_hora>/`) fica também o `<data>_<conjunto>_<assunto>_instrucoes.json`: o **mesmo arquivo** que a tela do gerenciador gera ao exportar. Para corrigir um detalhe de formatação, abra a tela do gerenciador e use **Abrir a partir de instruções** com esse arquivo; ajuste e exporte de novo.

O caminho do arquivo aparece no comentário que o fluxo deixa no card do Trello (`noticias-completo`, `dicionario-completo`) e na saída do último nó (`instrucoes`). O `.json` **não** entra na lista `arquivos` (que só tem as imagens).

**Exige o gerenciador atualizado.** A opção `exportacao.instrucoes` foi acrescentada ao `iaclube_n8n` em 20/10/2026 (antes a API não a aceitava: o pedido dava `422 pedido_invalido`). Se o gerenciador estiver de pé desde antes disso, reinicie-o; os fluxos o sobem e o desligam a cada execução, então basta rodar de novo.

## Onde fica o token da ponte

Os fluxos que geram arte (`noticias-2-arte`, `noticias-completo`, `dicionario-completo`) falam com a ponte (`scripts/ponte.py`) e mandam o token em todo pedido. Ele está **num lugar só por fluxo**: o nó **Configuração**, na **linha 7** do código dele:

```js
  token_ponte: 'COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA',
```

**Para trocar, no n8n (jeito normal):** abra o fluxo → clique duas vezes no nó **Configuração** → na linha 7, troque só o texto entre as aspas simples → salve. Faça isso em cada fluxo de arte que você usa.

**Se preferir editar o arquivo `.json`:** o código do nó é uma string de uma linha só, então o token não está numa linha própria. Procure por `token_ponte:` (ou vá à linha do `"jsCode"` do nó Configuração: 49 no `noticias-2-arte`, 89 no `noticias-completo` e no `dicionario-completo`). Depois importe o arquivo de novo no n8n.

**De onde vem o token:** a ponte mostra o token ao subir (`Token (cabeçalho X-Ponte-Token): ...`) e o guarda em `~/.config/iaclube-orquestracao/ponte.token`. Ele só muda se esse arquivo for apagado ou se a ponte subir com `--token` ou com a variável `IACLUBE_PONTE_TOKEN`. Se o fluxo falhar com `401` / `nao_autorizado`, o token do nó não confere com o da ponte.

**Cuidado com o repositório:** trocar o token no n8n **não** altera os arquivos desta pasta. Se você exportar o fluxo de novo do n8n para cá, o token novo vai junto para o arquivo; tire-o (volte ao texto `COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`) antes de commitar ou publicar.

## Notas

1. **`noticias-2-arte` (antes `noticias-10-cards`).** Foi montado por Claude na sessão de **18/10/2026**, no outro usuário do computador (`yuri-santos`), conforme o [RELATORIO.md](../RELATORIO.md). A hora exata em que foi criado lá **não dá para saber**. O que existe é a hora em que chegou a esta pasta: todos os arquivos do repositório (este fluxo, `entradas/`, `scripts/`) têm o mesmo instante, 12:19:11, então vieram juntos numa cópia. O primeiro commit (`begin`, 12:35) é só a foto desse estado inicial.
2. **`noticias-1-texto` (antes `texto-de-noticias.json`).** É uma exportação do **seu** n8n: o `instanceId`, as credenciais (Anthropic, OpenAI, Trello) e a Data Table são do seu ambiente. Estava na pasta, fora do git, quando a sessão de hoje começou. Claude **não escreveu o fluxo**; em 19/10 às ~17:53 só **renomeou** o arquivo e **acrescentou o campo `name`** (o export não trazia nome). O conteúdo dos nós está como veio.
3. **`noticias-completo`.** Criado por Claude em 19/10 às ~17:49, a partir dos dois fluxos acima, e ajustado até ~17:53. Os nós de código foram testados numa simulação com dados de mentira, e o pedido gerado passou no validador do gerenciador. **Ainda não foi importado nem rodado no n8n de verdade.**
4. **Autor do commit.** O git mostra `cadu-unb_linux` nos dois commits porque foi a conta que commitou; não indica quem escreveu cada fluxo.
5. `noticias-2-arte` e `noticias-completo` trazem o token da ponte escrito no nó **Configuração**; tire-o antes de publicar o repositório. O `dicionario-completo` **não**: o token veio em branco (`COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`) e precisa ser colado ao importar.
6. **`dicionario-v1` (antes de ganhar a arte).** Exportação do **seu** n8n, como o `noticias-1-texto` (mesmo `instanceId`, mesmas credenciais, Data Table `dicionario_ia`). O arquivo foi alterado às ~14:05 do mesmo dia (depois de entrar na pasta); não sei por quem nem o quê. Claude não mexeu nele.
7. **`dicionario-completo`.** Criado por Claude em 20/10 às ~14:11, a partir do `dicionario-v1` (texto) e dos nós de arte do `noticias-completo`. No prompt da IA, mudaram os limites de caracteres (agora os dos cards `dict-v1`, bem menores) e entrou o `prompt_imagem`; o resto do texto do prompt é o seu. Os nós de código foram testados numa simulação com dados de mentira, e o pedido gerado passou no validador do gerenciador. **Não foi importado nem rodado no n8n de verdade.**
8. **Marca dos cards.** O texto do cabeçalho dos cards vem de `marca` no nó **Configuração** (`noticias-completo`, `dicionario-completo`) ou de `entrada.marca` no arquivo de `entradas/` (`noticias-2-arte`). O padrão agora é `@iaclube.help` (antes `@iaclube`). Exige o gerenciador que aceita essa marca (acrescentada ao `iaclube_n8n` em 20/10/2026); com um gerenciador mais antigo o pedido dá `422 entrada_invalida`. Os textos dos encerramentos ("…toda semana no @iaclube…") não mudaram.
