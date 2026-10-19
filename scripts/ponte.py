#!/usr/bin/env python3
"""Ponte entre o n8n e os servidores do IA Clube, que rodam nesta máquina.

Por que existe: o n8n costuma rodar num container (ou como outro usuário). Dali ele não
enxerga as pastas dos projetos, não tem o `uv` e não alcança `127.0.0.1` do computador. A ponte
roda **aqui**, como o seu usuário, e o n8n conversa só com ela, por HTTP:

  GET  /saude                              sem token; serve para testar a conexão
  POST /servidores/{gerador|gerenciador}/subir
  POST /servidores/{gerador|gerenciador|todos}/parar
  GET  /servidores/{gerador|gerenciador|todos}/status
  GET  /entradas/ARQUIVO.json              lê um arquivo da pasta `entradas/`
  *    /gerador/...                        repassa ao gerador (127.0.0.1:7000)
  *    /gerenciador/...                    repassa ao gerenciador (127.0.0.1:8000)

Tudo, menos `/saude`, exige o cabeçalho `X-Ponte-Token`. A ponte só executa os dois comandos
fixos de `servidor.sh`, nas pastas dadas aqui na linha de comando; o n8n não manda comando
nem caminho nenhum. O repasse só aceita as rotas de API listadas abaixo.

Uso:  python3 scripts/ponte.py            (Ctrl+C para encerrar)
Só usa a biblioteca padrão do Python.
"""

import argparse
import hmac
import http.client
import json
import os
import re
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_CORPO = 2 * 1024 * 1024
TEMPO_REPASSE_S = 330  # a produção de cards pode levar até ~2 min; sobra folga

# Só estas rotas de cada servidor passam pela ponte.
ROTAS_PERMITIDAS = {
    "gerador": re.compile(r"/api/v1/(health|status|jobs(/free)?|jobs/[0-9a-fA-F-]+(/result)?)"),
    "gerenciador": re.compile(r"/(saude|integracao/(producao|validar|conjuntos|prompt))"),
}


class Config:
    pass


cfg = Config()


def _erro(codigo: str, mensagem: str) -> dict:
    return {"ok": False, "erros": [{"codigo": codigo, "mensagem": mensagem}]}


def _ler_token(argumento: str | None) -> tuple[str, str]:
    """Token vindo do argumento, da variável IACLUBE_PONTE_TOKEN ou do arquivo (criado na 1ª vez)."""
    if argumento:
        return argumento, "argumento --token"
    if os.environ.get("IACLUBE_PONTE_TOKEN"):
        return os.environ["IACLUBE_PONTE_TOKEN"], "variável IACLUBE_PONTE_TOKEN"
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    arquivo = base / "iaclube-orquestracao" / "ponte.token"
    if arquivo.exists() and arquivo.read_text(encoding="utf-8").strip():
        return arquivo.read_text(encoding="utf-8").strip(), str(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(secrets.token_urlsafe(24) + "\n", encoding="utf-8")
    arquivo.chmod(0o600)
    return arquivo.read_text(encoding="utf-8").strip(), f"{arquivo} (criado agora)"


def _servidor_sh(acao: str, qual: str) -> tuple[int, dict]:
    """Chama `servidor.sh` e devolve (status HTTP, JSON da resposta)."""
    pasta = {"gerador": cfg.pasta_gerador, "gerenciador": cfg.pasta_gerenciador}.get(qual, "")
    porta = {"gerador": cfg.porta_gerador, "gerenciador": cfg.porta_gerenciador}.get(qual, "")
    comando = ["bash", str(cfg.script), acao, qual]
    if acao == "start":
        comando += [str(pasta), str(porta)]
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=90, check=False)
    except subprocess.TimeoutExpired:
        return 504, _erro("tempo_esgotado", f"servidor.sh {acao} {qual} demorou mais de 90 s")
    linhas = [x for x in r.stdout.splitlines() if x.strip().startswith("{")]
    try:
        dados = json.loads(linhas[-1])
    except (IndexError, ValueError):
        return 500, _erro("script_invalido", (r.stdout + r.stderr).strip()[:400] or "sem saída")
    return (200 if dados.get("ok") else 500), dados


