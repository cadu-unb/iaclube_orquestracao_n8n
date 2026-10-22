# A fazer

## 1. Revisar os fluxos de `workflows/completo` para a API da 8000 em `/api/v1/` (obrigatório, último passo do MVP 1.9.1)

**Pedido do usuário em 2026-10-22.** O `iaclube_n8n` (a porta 8000) vai mover toda a sua API para **`/api/v1/…`**, como a 7000 já faz (fase 0B do MVP 1.9.1 de lá: `_plan/implementacao/mvp-1.9.1/fase-0B-api-em-api-v1.md`). O usuário aceita o trabalho de rever os fluxos e quer a decisão **o quanto antes**.

**Quando fazer (decisão do usuário, 2026-10-22):** **não é um "a fazer" opcional.** É o **último passo do MVP 1.9.1** do `iaclube_n8n` (`fase-H-fluxos-do-n8n.md`) e **será feito logo depois de a fase G fechar o 1.9.1**, porque o n8n precisa continuar funcionando. Até lá os endereços antigos `/saude` e `/integracao/*` **continuam respondendo, obsoletos** (com os cabeçalhos `Deprecation` e `Link`), para os fluxos não pararem; **a revisão termina com a retirada desses aliases** na 8000.

### O que os fluxos usam hoje (conferido em 2026-10-22)

Os três fluxos de `workflows/completo/` falam só com a **ponte** (`172.19.0.1:7777`), que repassa ao `gerenciador` (8000) e ao `gerador` (7000). Os endereços **do gerenciador** que aparecem nos nós:

| Endereço no fluxo (via ponte) | Vira | Fluxos |
|---|---|---|
| `/gerenciador/saude` | `/gerenciador/api/v1/saude` | `noticias-completo`, `dicionario-completo`, `hands_on-completo` |
| `/gerenciador/integracao/producao` | `/gerenciador/api/v1/integracao/producao` | os três |
| `/gerenciador/subir`, `/gerenciador/parar` | **não mudam** (são comandos da própria ponte) | os três |
| `/gerador/api/v1/…` | **não mudam** (a 7000 já usa `/api/v1/`) | `noticias-completo`, `dicionario-completo` |

A ponte também tem uma lista de endereços permitidos para o gerenciador (`scripts/ponte.py`, `PERMITIDOS["gerenciador"]`: `/(saude|integracao/(producao|validar|conjuntos|prompt))`), que precisa aceitar o prefixo novo.

### Tarefas

1. **Ponte:** a lista de permitidos aceita `/api/v1/saude` e `/api/v1/integracao/(producao|validar|conjuntos|prompt)` (e, por um tempo, os antigos); os testes de `testes/` cobrem os dois; **não** mexer na regra do token.
2. **Os três fluxos de `workflows/completo/`:** trocar os dois endereços da tabela acima; **nenhuma outra** mudança de comportamento; conferir os nós "Código" que leem `$json` da resposta (o corpo **não muda**: só o endereço).
3. **Os demais fluxos** (`noticias-2-arte`, `noticias-1-texto`, `servidores-sob-demanda`, `dicionario-v1`, `hands_on-v1`): conferir se chamam o gerenciador pelos endereços antigos e, se chamarem, trocar também (o usuário pediu, em especial, `workflows/completo`).
4. **Prova sem o n8n:** rodar a suíte de `testes/` (usar o venv do `iaclube_n8n`); **com o n8n**, rodar um fluxo de cada vez (reiniciar a ponte antes; ela serve `/documentos` desde o 1.9).
5. **Documentação:** `workflows/README.md`, `README.md`, `RELATORIO.md` e `PONTE_AUTOSTART.md` com os endereços novos.
6. **Retirar os aliases obsoletos na 8000** (`iaclube_n8n`, fase H) **só depois** de os três fluxos rodarem pelos endereços novos.

### Cuidados

- **Token da ponte:** o `workflows/servidores-sob-demanda.workflow.json` e alguns históricos têm o token real no lugar do marcador. **Não** commitar token; trocar pelo marcador antes de publicar o repositório e gerar um token novo.
- **Guardar o fluxo antigo** (exportar do n8n) antes de importar o novo, para poder voltar.
- Fazer **um fluxo de cada vez**, na ordem Hands on (sem imagens) → Dicionário → Notícias.

### Pronto quando

Os três fluxos de `workflows/completo/` rodam no n8n pelos endereços `/api/v1/…`, a ponte aceita os novos, os testes passam e o `iaclube_n8n` foi avisado.
