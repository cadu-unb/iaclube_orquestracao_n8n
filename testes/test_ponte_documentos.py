"""A ponte lê os documentos compartilhados (MVP 1.9, fase N): rotas, segurança e paridade com a 8000 e a 7000.

Os arquivos de `documentos-de-teste/` e o manifesto `documentos-de-teste-casos.json` são **os mesmos** da porta 8000 e
da porta 7000 (fase K): provam que as três leem cada arquivo do mesmo jeito.
"""

import hashlib
import importlib.util
import json
import shutil
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

TESTES = Path(__file__).resolve().parent
RAIZ = TESTES.parent
CASOS = json.loads((TESTES / "documentos-de-teste-casos.json").read_text("utf-8"))
TOKEN = "token-de-teste"


def _carregar_ponte():
    espec = importlib.util.spec_from_file_location("ponte", RAIZ / "scripts" / "ponte.py")
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


ponte = _carregar_ponte()


@pytest.fixture
def pasta(tmp_path) -> Path:
    destino = tmp_path / "documentos"
    shutil.copytree(TESTES / "documentos-de-teste", destino)
    (destino / ".gitattributes").unlink()
    (destino / "antigo.md.bak").write_text("cópia de segurança", encoding="utf-8")
    return destino


@pytest.fixture
def servidor(pasta):
    ponte.cfg.token = TOKEN
    ponte.cfg.pasta_documentos = pasta
    http = ThreadingHTTPServer(("127.0.0.1", 0), ponte.Ponte)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{http.server_address[1]}"
    http.shutdown()


def pedir(base: str, caminho: str, token: str | None = TOKEN, metodo: str = "GET"):
    cabecalhos = {"X-Ponte-Token": token} if token else {}
    pedido = urllib.request.Request(base + caminho, method=metodo, headers=cabecalhos, data=b"" if metodo == "POST" else None)
    try:
        with urllib.request.urlopen(pedido, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read())


# ----------------------------------------------------------------------------------------------- N-02


def test_n02_lista_devolve_os_validos_e_manda_os_ilegiveis_para_a_parte(servidor):
    status, lista = pedir(servidor, "/documentos")
    assert status == 200 and lista["ok"]
    assert {d["nome"] for d in lista["documentos"]} == set(CASOS["validos"])  # ignorados e .bak não aparecem
    assert {i["nome"] for i in lista["ilegiveis"]} == set(CASOS["ilegiveis"])
    assert all("corpo" not in d for d in lista["documentos"])


def test_n02_filtros_de_tipo_categoria_e_tag(servidor):
    nomes = lambda q: {d["nome"] for d in pedir(servidor, "/documentos" + q)[1]["documentos"]}  # noqa: E731
    assert nomes("?tipo=imagem") == {"imagem-completa.md", "imagem-sufixo.md"}
    assert nomes("?categoria=estilo") == {"imagem-sufixo.md"}
    assert nomes("?categoria=Teste%20R%C3%A1pido") == {"com-categoria.md"}  # a chave sai do rótulo digitado
    assert nomes("?tag=not%C3%ADcias") == {"prompt-simples.md", "glossario_com_sublinhado.md"}
    assert pedir(servidor, "/documentos?tipo=banana")[0] == 422


def test_n02_um_documento_traz_os_campos_do_contrato_17(servidor, pasta):
    for caminho in ("/documentos/prompt-simples", "/documentos/prompt-simples.md"):
        status, doc = pedir(servidor, caminho)
        assert status == 200 and doc["ok"]
        assert (doc["nome"], doc["titulo"], doc["tipo"], doc["categoria"], doc["tags"]) == (
            "prompt-simples.md",
            "Prompt de notícias",
            "prompt",
            "assunto",
            ["noticias", "ia"],
        )
        assert doc["corpo"].startswith("# Prompt de notícias")
        assert doc["hash"] == hashlib.sha256((pasta / "prompt-simples.md").read_bytes()).hexdigest()


# ----------------------------------------------------------------------------------------------- N-03


def test_n03_sem_token_da_401_em_todas_as_rotas_de_documentos(servidor):
    assert pedir(servidor, "/documentos", token=None)[0] == 401
    assert pedir(servidor, "/documentos/prompt-simples", token=None)[0] == 401
    assert pedir(servidor, "/documentos", token="errado")[0] == 401


@pytest.mark.parametrize(
    "caminho",
    [
        "/documentos/..%2f..%2fscripts%2fponte.py",
        "/documentos/../ponte",
        "/documentos/subpasta/ignorada",
        "/documentos/a%5Cb",
        "/documentos/antigo.md.bak",
        "/documentos/_oculto",
        "/documentos/con",
        "/documentos/Nome%20Invalido!",
        "/documentos/" + "a" * 65,
        "/documentos/C:x",
    ],
)
def test_n03_nome_fora_do_padrao_e_recusado_sem_tocar_no_disco(servidor, caminho):
    status, resposta = pedir(servidor, caminho)
    assert status in (404, 422) and not resposta["ok"]


