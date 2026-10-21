# iaclube_orquestracao_n8n

> **Atenção:** este README foi escrito antes da ponte (`scripts/ponte.py`) e descreve o desenho com *Execute Command*, que não funciona com o n8n em Docker. Leia primeiro o [RELATORIO.md](RELATORIO.md).

Fluxos do n8n que produzem os carrosséis do IA Clube (**Notícias IA**, **Dicionário IA** e **Hands on**): a IA escreve o texto, o `iaclube_geracao_local` gera as imagens (nos conjuntos que têm), o `iaclube_n8n` (gerenciador de carrosséis) monta os cards, e o resultado volta como uma pasta de PNG e um card no Trello.

Esta pasta só chama as outras duas pela API (quem orquestra é o n8n). Quando um fluxo precisou de algo que a API não tinha, a mudança foi feita no `iaclube_n8n` (por exemplo `exportacao.instrucoes` e a marca `@iaclube.help`).

## O que tem aqui

```
workflows/                           os fluxos do n8n (Workflows → Import from File)
  completo/                            os que fazem tudo: texto pela IA → arte → card no Trello
    noticias-completo.workflow.json
    dicionario-completo.workflow.json
    hands_on-completo.workflow.json
  noticias-1-texto.workflow.json       só o texto (RSS → IA → Trello)
  noticias-2-arte.workflow.json        só a arte, a partir de um arquivo de entradas/
  servidores-sob-demanda.workflow.json liga os dois servidores por um tempo, para mexer nas telas (sem produzir nada)
  dicionario-v1.json                   só o texto do Dicionário IA
  hands_on-v1.json                     só o texto do Hands on
entradas/exemplo-noticias-10.json    entrada de exemplo do fluxo noticias-2-arte (10 notícias + o prompt de cada imagem)
scripts/ponte.py                     serviço HTTP no computador que o n8n (em Docker) chama
scripts/servidor.sh                  sobe, para e consulta os dois servidores
```

## Os fluxos

| Conjunto | Só o texto | Só a arte | Completo | Dispara | Imagens |
|---|---|---|---|---|---|
| Notícias IA | `noticias-1-texto` | `noticias-2-arte` | `completo/noticias-completo` | sexta 15h | uma por notícia |
| Dicionário IA | `dicionario-v1` | (não há) | `completo/dicionario-completo` | segunda 15h | 2 |
| Hands on | `hands_on-v1` | (não há) | `completo/hands_on-completo` | quarta 15h | nenhuma |

Todos usam a mesma **ponte**: rode um fluxo de cada vez. O que cada um faz, a ordem em que foram criados, onde fica o token da ponte, a marca dos cards e o `.json` de instruções estão em [workflows/README.md](workflows/README.md). O resto deste README descreve o fluxo de arte das Notícias (`noticias-2-arte`), que é o que as Notícias completas reaproveitam.

## Ligar os servidores só para mexer nas telas (`servidores-sob-demanda`)

Para quem não quer rodar um fluxo de produção, só abrir o gerador de imagens (porta 7000) e o gerenciador de carrosséis (porta 8000) no navegador. Duas entradas, ambas formulários do n8n:

- **Ligar:** pergunta por quantos minutos (5 a 240; vazio = 60). Confere antes se os dois estão livres; se estiverem, manda ligar os dois **um logo após o outro** (eles iniciam ao mesmo tempo), espera os dois responderem e mostra na tela os endereços e a hora em que desligam sozinhos.
- **Desligar:** desliga os dois antes do tempo.

Se **algum já estiver em uso** (ligado antes, por outro fluxo ou pessoa, ou com a porta tomada por outro programa), o fluxo **avisa na tela qual está ocupado e não liga nem desliga nada**. Se algo falhar ao ligar, **desliga os dois**, mostra o motivo e termina com erro.

Precisa da ponte no ar e do token dela no nó **Configuração**, como os outros fluxos. Os endereços mostrados (`127.0.0.1`) só abrem **neste computador**.

