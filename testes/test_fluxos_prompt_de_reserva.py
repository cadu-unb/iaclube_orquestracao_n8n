"""O prompt de reserva das imagens vira documento (MVP 1.9.2, fase I): simulação dos nós, sem o n8n.

Quando a IA não escreve a cena de uma imagem (`prompt_imagem` vazio), os fluxos de Notícias e de Dicionário usavam um texto de
reserva escrito no nó **Montar entrada dos cards**. Agora o texto mora num documento da pasta compartilhada (tela Prompts) e o
fluxo o lê pela ponte, como o guia de imagem. O que se prova: o prompt final de cada imagem de reserva sai **byte a byte** igual ao
de antes; a falha é clara; os documentos têm tipo, categoria e a tag de imagem.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "documentos" / "servidores" / "documentos-compartilhados" / "prompts"
COMPLETO = RAIZ / "workflows" / "completo"
RESERVAS = {
    "noticias-completo": "prompt-de-reserva-noticias",
    "dicionario-completo": "prompt-de-reserva-dicionario",
}
#: Os textos que estavam escritos nos nós antes da fase I (medidos em 2026-10-25), sem o que se acrescenta depois.
TEXTO_DE_ANTES = {
    "noticias-completo": "an editorial illustration about artificial intelligence news, ",
    "dicionario-completo": "a simple friendly editorial illustration that explains the artificial intelligence concept: ",
}

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


# ----------------------------------------------------------------------------------------------- I-03


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i03_o_prompt_de_reserva_existe_como_documento_categorizado_e_com_a_tag_de_imagem(fluxo_nome):
    chaves, corpo = documento(RESERVAS[fluxo_nome])
    assert chaves["tipo"] == "prompt" and chaves["categoria"] == "sistema" and chaves["origem"] == "outro"
    assert "n8n" in chaves["tags"] and "imagem" in chaves["tags"] and chaves["titulo"]
    assert "{{" not in corpo and "}}" not in corpo and corpo.strip() == TEXTO_DE_ANTES[fluxo_nome].strip()


def test_i03_todo_documento_que_guia_imagem_tem_tipo_categoria_e_a_tag_imagem():
    """Os 23 prompts de imagem da 7000, os 2 estilos, os 2 guias e os 2 prompts de reserva: 29, todos filtráveis pela tag."""
    guiam = []
    for arquivo in sorted(PASTA.glob("*.md")):
        chaves, _ = documento(arquivo.stem)
        tags = [t.strip() for t in chaves.get("tags", "[]").strip("[]").split(",") if t.strip()]
        if chaves["tipo"] == "imagem" or "imagem" in tags:
            guiam.append(arquivo.stem)
            assert "imagem" in tags, arquivo.name
            assert chaves.get("categoria"), f"{arquivo.name} sem categoria"
    assert len(guiam) == 29, guiam
    assert {"estilo-noticias", "estilo-dicionario", "guia-de-imagem-noticias", "guia-de-imagem-dicionario", *RESERVAS.values()} <= set(guiam)


def test_i03_o_cadastro_de_tags_tem_a_tag_imagem():
    tags = json.loads((PASTA / ".tags.json").read_text("utf-8"))
    assert tags["imagem"] == "Imagem" and tags["n8n"] == "n8n"


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i03_o_nome_do_prompt_de_reserva_esta_no_fluxo_e_o_texto_nao_esta_mais(fluxo_nome):
    d = fluxo(fluxo_nome)
    assert no(d, "Ler prompt de reserva")["parameters"]["url"].endswith("/documentos/" + RESERVAS[fluxo_nome])
    codigo = no(d, "Montar entrada dos cards")["parameters"]["jsCode"]
    assert TEXTO_DE_ANTES[fluxo_nome].strip() not in codigo  # o texto saiu do nó
    assert "$('Ler prompt de reserva')" in codigo


# ----------------------------------------------------------------------------------------------- I-04


def _contexto_noticias(reserva):
    noticias = [
        {"manchete": "Uma manchete", "rotulo_indice": "preço da OpenAI", "texto_slide": "texto um", "prompt_imagem": ""},
        {"manchete": "Outra", "rotulo_indice": "regra nova", "texto_slide": "texto dois", "prompt_imagem": "a scene written by the AI"},
    ]
    slides = [
        {"papel": "gancho", "titulo": "Gancho", "texto": "t"},
        {"papel": "contexto", "titulo": "Índice"},
        {"papel": "desenvolvimento", "titulo": "Um", "texto": "a"},
        {"papel": "desenvolvimento", "titulo": "Dois", "texto": "b"},
        {"papel": "cta", "titulo": "Fim", "texto": "c"},
    ]
    return {
        "Configuração": {"serie": "news", "assunto": "IA em foco", "marca": "@iaclube.help", "estilo_documento": "estilo-noticias"},
        "Monta slides do carrossel": {"noticias": noticias, "slides": slides, "tema_card": "tema"},
        "Ler prompt de reserva": {"corpo": reserva},
    }


def _contexto_dicionario(reserva):
    slides = [
        {"papel": "gancho", "titulo_leve": "A IA pode te", "titulo": "esquecer.", "texto": "t"},
        {"papel": "contexto", "titulo": "Token", "texto": "c"},
        {"papel": "desenvolvimento", "titulo_leve": "um", "titulo": "dois", "texto": "x", "prompt_imagem": ""},
        {"papel": "desenvolvimento", "titulo_leve": "três", "titulo": "quatro", "texto": "y", "prompt_imagem": "a scene written by the AI"},
        {"papel": "desenvolvimento", "titulo": "cinco", "texto": "z"},
        {"papel": "desenvolvimento", "titulo": "seis", "texto": "w"},
        {"papel": "cta", "titulo": "Siga a gente", "texto": "Siga @iaclube"},
    ]
    return {
        "Configuração": {"serie": "dict-v1", "assunto": "Dicionário IA", "marca": "@iaclube.help", "estilo_documento": "estilo-dicionario", "tipo": "dicionario"},
        "Adiciona slide de CTA": {"termo": "Token", "slides": slides, "definicao_curta": "d", "tema_card": "tema"},
        "Ler prompt de reserva": {"corpo": reserva},
    }


def test_i04_o_prompt_final_de_reserva_das_noticias_e_byte_a_byte_o_de_antes():
    reserva = documento(RESERVAS["noticias-completo"])[1]
    r = rodar(fluxo("noticias-completo"), "Montar entrada dos cards", _contexto_noticias(reserva))
    assert r["ok"], r
    prompts = [i["prompt"] for i in r["itens"][0]["imagens"]]
    assert prompts[0] == TEXTO_DE_ANTES["noticias-completo"] + "preço da OpenAI"
    assert prompts[1] == "a scene written by the AI"  # a cena da IA continua vencendo


def test_i04_o_prompt_final_de_reserva_do_dicionario_e_byte_a_byte_o_de_antes():
    reserva = documento(RESERVAS["dicionario-completo"])[1]
    r = rodar(fluxo("dicionario-completo"), "Montar entrada dos cards", _contexto_dicionario(reserva))
    assert r["ok"], r
    prompts = [i["prompt"] for i in r["itens"][0]["imagens"]]
    assert prompts[0] == TEXTO_DE_ANTES["dicionario-completo"] + "Token"
    assert prompts[1] == "a scene written by the AI"


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i04_o_texto_editado_na_tela_chega_a_imagem_sem_mexer_no_resto(fluxo_nome):
    contexto = _contexto_noticias if fluxo_nome.startswith("noticias") else _contexto_dicionario
    reserva = documento(RESERVAS[fluxo_nome])[1]
    antes = rodar(fluxo(fluxo_nome), "Montar entrada dos cards", contexto(reserva))["itens"][0]["imagens"][0]["prompt"]
    depois = rodar(fluxo(fluxo_nome), "Montar entrada dos cards", contexto(reserva.strip() + " in a warm light"))["itens"][0]["imagens"][0]["prompt"]
    assert depois != antes and depois.replace(" in a warm light", "") == antes


def test_i04_os_fluxos_que_nao_mudaram_continuam_iguais():
    """O Hands on não gera imagem; o fluxo de arte avulso não tem texto de reserva: nada deles mudou."""
    assert "Ler prompt de reserva" not in json.dumps(fluxo("hands_on-completo"))
    assert "prompt-de-reserva" not in (RAIZ / "workflows" / "noticias-2-arte.workflow.json").read_text("utf-8")


# ----------------------------------------------------------------------------------------------- I-05


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i05_a_leitura_vem_antes_da_ia_e_a_falha_nao_segue_adiante(fluxo_nome):
    d = fluxo(fluxo_nome)
    con = d["connections"]
    ok, erro = con["Ler prompt de reserva"]["main"]
    assert [x["node"] for x in ok] == ["Validar prompt de reserva"] and [x["node"] for x in erro] == ["Prompt de reserva não lido"]
    assert no(d, "Ler prompt de reserva")["onError"] == "continueErrorOutput"
    assert "Prompt de reserva não lido" not in con  # termina na falha
    assert con["Validar guia de imagem"]["main"][0][0]["node"] == "Ler prompt de reserva"
    assert con["Validar prompt de reserva"]["main"][0][0]["node"] == "Memoria - ler"  # só depois a memória, a IA e o resto


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i05_documento_vazio_ou_com_expressao_do_n8n_para_o_fluxo_dizendo_qual(fluxo_nome):
    d = fluxo(fluxo_nome)
    doc = RESERVAS[fluxo_nome]
    cfg = {"serie": "x", "url_ponte": "http://x"}
    bom = rodar(d, "Validar prompt de reserva", {"Configuração": cfg}, {"ok": True, "corpo": documento(doc)[1]})
    assert bom["ok"] and bom["itens"] == [cfg]
    for corpo, trecho in (("", "está vazio"), ("   \n", "está vazio"), ("cena {{ $json.x }}", "«{{» ou «}}»"), ("fim }}", "«{{» ou «}}»")):
        ruim = rodar(d, "Validar prompt de reserva", {"Configuração": cfg}, {"ok": True, "corpo": corpo})
        assert not ruim["ok"] and doc in ruim["erro"] and trecho in ruim["erro"], (corpo, ruim)


@pytest.mark.parametrize("fluxo_nome", sorted(RESERVAS))
def test_i05_ponte_desligada_ou_documento_ausente_para_o_fluxo_dizendo_qual(fluxo_nome):
    d = fluxo(fluxo_nome)
    doc = RESERVAS[fluxo_nome]
    for entrada in ({"error": {"message": "connect ECONNREFUSED 172.19.0.1:7777"}}, {"error": {"message": "404", "description": "não existe o documento"}}):
        r = rodar(d, "Prompt de reserva não lido", {}, entrada)
        assert not r["ok"] and doc in r["erro"] and "prompt de reserva" in r["erro"] and "ponte" in r["erro"]
