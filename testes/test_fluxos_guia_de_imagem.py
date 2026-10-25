"""O guia de imagem de cada agente vira documento (MVP 1.9.1, fase H): simulação dos nós, sem o n8n.

O que se prova: o texto do guia que o designer edita na tela Prompts é **o mesmo** que o agente recebia escrito no
nó (o prompt final sai byte a byte igual), a falha é clara e nada de guia ficou escondido nos fluxos.
"""

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "documentos" / "servidores" / "documentos-compartilhados" / "prompts"
COMPLETO = RAIZ / "workflows" / "completo"
GUIAS = {
    "noticias-completo": ("AI Agent - Noticias", "guia-de-imagem-noticias"),
    "dicionario-completo": ("AI Agent - Dicionario", "guia-de-imagem-dicionario"),
}
#: sha256 do texto do agente **antes** da fase H (com a seção de imagem escrita no nó), medido em 2026-10-23.
PROMPT_DE_ANTES = {
    "noticias-completo": "c11153cda7e891232c3bb43bf7284e8105f5163abce7dc5cd8d9cda7c04547c3",
    "dicionario-completo": "3b7b6de23179037d1028fe55d82b6ddf6afff17306f5b7c894bcbbe6fefe9c63",
    "hands_on-completo": "41af49ced93d52649c5c2e89e9dd8f6bb367678416ff79a92c6b1ff478e5927c",
}
AGENTE_DO_HANDS_ON = "AI Agent - Mao na Massa"
EXPRESSAO = "{{ $('Ler guia de imagem').first().json.corpo.trim() }}"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não instalado")


def fluxo(nome):
    return json.loads((COMPLETO / f"{nome}.workflow.json").read_text("utf-8"))


def no(d, nome):
    return next(n for n in d["nodes"] if n["name"] == nome)


def rodar(d, nome_do_no, contexto=None, entrada=None):
    pedido = {"codigo": no(d, nome_do_no)["parameters"]["jsCode"], "contexto": contexto or {}, "entrada": entrada or {}}
    saida = subprocess.run(["node", str(RAIZ / "testes" / "rodar_no.js")], input=json.dumps(pedido), capture_output=True, text=True, check=True)
    return json.loads(saida.stdout)


def documento(nome):
    texto = (PASTA / f"{nome}.md").read_text("utf-8")
    cabecalho, corpo = texto.split("\n---\n", 1)
    chaves = dict(re.findall(r"^(\w+): (.*)$", cabecalho.removeprefix("---\n"), flags=re.MULTILINE))
    return chaves, corpo


def prompt_final(nome_do_fluxo):
    """O texto que o agente recebe: a expressão do guia trocada pelo corpo do documento, como o n8n faz."""
    agente, doc = GUIAS[nome_do_fluxo]
    texto = no(fluxo(nome_do_fluxo), agente)["parameters"]["text"]
    _, corpo = documento(doc)
    return texto.replace(EXPRESSAO, corpo.strip())


# ----------------------------------------------------------------------------------------------- H-02


@pytest.mark.parametrize("arquivo", sorted(p.name for p in COMPLETO.glob("*.json")))
def test_h02_os_fluxos_completos_so_chamam_o_gerenciador_em_api_v1(arquivo):
    texto = (COMPLETO / arquivo).read_text("utf-8")
    enderecos = set(re.findall(r"/gerenciador/[A-Za-z0-9_/.-]+", texto))
    assert enderecos == {
        "/gerenciador/api/v1/saude",
        "/gerenciador/api/v1/integracao/producao",
        "/gerenciador/subir",
        "/gerenciador/parar",
    }, enderecos


@pytest.mark.parametrize("arquivo", sorted(p.name for p in (RAIZ / "workflows").glob("*.json")))
def test_h02_nenhum_fluxo_usa_os_enderecos_antigos(arquivo):
    texto = (RAIZ / "workflows" / arquivo).read_text("utf-8")
    assert not re.search(r"/gerenciador/(saude|integracao/)", texto), arquivo


# ----------------------------------------------------------------------------------------------- H-03


def test_h03_os_nos_que_leem_a_resposta_do_gerenciador_seguem_certos():
    """`Montar resultado` lê a resposta de `Produzir cards`; o corpo da resposta não mudou com o prefixo."""
    exemplo = RAIZ.parent / "iaclube_n8n" / "docs" / "api" / "exemplos" / "producao-resposta.json"
    if not exemplo.is_file():
        pytest.skip("o repositório iaclube_n8n não está ao lado")
    resposta = json.loads(exemplo.read_text("utf-8"))
    d = fluxo("noticias-completo")
    contexto = {
        "Produzir cards": resposta,
        "Configuração": {"serie": "news", "tipo": "noticias"},
        "Validar entrada": {"tipo": "noticias", "nome": "teste", "cfg": {}},
    }
    saida = rodar(d, "Montar resultado", contexto, resposta)
    assert saida["ok"], saida


# ----------------------------------------------------------------------------------------------- H-09


