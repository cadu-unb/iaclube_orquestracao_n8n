# Relatório da sessão — 18/10/2026

Resumo do que foi feito, do que se aprendeu e do que fica para retomar no outro usuário (onde o n8n roda de fato).

## Resumo em uma linha

Foi montado um workflow do n8n (10 imagens + cards de Notícias IA) **e** uma "ponte" para ele conversar com os servidores, mas tudo foi pensado para rodar **neste usuário** (`yuri-santos`). O n8n roda em **Docker, em outro usuário** (`cadu`), então o desenho precisa ser revisto lá.

## O que foi feito

### 1. Porta padrão do gerador: 8765 → 7000
- Em `iaclube_geracao_local`: código (`dominio/portas.py`), testes, manuais, contratos, `ESTRUTURA.md` e as duas skills `for-dummy-*`.
- Onde 7000 era exemplo de "outra porta", virou 8765.
- Testes: front 132/132; back 759 passam e **6 falham, mas já falhavam antes** (catálogo de prompts e metadados de PNG).
- Ficaram como estavam, de propósito: `COMMITS.md` e os relatórios/roteiros antigos (são histórico).
- **Nada foi commitado** nesse repositório: as alterações estão só no diretório de trabalho.

### 2. Mapa de portas
| Porta | Quem |
|---|---|
| 7000 | gerador de imagens (`iaclube_geracao_local`) |
| 8000 | gerenciador de carrosséis (`iaclube_n8n`) |
| 5678 | o n8n |
| 8800 | só o simulador da plataforma irmã (não é padrão) |
| 5173 | dev server do front do gerador (padrão do Vite) |

O motor `sd-cli` não abre porta. Não achei 8999 nem 17999 em nenhum dos repositórios.

### 3. Esta pasta (`iaclube_orquestracao_n8n`)
```
workflows/noticias-10-cards.workflow.json   workflow (33 nós), para importar no n8n (hoje noticias-2-arte.workflow.json)
entradas/exemplo-noticias-10.json           12 cards (capa + 10 notícias + encerramento) e 10 prompts de imagem
scripts/servidor.sh                         sobe/para/consulta os dois servidores (grupo de processos, PID e log)
scripts/ponte.py                            serviço HTTP no computador: sobe/para servidores, entrega as entradas e repassa a API
README.md                                   (escrito ANTES da ponte; veja "Pontos de atenção")
```

Fluxo do workflow: sobe o gerador → espera 5 s → confere `/api/v1/health` → enfileira as 10 imagens → consulta `/api/v1/status` até concluir → pega o caminho de cada imagem → desliga o gerador → sobe o gerenciador → `POST /integracao/producao` → desliga o gerenciador → devolve `pasta` e `arquivos`. Qualquer erro cai num ramo que desliga os dois servidores e termina com o motivo.

Decisões que valem ser revisadas: 12 cards **sem Índice** (o Índice de Notícias IA só tem 6 itens); imagens **Pequenas 3:2 (624×416, ≈4 min cada, ≈40 min no total)**, porque as Médias (944×624) levam ≈9 min cada, ≈90 min no total; notícias 7 a 10 do exemplo são textos genéricos, **sem fonte**.

## O que se aprendeu

1. **O n8n está em Docker, em outro usuário.** O primeiro erro (`cat: can't open ... No such file or directory`) veio disso: o container não enxerga `/home/yuri-santos/...`, não tem o `uv` e não alcança o `127.0.0.1` do computador.
2. Por isso os nós *Execute Command* do primeiro desenho **não funcionam** nesse n8n. Foram trocados por chamadas HTTP a uma ponte no computador.
3. Os dois servidores só aceitam `Host` `127.0.0.1`/`localhost` (o gerador recusa o resto com `invalid_host`) e escutam só em `127.0.0.1`. Um container não os alcança direto; daí a ponte repassar as chamadas.
4. O gerenciador (`iaclube_n8n`) **não tinha `.venv`** e o Chromium dele **não está instalado**: sem `uv sync` e `uv run playwright install chromium`, a produção dos cards falha com `render_falhou`.
5. O n8n do outro usuário "já puxava coisas" de lá. **Vale descobrir como** (volume montado? script? serviço?) antes de reaproveitar a ponte: pode existir um caminho mais simples.

## O que foi testado, e o que não foi

**Testado de verdade**
- `servidor.sh` com os dois servidores reais: subir, subir de novo (idempotente), consultar, parar, porta liberada.
- A entrada de exemplo e o pedido de produção montado pelo fluxo, no gerenciador real (`/api/v1/integracao/validar`): 12 cards, sem erros e sem avisos. Também passando pela ponte.
- A ponte: token obrigatório (401 sem ele), rota não permitida (403), tentativa de sair da pasta `entradas/` (404), servidor fora do ar (502), subir/parar pelo HTTP.
- O workflow, num simulador simples do n8n (script de teste que **não** está nesta pasta), com a ponte real e servidores de mentira, em quatro cenários: tudo certo, gerador sem motor, imagem que falha, produção que dá erro. Nos de falha, os dois servidores foram desligados e a mensagem saiu certa.

**Não testado**
- **Importar e rodar no n8n de verdade** (nem no n8n em Docker).
- **Gerar imagem de verdade** (o gerador não está configurado neste usuário) e **produzir os cards de verdade** (falta o Chromium).
- Que o container alcance a ponte (`host.docker.internal` precisa de `--add-host=host.docker.internal:host-gateway` no `docker run`/compose; firewall pode barrar).

## Pontos de atenção

- **O `README.md` desta pasta está desatualizado**: descreve o desenho com *Execute Command* (antes da ponte). Vale mais este relatório.
- A ponte escuta em `0.0.0.0` (para o container alcançar) e exige token (`X-Ponte-Token`); o token aparece no terminal ao subir e fica em `~/.config/iaclube-orquestracao/ponte.token`. No nó **Configuração** do workflow, ele está como `COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`.
- Se o fluxo falhar depois de enfileirar as imagens, os pedidos ficam gravados na fila do gerador e voltam a rodar quando ele subir de novo.
- Os testes com os servidores reais usaram pastas temporárias; nada foi criado dentro de `iaclube_n8n` nem de `iaclube_geracao_local` além da troca de porta do item 1.
- Ficaram **fora desta pasta** (em área temporária da sessão, que some com ela): o gerador do JSON do workflow e o simulador do n8n. Se quiser guardá-los, peça e eu os copio para cá.

## Para retomar no outro usuário

1. Ver como o n8n de lá já alcança as coisas do outro usuário e escolher o caminho mais simples (provavelmente sem a ponte).
2. Instalar o que falta lá: `uv sync` e `playwright install chromium` no gerenciador; configurar o gerador (motor e três modelos).
3. Ajustar os caminhos e o tamanho das imagens no nó **Configuração**, importar o workflow e rodar.
4. Substituir o texto das notícias 7 a 10 (e conferir as 1 a 6) por conteúdo real.
