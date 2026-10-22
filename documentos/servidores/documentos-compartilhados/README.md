# Documentos compartilhados

Esta pasta é lida e gravada pelas **duas aplicações do IA Clube** e pelo **n8n**:

- a porta **8000** (gerenciador de carrosséis, repositório `iaclube_n8n`);
- a porta **7000** (gerador de imagens, repositório `iaclube_geracao_local`);
- a ponte e os fluxos do n8n deste repositório.

Os documentos ficam em [`prompts/`](prompts/): arquivos `.md` (prompts, glossários, prompts de imagem e outros), mais o `.tags.json`. **Não ponha nada além disso dentro de `prompts/`**: o que não for documento seria listado pelas telas.

**Como cada arquivo é lido** (nome, cabeçalho, tipo, categoria, links, gravação) está no contrato `docs/contratos/17-documentos-compartilhados.md` do `iaclube_n8n`. Para as aplicações usarem esta pasta, aponte `IACLUBE_DOCUMENTOS` para o caminho **absoluto** de `prompts/`.

**Uma pasta só, ligada por padrão (MVP 1.9.1, fase 0A):** os dois servidores usam esta pasta **sozinhos** quando sobem por `scripts/servidor.sh` ou pela ponte (a variável `IACLUBE_DOCUMENTOS` é definida ali). Quem sobe um servidor à mão define a variável, como acima. Sem a pasta ligada, as duas telas **avisam** em vez de mostrar só o catálogo próprio.

**Origem:** cada documento tem a chave `origem` no cabeçalho (`8000`, `7000` ou `outro`): quem **criou** o arquivo. Onde se edita não importa.

**Versionada aqui:** depois de criar ou editar documentos nas telas, **faça o commit neste repositório** (os programas nunca rodam `git`). As cópias `.bak` e os `.tmp` ficam de fora (`.gitignore`).

Situação: a pasta tem os seis arquivos que a 8000 já trazia, os dois estilos de imagem dos fluxos e os **23 prompts de imagem do catálogo da 7000** (migrados na fase 0A, sem apagar o `prompts.json` de lá).
