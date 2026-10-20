# Subir a ponte automaticamente (systemd --user)

Este arquivo só **descreve** como fazer; nada foi instalado nem ativado. Quem executa os comandos é você, como o usuário `cadu`.

A ponte (`scripts/ponte.py`) é o serviço que deixa o n8n (em Docker) conversar com o gerador de imagens e o gerenciador de cards, que rodam no computador. Hoje ela é iniciada à mão. A ideia aqui é um serviço do `systemd --user` que a inicia no boot e a reinicia se cair.

## Situação verificada no computador (19/10/2026)

- `systemctl --user` funciona (estado `running`); ainda não existe nenhum serviço em `~/.config/systemd/user/`.
- **Linger = `no`**: sem ele, o serviço só sobe depois que você faz login.
- O Docker está habilitado e o container do n8n (`runv2-n8n-1`) tem `restart: unless-stopped`: sobe sozinho no boot.
- `python3` em `/usr/bin/python3`; `uv` em `/home/cadu/.local/bin/uv`.
- A rede do n8n é `runv2_default` (ponte `br-b1bb80d6cbff`), gateway `172.19.0.1`. É esse o endereço que o container usa para chegar ao computador (o nome `host.docker.internal` não existe nesse container).

## Passo 1: criar o arquivo do serviço

Caminho: `~/.config/systemd/user/iaclube-ponte.service`

```ini
[Unit]
Description=Ponte n8n <-> servidores IA Clube
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/cadu/Documentos/GitHub/iaclube_orquestracao_n8n
Environment=PATH=/home/cadu/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 scripts/ponte.py --escutar 172.19.0.1
Restart=on-failure
RestartSec=5
# Sem isto, parar/reiniciar a ponte também derruba o gerador e o gerenciador que ela subiu
# (veja "Cuidados").
KillMode=process

[Install]
WantedBy=default.target
```

O que cada linha faz:

- **`Environment=PATH=...`**: o serviço não herda o PATH do seu terminal. Sem isso, o `servidor.sh` não acha o `uv` e responde "o comando uv não foi encontrado".
- **`--escutar 172.19.0.1`**: a ponte só aceita conexões vindas da rede do Docker; a porta 7777 não fica aberta para a rede local.
- **`Restart=on-failure` e `RestartSec=5`**: se a ponte cair, volta em 5 s. Isso também cobre o caso do passo 2.
- **`KillMode=process`**: ao parar ou reiniciar a ponte, o systemd encerra só o processo dela, e não o grupo inteiro.

## Passo 2: ordem no boot

O `systemd --user` não sabe esperar o Docker. Se a ponte iniciar antes de a rede `172.19.0.1` existir, ela falha com `Cannot assign requested address`; o `Restart=on-failure` faz ela tentar de novo a cada 5 s até o Docker criar a rede. Alternativas:

- **Manter `172.19.0.1`** e confiar no retry (recomendado).
- **Escutar em `0.0.0.0`** (o padrão do script): nunca falha por ordem, mas fica aberta na rede local, protegida só pelo token.

O IP `172.19.0.1` costuma se manter enquanto a rede do compose não for recriada. Se você rodar `docker compose down` e subir de novo e o IP mudar, atualize o `--escutar` do serviço e o `url_ponte` do nó **Configuração** do workflow.

## Passo 3: ativar

```bash
systemctl --user daemon-reload
systemctl --user enable --now iaclube-ponte
loginctl enable-linger cadu
```

- `enable --now` liga o serviço agora e em todo login.
- `enable-linger` é o que faz o serviço subir **no boot, sem você logar**. Esse comando muda uma configuração do sistema; por isso é um passo à parte e deliberado.

## Passo 4: token

Na primeira subida, a ponte cria `~/.config/iaclube-orquestracao/ponte.token` (permissão 600). O valor fica fixo daí em diante.

```bash
cat ~/.config/iaclube-orquestracao/ponte.token
```

Cole o valor em `token_ponte`, no nó **Configuração** do workflow (hoje está `COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA`), uma única vez.

## Passo 5: conferir

```bash
systemctl --user status iaclube-ponte
journalctl --user -u iaclube-ponte -f
curl http://172.19.0.1:7777/saude
```

Esperado no `curl`: `{"ok": true, "ponte": "iaclube-orquestracao", "autenticado": false}`.

## Administrar depois

| Ação | Comando |
|---|---|
| Reiniciar | `systemctl --user restart iaclube-ponte` |
| Parar | `systemctl --user stop iaclube-ponte` |
| Desativar o autostart | `systemctl --user disable --now iaclube-ponte` |
| Ver o log | `journalctl --user -u iaclube-ponte -n 50` |
| Desligar gerador e gerenciador | `POST /servidores/todos/parar` na ponte, ou `bash scripts/servidor.sh stop todos` |

## Cuidados

- **Servidores sobrevivem à ponte só com `KillMode=process`.** O `servidor.sh` sobe os servidores com `setsid`, mas isso não os tira do cgroup do serviço. Com o padrão do systemd (`KillMode=control-group`), parar ou reiniciar a ponte mataria também o gerador e o gerenciador, inclusive no meio de uma geração de imagens. Por isso o arquivo acima traz `KillMode=process`.
- **Firewall.** Se o `ufw` estiver ativo, ele pode bloquear o container de chegar à porta 7777. O teste feito em 19/10 (container até `172.19.0.1:7777`) funcionou, então por ora não há bloqueio.
- **Se mover a pasta da orquestração**, atualize `WorkingDirectory` e `ExecStart` e rode `systemctl --user daemon-reload`.
- **A ponte não instala nada**: `uv sync` e `uv run playwright install chromium` no gerenciador, e a configuração do gerador (motor e modelos), continuam sendo pré-requisitos.

## Por que não colocar a ponte dentro de um container

A ponte existe justamente para estar **fora** do container: é ela que enxerga o `uv`, as pastas dos projetos, o motor de imagens e o `127.0.0.1` dos servidores. Dentro de um container ela perderia tudo isso (exigiria `network_mode: host`, volumes para projetos, `.venv`, `uv` e modelos, e GPU configurada), sem ganho real sobre o `systemd --user` com linger. O caminho de verdade para "tudo em Docker" seria containerizar os próprios servidores na rede `runv2_default` e dispensar a ponte, o que é um trabalho bem maior.
