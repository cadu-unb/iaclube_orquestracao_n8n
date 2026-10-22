#!/usr/bin/env bash
# Sobe, para ou consulta um dos dois servidores do IA Clube, para o workflow do n8n.
#
# Uso:
#   servidor.sh start  gerador|gerenciador PASTA_DO_PROJETO [PORTA]
#   servidor.sh stop   gerador|gerenciador|todos
#   servidor.sh status gerador|gerenciador|todos
#
# Portas padrão: gerador 7000, gerenciador 8000.
# Imprime UMA linha de JSON em stdout (o n8n lê isso); mensagens longas vão para o log.
# Código de saída: 0 deu certo; 1 não deu (start). `stop` e `status` sempre saem com 0.
#
# Onde ficam o PID e o log de cada servidor (por padrão, na pasta de estado do usuário):
#   $IACLUBE_ORQ_ESTADO ou ~/.local/state/iaclube-orquestracao/<servidor>.{pid,log}

set -u

export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

ACAO="${1:-}"
QUAL="${2:-}"
PASTA="${3:-}"
PORTA="${4:-}"

ESTADO="${IACLUBE_ORQ_ESTADO:-${XDG_STATE_HOME:-$HOME/.local/state}/iaclube-orquestracao}"

# Pasta de documentos única (contrato 17 do iaclube_n8n): os dois servidores a usam, a menos que
# IACLUBE_DOCUMENTOS já venha definida. Sem a pasta no disco, nada é exportado e cada servidor mostra o aviso.
RAIZ_ORQ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCUMENTOS_PADRAO="$RAIZ_ORQ/documentos/servidores/documentos-compartilhados/prompts"
if [ -z "${IACLUBE_DOCUMENTOS:-}" ] && [ -d "$DOCUMENTOS_PADRAO" ]; then
  export IACLUBE_DOCUMENTOS="$DOCUMENTOS_PADRAO"
fi
ESPERA_PARADA_S=25

saida() { # ok servidor acao mensagem [extra-json]
  printf '{"ok":%s,"servidor":"%s","acao":"%s","mensagem":"%s"%s}\n' "$1" "$2" "$3" "$4" "${5:+,$5}"
}

porta_padrao() {
  case "$1" in
    gerador) echo 7000 ;;
    gerenciador) echo 8000 ;;
  esac
}

porta_em_uso() { # porta
  (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null
}

viva() { # pid
  [ -n "$1" ] && kill -0 "$1" 2>/dev/null
}

iniciar() { # qual pasta porta
  local qual="$1" pasta="$2" porta="${3:-$(porta_padrao "$1")}"
  local pidfile="$ESTADO/$qual.pid" logfile="$ESTADO/$qual.log"
  mkdir -p "$ESTADO"

  if [ -f "$pidfile" ] && viva "$(cat "$pidfile")"; then
    saida true "$qual" start "já estava rodando (iniciado antes por este script)" "\"ja_rodando\":true,\"pid\":$(cat "$pidfile"),\"porta\":$porta"
    return 0
  fi
  rm -f "$pidfile"

  if [ -z "$pasta" ] || [ ! -d "$pasta" ]; then
    saida false "$qual" start "pasta do projeto não encontrada: $pasta"
    return 1
  fi
  if ! command -v uv >/dev/null 2>&1; then
    saida false "$qual" start "o comando uv não foi encontrado no PATH de $(whoami)"
    return 1
  fi
  if porta_em_uso "$porta"; then
    saida false "$qual" start "a porta $porta já está em uso por outro programa; feche-o ou escolha outra porta"
    return 1
  fi

  cd "$pasta" || { saida false "$qual" start "não consegui entrar em $pasta"; return 1; }
  printf '\n=== %s: iniciando %s (porta %s) ===\n' "$(date -Is)" "$qual" "$porta" >>"$logfile"

  # setsid: o servidor vira líder do próprio grupo, e `stop` encerra o grupo inteiro
  # (uv, Python e o motor de imagens), sem tocar no n8n.
  case "$qual" in
    gerador)
      setsid nohup uv run python -m iaclube_geracao_local --port "$porta" \
        >>"$logfile" 2>&1 </dev/null &
      ;;
    gerenciador)
      IACLUBE_HOST=127.0.0.1 IACLUBE_PORTA="$porta" \
        setsid nohup uv run python -m gerenciador \
        >>"$logfile" 2>&1 </dev/null &
      ;;
  esac
  echo $! >"$pidfile"
  saida true "$qual" start "iniciado; aguarde ele responder antes de usar" "\"ja_rodando\":false,\"pid\":$!,\"porta\":$porta,\"log\":\"$logfile\""
}

parar() { # qual
  local qual="$1" pidfile="$ESTADO/$1.pid"
  if [ ! -f "$pidfile" ]; then
    saida true "$qual" stop "nada a parar (sem PID deste script)" "\"parou\":false"
    return 0
  fi
  local pid
  pid="$(cat "$pidfile")"
  if ! viva "$pid"; then
    rm -f "$pidfile"
    saida true "$qual" stop "já estava parado" "\"parou\":false"
    return 0
  fi

  kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  local i=0
  while viva "$pid" && [ "$i" -lt "$ESPERA_PARADA_S" ]; do
    sleep 1
    i=$((i + 1))
  done
  local forcado=false
  if viva "$pid"; then
    kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
    forcado=true
    sleep 1
  fi
  rm -f "$pidfile"
  saida true "$qual" stop "parado" "\"parou\":true,\"forcado\":$forcado"
}

consultar() { # qual
  local qual="$1" pidfile="$ESTADO/$1.pid" porta
  porta="$(porta_padrao "$qual")"
  if [ -f "$pidfile" ] && viva "$(cat "$pidfile")"; then
    saida true "$qual" status "rodando" "\"rodando\":true,\"pid\":$(cat "$pidfile")"
  elif porta_em_uso "$porta"; then
    saida true "$qual" status "porta $porta ocupada por outro programa" "\"rodando\":false,\"porta_ocupada\":true"
  else
    saida true "$qual" status "parado" "\"rodando\":false"
  fi
}

case "$ACAO:$QUAL" in
  start:gerador | start:gerenciador) iniciar "$QUAL" "$PASTA" "$PORTA" ;;
  stop:gerador | stop:gerenciador) parar "$QUAL" ;;
  stop:todos)
    parar gerador
    parar gerenciador
    ;;
  status:gerador | status:gerenciador) consultar "$QUAL" ;;
  status:todos)
    consultar gerador
    consultar gerenciador
    ;;
  *)
    saida false "${QUAL:-?}" "${ACAO:-?}" "uso: servidor.sh start|stop|status gerador|gerenciador|todos [PASTA] [PORTA]"
    exit 1
    ;;
esac