def test_n03_grande_demais_nao_utf8_e_inexistente(servidor):
    assert pedir(servidor, "/documentos/grande-demais")[0] == 413
    assert pedir(servidor, "/documentos/nao-utf8")[0] == 422
    status, erro = pedir(servidor, "/documentos/nao-existe")
    assert status == 404 and "nao-existe.md" in erro["erros"][0]["mensagem"]


def test_n03_a_ponte_so_le_post_em_documentos_da_405(servidor):
    assert pedir(servidor, "/documentos/prompt-simples", metodo="POST")[0] == 405


def test_n03_pasta_ausente_da_503_na_lista(servidor, pasta, tmp_path):
    ponte.cfg.pasta_documentos = tmp_path / "nada"
    status, erro = pedir(servidor, "/documentos")
    assert status == 503 and "não foi encontrada" in erro["erros"][0]["mensagem"]


# ----------------------------------------------------------------------------------------------- N-04


def test_n04_cada_arquivo_de_teste_e_lido_como_o_contrato_17_manda(servidor):
    for nome, esperado in CASOS["validos"].items():
        status, doc = pedir(servidor, "/documentos/" + nome.removesuffix(".md"))
        assert status == 200, nome
        assert doc["titulo"] == esperado["titulo"], nome
        assert doc["tipo"] == esperado["tipo"], nome
        assert doc["categoria"] == esperado["categoria"], nome
        assert doc["tags"] == esperado["tags"], nome
        assert doc["avisos"] == esperado["avisos"], nome
        for linha in esperado["extras"]:
            chave, valor = (x.strip() for x in linha.split(":", 1))
            assert doc["extras"][chave] == valor, (nome, linha)
        if "corpo" in esperado:
            assert doc["corpo"] == esperado["corpo"], nome


@pytest.mark.parametrize("nome", CASOS["nomes-validos"])
def test_n04_nomes_validos(nome):
    assert ponte.nome_de_documento_valido(nome), nome


@pytest.mark.parametrize("nome", CASOS["nomes-invalidos"])
def test_n04_nomes_invalidos(nome):
    assert not ponte.nome_de_documento_valido(nome), nome


def test_n04_os_arquivos_de_teste_sao_iguais_aos_da_8000_quando_ela_esta_ao_lado():
    outro = RAIZ.parent / "iaclube_n8n" / "app" / "backend" / "tests" / "documentos-de-teste"
    if not outro.is_dir():
        pytest.skip("o iaclube_n8n não está ao lado deste repositório")

    def hashes(base: Path) -> dict[str, str]:
        return {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(base.rglob("*")) if p.is_file()}

    assert hashes(TESTES / "documentos-de-teste") == hashes(outro)
    assert (TESTES / "documentos-de-teste-casos.json").read_bytes() == (outro.parent / "documentos-de-teste-casos.json").read_bytes()


# ----------------------------------------------------------------------------------------------- N-05

#: sha256 do texto do `estilo_comum` que estava escrito em cada fluxo antes da fase N (sem a quebra de linha final).
ESTILOS = {
    "estilo-noticias": "a2551ce64623d35a07ff1411f1e9b3bb33e9703b95a01974c8be729dc2ab2cab",
    "estilo-dicionario": "677c0cff51006ac66639ee147fea0ff60c111d6c1492bf7f0d7e9b5b1f15dbfc",
}
PASTA_DE_VERDADE = RAIZ / "documentos" / "servidores" / "documentos-compartilhados" / "prompts"


@pytest.mark.parametrize("nome", ESTILOS)
def test_n05_os_documentos_de_estilo_tem_o_texto_identico_ao_estilo_comum_de_antes(nome):
    doc = ponte.ler_documento(PASTA_DE_VERDADE, nome)
    assert (doc["tipo"], doc["categoria"], doc["extras"]["uso"]) == ("imagem", "estilo", "sufixo")
    assert hashlib.sha256(doc["corpo"].strip().encode()).hexdigest() == ESTILOS[nome]


def test_a_pasta_de_verdade_so_tem_documentos_e_a_ponte_a_le_inteira():
    lista = ponte.listar_documentos(PASTA_DE_VERDADE)
    # 6 da 8000 + 2 estilos do n8n + os 23 prompts de imagem da 7000 (migrados na fase 0A do 1.9.1)
    assert lista["ilegiveis"] == [] and lista["total"] == 31
    assert not (PASTA_DE_VERDADE / "README.md").exists()
