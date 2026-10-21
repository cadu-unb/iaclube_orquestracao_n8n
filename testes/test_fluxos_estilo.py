"""Os fluxos leem o estilo das imagens de um documento (MVP 1.9, fase N): simulação dos nós, sem o n8n.

O código dos nós Code é executado com o Node.js (`rodar_no.js`), com um contexto no lugar dos nós anteriores. O que se prova:
o `prompt` final que o fluxo monta com o estilo **lido do documento** é idêntico ao de antes (`cena, estilo_comum`), a falha é
clara e nenhum texto de estilo ficou escondido nos fluxos.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
FLUXOS = {
    "noticias-completo": RAIZ / "workflows" / "completo" / "noticias-completo.workflow.json",
    "dicionario-completo": RAIZ / "workflows" / "completo" / "dicionario-completo.workflow.json",
    "noticias-2-arte": RAIZ / "workflows" / "noticias-2-arte.workflow.json",
}
DOCUMENTO_DO_FLUXO = {"noticias-completo": "estilo-noticias", "dicionario-completo": "estilo-dicionario", "noticias-2-arte": "estilo-noticias"}
PASTA = RAIZ / "documentos" / "servidores" / "documentos-compartilhados" / "prompts"
#: O `estilo_comum` que cada fluxo trazia escrito antes da fase N (os mesmos textos dos documentos).
ESTILO_ANTES = {
    "estilo-noticias": "flat vector editorial illustration, bold simple shapes, soft gradients, blue and warm yellow palette, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark",
    "estilo-dicionario": "flat vector editorial illustration, bold simple shapes, soft gradients, vivid red-orange and deep navy palette on a warm off-white background, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark",
}

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não instalado")


def fluxo(nome):
    return json.loads(FLUXOS[nome].read_text("utf-8"))


def no(d, nome):
    return next(n for n in d["nodes"] if n["name"] == nome)


def rodar(d, nome_do_no, contexto=None, entrada=None):
    pedido = {"codigo": no(d, nome_do_no)["parameters"]["jsCode"], "contexto": contexto or {}, "entrada": entrada or {}}
    saida = subprocess.run(["node", str(RAIZ / "testes" / "rodar_no.js")], input=json.dumps(pedido), capture_output=True, text=True, check=True)
    return json.loads(saida.stdout)


def corpo_do_documento(nome):
    texto = (PASTA / f"{nome}.md").read_text("utf-8")
    return texto.split("\n---\n", 1)[1]  # o que a ponte devolve em `corpo`


CFG = {"largura": 624, "altura": 416, "url_ponte": "http://172.19.0.1:7777", "token_ponte": "x"}
IMAGENS = [
    {"card": 2, "mascara": "imagem_1", "nome_arquivo": "noticia-01", "prompt": "a robot reading a newspaper, calm scene"},
    {"card": 3, "mascara": "imagem_1", "prompt": "  a fox in a library  "},
]
CARDS = [{"modelo": "capa", "campos": {}}, {"modelo": "texto-com-imagem", "campos": {}}, {"modelo": "texto-com-imagem", "campos": {}}]


def entrada_validar(nome_do_fluxo, **extra):
    dados = {"nome": "Teste", "tipo": "noticias", "entrada": {"serie": "news", "cards": CARDS}, "imagens": IMAGENS}
    dados.update(extra)
    return dados


@pytest.mark.parametrize("nome_do_fluxo", FLUXOS)
def test_n06_o_prompt_final_com_o_estilo_lido_do_documento_e_identico_ao_de_antes(nome_do_fluxo):
    d = fluxo(nome_do_fluxo)
    documento = DOCUMENTO_DO_FLUXO[nome_do_fluxo]
    validado = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar(nome_do_fluxo, estilo_documento=documento))
    assert validado["ok"], validado
    v = validado["itens"][0]
    assert v["estilo_documento"] == documento
    contexto = {"Validar entrada": v, "Ler estilo": {"ok": True, "nome": documento + ".md", "corpo": corpo_do_documento(documento)}}
    pedidos = rodar(d, "Montar pedidos de imagem", contexto)
    assert pedidos["ok"], pedidos
    esperado = [im["prompt"].strip() + ", " + ESTILO_ANTES[documento] for im in IMAGENS]
    assert [p["corpo"]["prompt"] for p in pedidos["itens"]] == esperado  # idêntico ao `cena, estilo_comum` de antes
    assert pedidos["itens"][0]["corpo"]["width"] == 624


@pytest.mark.parametrize("nome_do_fluxo", ["noticias-completo", "dicionario-completo"])
def test_n06_o_estilo_vira_obrigatorio_nos_fluxos_completos(nome_do_fluxo):
    d = fluxo(nome_do_fluxo)
    r = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar(nome_do_fluxo))
    assert not r["ok"] and "estilo_documento é obrigatório" in r["erro"]
    r = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar(nome_do_fluxo, estilo_documento="../x"))
    assert not r["ok"]


def test_n06_na_arte_estilo_documento_substitui_estilo_comum_e_o_arquivo_antigo_continua_valendo():
    d = fluxo("noticias-2-arte")
    antigo = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar("noticias-2-arte", estilo_comum=ESTILO_ANTES["estilo-noticias"]))
    assert antigo["ok"] and antigo["itens"][0]["estilo_documento"] == ""
    pedidos = rodar(d, "Montar pedidos de imagem", {"Validar entrada": antigo["itens"][0]})
    assert pedidos["ok"]
    assert pedidos["itens"][1]["corpo"]["prompt"] == "a fox in a library, " + ESTILO_ANTES["estilo-noticias"]
    os_dois = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar("noticias-2-arte", estilo_comum="x", estilo_documento="estilo-noticias"))
    assert not os_dois["ok"] and "use só um" in os_dois["erro"]
    sem_estilo = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar("noticias-2-arte"))
    assert sem_estilo["ok"]
    sem = rodar(d, "Montar pedidos de imagem", {"Validar entrada": sem_estilo["itens"][0]})
    assert sem["itens"][0]["corpo"]["prompt"] == "a robot reading a newspaper, calm scene"  # sem estilo, como antes


@pytest.mark.parametrize("nome_do_fluxo", FLUXOS)
def test_n06_documento_de_estilo_vazio_para_o_fluxo(nome_do_fluxo):
    d = fluxo(nome_do_fluxo)
    v = rodar(d, "Validar entrada", {"Configuração": CFG}, entrada_validar(nome_do_fluxo, estilo_documento="estilo-vazio"))["itens"][0]
    r = rodar(d, "Montar pedidos de imagem", {"Validar entrada": v, "Ler estilo": {"ok": True, "corpo": "  \n"}})
    assert not r["ok"] and "estilo-vazio" in r["erro"] and "vazio" in r["erro"]


@pytest.mark.parametrize("nome_do_fluxo", FLUXOS)
def test_n07_falha_clara_diz_qual_documento_e_chega_ao_ramo_de_falha(nome_do_fluxo):
    d = fluxo(nome_do_fluxo)
    contexto = {"Validar entrada": {"estilo_documento": "estilo-noticias"}}
    erro_do_n8n = {"error": {"message": "The service refused the connection - perhaps it is offline", "description": "ECONNREFUSED"}}
    r = rodar(d, "Estilo não lido", contexto, erro_do_n8n)
    assert r["ok"]
    motivo = r["itens"][0]["motivo"]
    assert "«estilo-noticias»" in motivo and "ECONNREFUSED" in motivo and "estilo-noticias.md" in motivo
    falha = rodar(d, "Montar mensagem de falha", {}, r["itens"][0])
    assert falha["itens"][0]["mensagem"] == motivo
    c = d["connections"]
    ler = no(d, "Ler estilo")
    assert ler["onError"] == "continueErrorOutput"
    assert c["Ler estilo"]["main"][1] == [{"node": "Estilo não lido", "type": "main", "index": 0}]
    assert c["Estilo não lido"]["main"][0] == [{"node": "Montar mensagem de falha", "type": "main", "index": 0}]


@pytest.mark.parametrize("nome_do_fluxo", FLUXOS)
def test_a_leitura_do_estilo_vem_antes_de_subir_o_gerador_e_usa_a_ponte_com_o_token(nome_do_fluxo):
    d = fluxo(nome_do_fluxo)
    c = d["connections"]
    assert c["Ler estilo"]["main"][0] == [{"node": "Subir gerador", "type": "main", "index": 0}]
    if nome_do_fluxo == "noticias-2-arte":
        assert c["Validar entrada"]["main"][0] == [{"node": "Estilo vem de documento?", "type": "main", "index": 0}]
        se = c["Estilo vem de documento?"]["main"]
        assert se[0] == [{"node": "Ler estilo", "type": "main", "index": 0}] and se[1] == [{"node": "Subir gerador", "type": "main", "index": 0}]
    else:
        assert c["Validar entrada"]["main"][0] == [{"node": "Ler estilo", "type": "main", "index": 0}]
    p = no(d, "Ler estilo")["parameters"]
    assert p["method"] == "GET" and "/documentos/" in p["url"] and "estilo_documento" in p["url"]
    assert p["headerParameters"]["parameters"][0]["name"] == "X-Ponte-Token"
    # todo nó citado nas conexões existe
    nomes = {n["name"] for n in d["nodes"]}
    for origem, saidas in c.items():
        assert origem in nomes
        for grupos in saidas.values():  # `main`, `ai_languageModel`…
            for grupo in grupos:
                for destino in grupo:
                    assert destino["node"] in nomes, destino


@pytest.mark.parametrize("nome_do_fluxo", FLUXOS)
def test_nenhum_texto_de_estilo_ficou_escondido_nos_fluxos(nome_do_fluxo):
    texto = FLUXOS[nome_do_fluxo].read_text("utf-8")
    for estilo in ESTILO_ANTES.values():
        assert estilo not in texto
    assert not re.search(r"estilo_comum\s*:\s*['\"]", texto.replace("estilo_comum: literal", ""))


def test_a_entrada_de_exemplo_usa_o_documento_de_estilo():
    entrada = json.loads((RAIZ / "entradas" / "exemplo-noticias-10.json").read_text("utf-8"))
    assert entrada["estilo_documento"] == "estilo-noticias" and "estilo_comum" not in entrada


def test_n08_os_fluxos_que_mexi_nao_ganharam_token_novo_e_o_dicionario_segue_em_branco():
    dicionario = FLUXOS["dicionario-completo"].read_text("utf-8")
    assert "token_ponte: 'COLE_AQUI_O_TOKEN_QUE_A_PONTE_MOSTRA'" in dicionario