## O fluxo de arte (`noticias-2-arte`)

```
Iniciar → Configuração → lê o arquivo de entrada → valida
  → sobe o gerador (porta 7000) → espera 5 s → confere /api/v1/health
  → enfileira as 10 imagens → espera e consulta /api/v1/status até todas ficarem prontas
  → pega o caminho de cada imagem → desliga o gerador
  → sobe o gerenciador (porta 8000) → espera 5 s → confere /saude
  → POST /integracao/producao (12 cards + 10 imagens) → desliga o gerenciador
  → Entregar resultado: { pasta, arquivos, avisos }
```

Qualquer erro cai num ramo de falha que **desliga os dois servidores** e termina o fluxo com o motivo (nó **Falha no fluxo**).

## Antes de rodar (uma vez)

1. **O n8n precisa poder rodar comandos.** O nó *Execute Command* vem desativado em versões novas do n8n; se ele aparecer como "desconhecido" ao importar, habilite-o (por exemplo, iniciando o n8n com `NODES_EXCLUDE='[]'`).
2. **Quem roda o n8n é quem roda os servidores.** Neste computador o processo do n8n pertence ao usuário `cadu`, não ao `yuri-santos`. Esse usuário precisa de:
   - o `uv` (o script já procura em `~/.local/bin` e `/usr/local/bin`);
   - permissão de leitura e execução nas pastas dos dois projetos (os caminhos padrão do workflow apontam para `/home/yuri-santos/Documentos/GitHub/...`; ajuste em **Configuração** se os projetos ficarem em outro lugar);
   - o gerador configurado para **ele** (motor `sd-cli` e os três modelos, em `~/.config/iaclube-geracao-local/`);
   - o gerenciador preparado: `uv sync` e `uv run playwright install chromium` na pasta `iaclube_n8n`. **Sem o Chromium a produção dos cards falha** (`render_falhou`); foi o que aconteceu no teste feito aqui.
3. As duas portas (7000 e 8000) precisam estar livres. O script **não** troca de porta sozinho: se estiverem ocupadas, o fluxo falha com a mensagem.

## Como usar

1. No n8n: **Workflows → Import from File** e escolha `workflows/noticias-2-arte.workflow.json`.
2. Abra o nó **Configuração** e confira os caminhos, as portas e o tamanho das imagens.
3. Edite (ou copie) `entradas/exemplo-noticias-10.json` com as notícias reais.
4. Clique em **Execute workflow**. O resultado fica na saída do último nó, **Entregar resultado**.

### Configuração (nó "Configuração")

| Campo | Padrão | O que é |
|---|---|---|
| `caminho_entrada` | `.../entradas/exemplo-noticias-10.json` | arquivo com as notícias e os prompts |
| `pasta_scripts` | `.../iaclube_orquestracao_n8n/scripts` | onde está o `servidor.sh` |
| `pasta_gerador` / `pasta_gerenciador` | `.../iaclube_geracao_local` / `.../iaclube_n8n` | pastas dos projetos |
| `porta_gerador` / `porta_gerenciador` | 7000 / 8000 | portas dos servidores |
| `largura` × `altura` | 624 × 416 | tamanho das imagens (múltiplos de 16) |
| `espera_subir_s` | 5 | pausa depois de subir cada servidor |
| `intervalo_consulta_s` | 30 | de quanto em quanto tempo olhar a fila de imagens |
| `tempo_maximo_geracao_min` | 240 | desiste se as imagens passarem disso |

### Tamanho e tempo das imagens

O espaço da imagem no card é 839 × 592 (proporção ≈ 1,42). Os tamanhos de referência, na proporção 3:2, e a estimativa do próprio gerador:

