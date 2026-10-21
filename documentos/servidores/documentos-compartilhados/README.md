# Documentos compartilhados

Esta pasta é lida e gravada pelas **duas aplicações do IA Clube** e pelo **n8n**:

- a porta **8000** (gerenciador de carrosséis, repositório `iaclube_n8n`);
- a porta **7000** (gerador de imagens, repositório `iaclube_geracao_local`);
- a ponte e os fluxos do n8n deste repositório.

Os documentos ficam em [`prompts/`](prompts/): arquivos `.md` (prompts, glossários, prompts de imagem e outros), mais o `.tags.json`. **Não ponha nada além disso dentro de `prompts/`**: o que não for documento seria listado pelas telas.

**Como cada arquivo é lido** (nome, cabeçalho, tipo, categoria, links, gravação) está no contrato `docs/contratos/17-documentos-compartilhados.md` do `iaclube_n8n`. Para as aplicações usarem esta pasta, aponte `IACLUBE_DOCUMENTOS` para o caminho **absoluto** de `prompts/`.

Situação (MVP 1.9, fase K): a pasta existe com os seis arquivos que a 8000 já trazia (copiados, sem apagar os originais). As aplicações passam a usá-la nas fases L, M e N.