class Ponte(BaseHTTPRequestHandler):
    server_version = "IAClubePonte/1.0"

    def log_message(self, formato, *args):  # uma linha por pedido, sem o token
        sys.stderr.write("%s %s\n" % (self.address_string(), formato % args))

    # ------------------------------------------------------------------ saída
    def _enviar(self, status: int, corpo: bytes, tipo: str = "application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, status: int, dados: dict):
        self._enviar(status, json.dumps(dados, ensure_ascii=False).encode("utf-8"))

    def _autorizado(self) -> bool:
        enviado = self.headers.get("X-Ponte-Token", "")
        return hmac.compare_digest(enviado.encode(), cfg.token.encode())

    # ------------------------------------------------------------------ rotas
    def do_GET(self):
        self._rotear("GET")

    def do_POST(self):
        self._rotear("POST")

    def _rotear(self, metodo: str):
        url = urlsplit(self.path)
        caminho = url.path
        if metodo == "GET" and caminho == "/saude":
            return self._json(200, {"ok": True, "ponte": "iaclube-orquestracao", "autenticado": self._autorizado()})
        if not self._autorizado():
            return self._json(401, _erro("nao_autorizado", "falta o cabeçalho X-Ponte-Token ou ele não confere"))

        m = re.fullmatch(r"/servidores/(gerador|gerenciador|todos)/(subir|parar|status)", caminho)
        if m:
            return self._servidores(metodo, m.group(1), m.group(2))

        m = re.fullmatch(r"/entradas/([A-Za-z0-9._-]+\.json)", caminho)
        if m and metodo == "GET":
            return self._entrada(m.group(1))

        m = re.fullmatch(r"/(gerador|gerenciador)(/.*)", caminho)
        if m:
            return self._repassar(metodo, m.group(1), m.group(2) + (f"?{url.query}" if url.query else ""))

        self._json(404, _erro("nao_encontrado", "rota inexistente na ponte"))

    def _servidores(self, metodo: str, qual: str, acao: str):
        if (acao == "status") != (metodo == "GET"):
            return self._json(405, _erro("metodo_nao_permitido", "use GET para status e POST para subir/parar"))
        if acao == "subir" and qual == "todos":
            return self._json(400, _erro("pedido_invalido", "suba um servidor de cada vez"))
        script_acao = {"subir": "start", "parar": "stop", "status": "status"}[acao]
        alvos = ["gerador", "gerenciador"] if qual == "todos" else [qual]
        resultados = [_servidor_sh(script_acao, a) for a in alvos]
        status = max(s for s, _ in resultados)
        if len(resultados) == 1:
            return self._json(status, resultados[0][1])
        self._json(status, {"ok": status == 200, "servidores": [d for _, d in resultados]})

    def _entrada(self, nome: str):
        arquivo = (cfg.pasta_entradas / nome).resolve()
        if arquivo.parent != cfg.pasta_entradas.resolve() or not arquivo.is_file():
            return self._json(404, _erro("nao_encontrado", f"não existe entradas/{nome}"))
        self._enviar(200, arquivo.read_bytes())

    def _repassar(self, metodo: str, qual: str, destino: str):
        caminho = urlsplit(destino).path
        if not ROTAS_PERMITIDAS[qual].fullmatch(caminho):
            return self._json(403, _erro("rota_nao_permitida", f"a ponte não repassa {metodo} /{qual}{caminho}"))
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho > LIMITE_CORPO:
            return self._json(413, _erro("muito_grande", "corpo maior que 2 MiB"))
        corpo = self.rfile.read(tamanho) if tamanho else None
        porta = cfg.porta_gerador if qual == "gerador" else cfg.porta_gerenciador
        cabecalhos = {}
        if corpo is not None:
            cabecalhos["Content-Type"] = self.headers.get("Content-Type", "application/json")
        try:
            con = http.client.HTTPConnection("127.0.0.1", porta, timeout=TEMPO_REPASSE_S)
            con.request(metodo, destino, body=corpo, headers=cabecalhos)
            resposta = con.getresponse()
            dados = resposta.read()
            tipo = resposta.getheader("Content-Type", "application/json")
            self._enviar(resposta.status, dados, tipo)
            con.close()
        except OSError as erro:
            self._json(502, _erro("servidor_fora_do_ar", f"o {qual} não respondeu em 127.0.0.1:{porta} ({erro})"))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--porta", type=int, default=7777, help="porta da ponte (padrão 7777)")
    p.add_argument("--escutar", default="0.0.0.0", help="endereço (padrão 0.0.0.0, para o container alcançar; exige token)")
    p.add_argument("--pasta-gerador", type=Path, default=RAIZ.parent / "iaclube_geracao_local")
    p.add_argument("--pasta-gerenciador", type=Path, default=RAIZ.parent / "iaclube_n8n")
    p.add_argument("--porta-gerador", type=int, default=7000)
    p.add_argument("--porta-gerenciador", type=int, default=8000)
    p.add_argument("--entradas", type=Path, default=RAIZ / "entradas", help="pasta dos JSONs de entrada")
    p.add_argument("--script", type=Path, default=Path(__file__).with_name("servidor.sh"))
    p.add_argument("--token", help="token (por padrão: IACLUBE_PONTE_TOKEN ou um arquivo criado na 1ª vez)")
    a = p.parse_args()

    cfg.pasta_gerador, cfg.pasta_gerenciador = a.pasta_gerador, a.pasta_gerenciador
    cfg.porta_gerador, cfg.porta_gerenciador = a.porta_gerador, a.porta_gerenciador
    cfg.pasta_entradas, cfg.script = a.entradas, a.script
    cfg.token, origem = _ler_token(a.token)

    for rotulo, pasta in (("gerador", cfg.pasta_gerador), ("gerenciador", cfg.pasta_gerenciador), ("entradas", cfg.pasta_entradas)):
        if not pasta.is_dir():
            print(f"Aviso: a pasta do {rotulo} não existe: {pasta}", file=sys.stderr)

    servidor = ThreadingHTTPServer((a.escutar, a.porta), Ponte)
    print(f"Ponte no ar em http://{a.escutar}:{a.porta}", flush=True)
    print(f"  Token (cabeçalho X-Ponte-Token): {cfg.token}   [origem: {origem}]", flush=True)
    print(f"  gerador    {cfg.pasta_gerador}  (porta {cfg.porta_gerador})", flush=True)
    print(f"  gerenciador {cfg.pasta_gerenciador}  (porta {cfg.porta_gerenciador})", flush=True)
    print("  Ctrl+C para encerrar. Isto NÃO desliga os servidores que já estiverem de pé.", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPonte encerrada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