| Tamanho | Largura × altura | Por imagem | 10 imagens |
|---|---|---|---|
| Pequena (padrão) | 624 × 416 | ≈ 4 min | ≈ 40 min |
| Média | 944 × 624 | ≈ 9 min | ≈ 90 min |

O padrão é o Pequeno porque bate com os 30 a 40 minutos esperados. Para Média, troque `largura` e `altura` em **Configuração**.

## O arquivo de entrada

```json
{
  "nome": "Notícias IA semana 12-18 outubro",
  "estilo_comum": "texto acrescentado ao fim de todo prompt de imagem",
  "entrada": { "serie": "news", "cards": [ ... ] },
  "imagens": [
    { "card": 2, "mascara": "imagem_1", "nome_arquivo": "noticia-01-dna", "prompt": "..." }
  ]
}
```

- `entrada` é o JSON de cards **exatamente** no formato do gerenciador (`serie`, `data`, `assunto`, `marca`, `cards`); o contrato está em `iaclube_n8n/docs/api/01-gerenciador.md`.
- `imagens[]` liga um prompt a um card: `card` é a **posição** do card em `entrada.cards` (o primeiro é 1), e `mascara` é a máscara de imagem do modelo (`imagem_1` no `texto-com-imagem`).
- O exemplo tem **12 cards**: capa, 10 `texto-com-imagem` e encerramento. Ficou **sem o Índice**, porque o Índice de Notícias IA só tem 6 itens.
- Os textos respeitam os limites de caracteres do modelo (título de até 31, texto de até 167 no `texto-com-imagem`). O gerenciador valida e avisa.
- **As notícias 1 a 6 vêm do teste de 08/09/2026 do `iaclube_n8n`; as 7 a 10 são textos genéricos, sem fonte.** O arquivo é só um exemplo para testar o fluxo.
- Os prompts de imagem estão em inglês, que o modelo entende melhor, e pedem "no text" para a imagem sair sem letras.

## `scripts/servidor.sh`

```bash
scripts/servidor.sh start  gerador|gerenciador PASTA [PORTA]
scripts/servidor.sh stop   gerador|gerenciador|todos
scripts/servidor.sh status gerador|gerenciador|todos
```

Imprime uma linha de JSON. O servidor sobe em segundo plano, num grupo de processos próprio, e `stop` encerra o grupo inteiro (envia `SIGTERM`, espera até 25 s e só então `SIGKILL`). Nunca encerra programa que ele não iniciou. PID e log ficam em `~/.local/state/iaclube-orquestracao/<servidor>.{pid,log}` (ou em `$IACLUBE_ORQ_ESTADO`).

## O que foi e o que não foi testado

**Testado:**
- `servidor.sh`, de verdade, com os dois servidores reais: subir, subir de novo (idempotente), consultar, parar e conferir que a porta ficou livre.
- A entrada de exemplo e o pedido de produção montado pelo fluxo, no gerenciador real (`/integracao/validar`): 12 cards, sem erros e sem avisos.
- O grafo do workflow, rodado num simulador simples do n8n contra servidores de mentira, em quatro cenários: tudo certo; gerador sem motor configurado; uma imagem que falha; produção que dá erro. Nos três cenários de falha os servidores foram desligados e a mensagem saiu certa.

**Não testado:**
- **Importação e execução no n8n de verdade.** Os erros que aparecerem aí (nomes de campos de um nó, versão do n8n, permissões) são o próximo passo.
- **Geração real de imagens** (os modelos do gerador não estão configurados neste ambiente de teste).
- **Produção real dos cards**: o Chromium do gerenciador não está instalado aqui.

## Limites conhecidos

- Se o fluxo falhar **depois** de enfileirar as imagens, os pedidos continuam gravados na fila do gerador e voltam a rodar na próxima vez que ele subir.
- O gerenciador gera uma produção por vez e a recusa com `504` se passar de 120 s; 12 cards ficam bem abaixo disso.
- Tudo roda na mesma máquina, sem chave de API (padrão dos dois contratos).
