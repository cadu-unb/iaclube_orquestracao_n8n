"""A ponte repassa o gerenciador pelos endereços `/api/v1/` e traduz os antigos (MVP 1.9.1, fase H).

Um servidor falso faz o papel do gerenciador (porta 8000) e anota o que a ponte lhe pediu.
"""

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
TOKEN = "token-de-teste"


def _carregar_ponte():
    espec = importlib.util.spec_from_file_location("ponte", RAIZ / "scripts" / "ponte.py")
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


ponte = _carregar_ponte()


@pytest.fixture
def mundo():
    pedidos: list[tuple[str, str]] = []

    class Falso(BaseHTTPRequestHandler):
        def _responder(self):
            pedidos.append((self.command, self.path))
            corpo = json.dumps({"ok": True, "caminho": self.path}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        do_GET = do_POST = _responder

        def log_message(self, *args):
            pass

    falso = ThreadingHTTPServer(("127.0.0.1", 0), Falso)
    threading.Thread(target=falso.serve_forever, daemon=True).start()
    ponte.cfg.token = TOKEN
    ponte.cfg.porta_gerenciador = falso.server_address[1]
    ponte.cfg.porta_gerador = falso.server_address[1]
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), ponte.Ponte)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}", pedidos
    servidor.shutdown()
    falso.shutdown()


def pedir(base: str, caminho: str, metodo: str = "GET", token: str | None = TOKEN):
    cabecalhos = {"X-Ponte-Token": token} if token else {}
    pedido = urllib.request.Request(base + caminho, method=metodo, headers=cabecalhos, data=b"{}" if metodo == "POST" else None)
    try:
        with urllib.request.urlopen(pedido, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read())


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("GET", "/gerenciador/api/v1/saude"),
        ("POST", "/gerenciador/api/v1/integracao/producao"),
        ("POST", "/gerenciador/api/v1/integracao/validar"),
        ("GET", "/gerenciador/api/v1/integracao/conjuntos"),
        ("POST", "/gerenciador/api/v1/integracao/prompt"),
    ],
)
def test_h01_a_ponte_repassa_os_enderecos_novos_do_gerenciador(mundo, metodo, caminho):
    base, pedidos = mundo
    status, corpo = pedir(base, caminho, metodo)
    assert status == 200 and corpo["caminho"] == caminho.removeprefix("/gerenciador")
    assert pedidos[-1] == (metodo, caminho.removeprefix("/gerenciador"))


@pytest.mark.parametrize(
    ("metodo", "antigo", "novo"),
    [
        ("GET", "/gerenciador/saude", "/api/v1/saude"),
        ("POST", "/gerenciador/integracao/producao", "/api/v1/integracao/producao"),
        ("POST", "/gerenciador/integracao/validar", "/api/v1/integracao/validar"),
        ("GET", "/gerenciador/integracao/conjuntos", "/api/v1/integracao/conjuntos"),
    ],
)
def test_h01_um_fluxo_antigo_continua_funcionando_porque_a_ponte_traduz(mundo, metodo, antigo, novo):
    base, pedidos = mundo
    status, _ = pedir(base, antigo, metodo)
    assert status == 200 and pedidos[-1] == (metodo, novo)


def test_h01_a_pergunta_da_url_vai_junto(mundo):
    base, pedidos = mundo
    assert pedir(base, "/gerenciador/integracao/conjuntos?a=1")[0] == 200
    assert pedidos[-1] == ("GET", "/api/v1/integracao/conjuntos?a=1")


@pytest.mark.parametrize(
    "caminho",
    [
        "/gerenciador/api/v1/projetos",
        "/gerenciador/projetos",
        "/gerenciador/api/v1/integracao/geracoes/noticias/x/y.png",
        "/gerenciador/api/v1/exportar",
        "/gerenciador/api/v1/saude/../projetos",
        "/gerenciador/api/v2/saude",
    ],
)
def test_h01_o_que_nao_esta_na_lista_continua_recusado(mundo, caminho):
    base, pedidos = mundo
    status, corpo = pedir(base, caminho)
    assert status == 403 and corpo["erros"][0]["codigo"] == "rota_nao_permitida", (caminho, corpo)
    assert pedidos == []


def test_h01_a_regra_do_token_nao_mudou(mundo):
    base, pedidos = mundo
    for caminho in ("/gerenciador/api/v1/saude", "/gerenciador/saude"):
        assert pedir(base, caminho, token=None)[0] == 401
        assert pedir(base, caminho, token="errado")[0] == 401
    assert pedidos == []


def test_h01_o_gerador_segue_como_antes(mundo):
    base, pedidos = mundo
    assert pedir(base, "/gerador/api/v1/health")[0] == 200
    assert pedidos[-1] == ("GET", "/api/v1/health")
    assert pedir(base, "/gerador/saude")[0] == 403