@pytest.mark.parametrize("fluxo_nome", sorted(GUIAS))
def test_h09_o_guia_existe_como_documento_com_o_texto_da_secao(fluxo_nome):
    agente, doc = GUIAS[fluxo_nome]
    chaves, corpo = documento(doc)
    assert chaves["tipo"] == "prompt" and chaves["origem"] == "outro"
    assert "n8n" in chaves["tags"] and chaves["titulo"]
    assert "{{" not in corpo and "}}" not in corpo
    primeira = corpo.splitlines()[0]
    assert primeira in ("A IMAGEM DE CADA NOTICIA", "AS IMAGENS")
    assert "prompt_imagem" in corpo and "em INGLES" in corpo
    # o texto do agente não tem mais a seção escrita: só a expressão que lê o documento
    texto = no(fluxo(fluxo_nome), agente)["parameters"]["text"]
    assert EXPRESSAO in texto and "em INGLES" not in texto


def test_h09_as_tags_novas_estao_no_cadastro():
    tags = json.loads((PASTA / ".tags.json").read_text("utf-8"))
    assert tags["n8n"] == "n8n" and tags["imagem"] == "Imagem"


# ----------------------------------------------------------------------------------------------- H-10


@pytest.mark.parametrize("fluxo_nome", sorted(GUIAS))
def test_h10_o_prompt_final_do_agente_e_byte_a_byte_o_de_antes(fluxo_nome):
    final = prompt_final(fluxo_nome)
    assert hashlib.sha256(final.encode("utf-8")).hexdigest() == PROMPT_DE_ANTES[fluxo_nome]


def test_h10_o_hands_on_nao_mudou():
    texto = no(fluxo("hands_on-completo"), AGENTE_DO_HANDS_ON)["parameters"]["text"]
    assert hashlib.sha256(texto.encode("utf-8")).hexdigest() == PROMPT_DE_ANTES["hands_on-completo"]
    assert "Ler guia de imagem" not in json.dumps(fluxo("hands_on-completo"))


def test_h10_o_texto_do_guia_editado_chega_ao_agente_sem_mexer_no_resto():
    antes = prompt_final("noticias-completo")
    corpo = documento("guia-de-imagem-noticias")[1]
    novo = corpo.replace("uma cena diferente para cada noticia", "uma cena diferente para cada noticia e sempre diurna")
    assert novo != corpo
    texto = no(fluxo("noticias-completo"), "AI Agent - Noticias")["parameters"]["text"]
    depois = texto.replace(EXPRESSAO, novo.strip())
    assert depois.replace(" e sempre diurna", "") == antes  # só a frase nova entrou


# ----------------------------------------------------------------------------------------------- H-11


@pytest.mark.parametrize("fluxo_nome", sorted(GUIAS))
def test_h11_a_leitura_vem_antes_de_tudo_e_a_falha_nao_leva_ao_agente(fluxo_nome):
    d = fluxo(fluxo_nome)
    con = d["connections"]
    assert con["Configuração"]["main"][0] == [{"node": "Ler guia de imagem", "type": "main", "index": 0}]
    ok, erro = con["Ler guia de imagem"]["main"]
    assert [x["node"] for x in ok] == ["Validar guia de imagem"] and [x["node"] for x in erro] == ["Guia de imagem não lido"]
    assert no(d, "Ler guia de imagem")["onError"] == "continueErrorOutput"
    assert "Guia de imagem não lido" not in con  # termina na falha: nada sai dele
    # 1.9.2-I: depois do guia vem a leitura do prompt de reserva das imagens; só então a memória
    assert con["Validar guia de imagem"]["main"][0] == [{"node": "Ler prompt de reserva", "type": "main", "index": 0}]
    assert con["Validar prompt de reserva"]["main"][0] == [{"node": "Memoria - ler", "type": "main", "index": 0}]


@pytest.mark.parametrize("fluxo_nome", sorted(GUIAS))
def test_h11_documento_vazio_ou_com_expressao_do_n8n_para_o_fluxo_dizendo_qual(fluxo_nome):
    d = fluxo(fluxo_nome)
    doc = GUIAS[fluxo_nome][1]
    cfg = {"serie": "x", "url_ponte": "http://x"}
    bom = rodar(d, "Validar guia de imagem", {"Configuração": cfg}, {"ok": True, "corpo": documento(doc)[1]})
    assert bom["ok"] and bom["itens"] == [cfg]  # passa a Configuração adiante, sem mudar nada
    for corpo, trecho in (("", "está vazio"), ("   \n", "está vazio"), ("cena {{ $json.x }}", "«{{» ou «}}»"), ("fim }}", "«{{» ou «}}»")):
        ruim = rodar(d, "Validar guia de imagem", {"Configuração": cfg}, {"ok": True, "corpo": corpo})
        assert not ruim["ok"] and doc in ruim["erro"] and trecho in ruim["erro"], (corpo, ruim)


@pytest.mark.parametrize("fluxo_nome", sorted(GUIAS))
def test_h11_ponte_desligada_ou_documento_ausente_para_o_fluxo_dizendo_qual(fluxo_nome):
    d = fluxo(fluxo_nome)
    doc = GUIAS[fluxo_nome][1]
    for entrada in ({"error": {"message": "connect ECONNREFUSED 172.19.0.1:7777"}}, {"error": {"message": "404", "description": "não existe o documento"}}):
        r = rodar(d, "Guia de imagem não lido", {}, entrada)
        assert not r["ok"] and doc in r["erro"] and "guia de imagem" in r["erro"].lower() and "ponte" in r["erro"]
    assert no(d, "Ler guia de imagem")["parameters"]["url"].endswith("/documentos/" + doc)
