"""UTF-8 de ponta a ponta no que é do orquestrador (2026-10-30): os agentes pedem acento, os nós do n8n não o tiram do
conteúdo (só das chaves e dos nomes de arquivo) e a ponte devolve os documentos em UTF-8, sem escapes nem BOM."""

import json
import re
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import test_fluxos_prompt_de_reserva as nos  # noqa: E402
import test_ponte_documentos as pd  # noqa: E402

AGENTES = {
    "noticias-completo": "AI Agent - Noticias",
    "dicionario-completo": "AI Agent - Dicionario",
    "hands_on-completo": "AI Agent - Mao na Massa",
}
FRASE = "Não é só informação: é ação, coração e caçarola — “ok” 🙂"


@pytest.mark.parametrize("fluxo_nome", sorted(AGENTES))
def test_o_prompt_de_cada_agente_pede_portugues_com_acento(fluxo_nome):
    texto = nos.no(nos.fluxo(fluxo_nome), AGENTES[fluxo_nome])["parameters"]["text"]
    assert "IDIOMA E ACENTUAÇÃO" in texto and "Nunca remova acentos" in texto
    # a regra vem antes de qualquer outra instrução de conteúdo (a primeira seção)
    assert texto.index("IDIOMA E ACENTUAÇÃO") < texto.index("PERSONALIDADE DA MARCA")


def test_o_no_que_monta_os_cards_conserva_os_acentos_do_conteudo():
    ctx = nos._contexto_dicionario("a simple friendly illustration of:")
    ctx["Adiciona slide de CTA"]["termo"] = "Coração e ação"
    for slide in ctx["Adiciona slide de CTA"]["slides"]:
        slide["texto"] = FRASE
    r = nos.rodar(nos.fluxo("dicionario-completo"), "Montar entrada dos cards", ctx)
    assert r["ok"], r
    entrada = r["itens"][0]["entrada"]
    assert entrada["assunto"] == "Coração e ação"
    assert all(c["campos"]["corpo"] == FRASE for c in entrada["cards"][1:3])


def test_a_ponte_devolve_os_documentos_em_utf8_sem_escapes(tmp_path):
    pasta = tmp_path / "docs"
    pasta.mkdir()
    (pasta / "acentos.md").write_bytes(f"---\ntitulo: Ação e coração\ntipo: prompt\n---\n{FRASE}\n".encode())
    pd.ponte.cfg.token = pd.TOKEN
    pd.ponte.cfg.pasta_documentos = pasta
    http = ThreadingHTTPServer(("127.0.0.1", 0), pd.ponte.Ponte)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    try:
        pedido = urllib.request.Request(f"http://127.0.0.1:{http.server_address[1]}/documentos/acentos", headers={"X-Ponte-Token": pd.TOKEN})
        with urllib.request.urlopen(pedido, timeout=10) as r:
            bruto = r.read()
            tipo = r.headers["Content-Type"]
    finally:
        http.shutdown()
    assert "charset=utf-8" in tipo.lower()
    assert not bruto.startswith(b"\xef\xbb\xbf") and not re.search(rb"\\u00", bruto)
    assert json.loads(bruto.decode("utf-8"))["corpo"].strip() == FRASE


def test_nenhum_documento_compartilhado_tem_bom_nem_mojibake():
    for arquivo in sorted(pd.RAIZ.glob("documentos/servidores/documentos-compartilhados/prompts/*.md")):
        bruto = arquivo.read_bytes()
        assert not bruto.startswith(b"\xef\xbb\xbf"), f"{arquivo.name} tem BOM"
        texto = bruto.decode("utf-8")  # levanta erro se não for UTF-8 válido
        assert not re.search(r"Ã[\x80-\xbf]|Â[\x80-\xbf]|â€", texto), f"{arquivo.name} tem cara de mojibake (UTF-8 lido como Latin-1)"
