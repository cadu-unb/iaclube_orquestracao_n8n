# Prompt de geração de imagem

De onde vêm os prompts que geram as imagens dos cards, e se eles usam os prompts declarados no `iaclube_geracao_local`. Levantado em 21/10/2026, lendo o código dos fluxos e do gerador e os metadados das imagens que já foram geradas.

Detalhes por conjunto de cards: [Notícias](noticias/prompt-de-geracao-de-imagem.md) · [Dicionário](dicionario/prompt-de-geracao-de-imagem.md) · [Hands on](hands-on/prompt-de-geracao-de-imagem.md).

## Resposta curta

1. **A seção de prompts existe no gerador, mas não declara o estilo do IA Clube.** O que há lá é um catálogo de 23 prompts de exemplo e de teste (cenas de passarinho, lobo-guará, paisagens…, em estilos variados) e uma página **Prompts** na interface. Nada ali descreve "como são as imagens do IA Clube".
2. **Nenhum fluxo usa esses prompts.** Os fluxos pedem ao gerador um **prompt livre** (`/api/v1/jobs/free`), não um prompt do catálogo (`/api/v1/jobs` com `prompt_id`), e não usam etiquetas.
3. **O prompt de cada imagem é montado em dois pedaços, fora do gerador:** a **cena**, escrita pela IA que escreve o texto do post (ou à mão, no arquivo de exemplo das Notícias), e o **estilo**, um texto fixo (`estilo_comum`) guardado no nó **Configuração** de cada fluxo. A junção é `cena, estilo`.
4. **O gerador local não acrescenta nada.** O texto chega ao `sd-cli` exatamente como o fluxo montou: sem estilo extra, sem prompt negativo. Não há API de IA externa gerando a imagem; a IA externa só escreve a **cena**.
5. **O Hands on não gera imagens.** Os cards dele não têm espaço para imagem.

## 1. O que o `iaclube_geracao_local` tem de prompts

- **Catálogo:** [`catalogo/prompts/prompts.json`](../../../iaclube_geracao_local/catalogo/prompts/prompts.json), 23 prompts. Aparecem na página **Prompts** da interface e são pedidos pela API com `prompt_id`. Cada um traz o texto e um tamanho sugerido.
- **Etiquetas:** um recurso previsto para anexar a um pedido arquivos Markdown de instrução (por exemplo `estilo/noticias.md`, que ficaria na "plataforma irmã"). Com `etiquetas` no pedido, o gerador junta esses arquivos à instrução. **Na prática está vazio:** `catalogo/etiquetas/` só tem o README, não existe nenhuma etiqueta criada, nenhum arquivo `estilo/*.md` existe em nenhum dos repositórios, e a API de arquivos da plataforma irmã ainda não existe (é o que o próprio código diz).

| Categoria do catálogo | Qtde | O que são |
|---|---|---|
| Estilo | 8 | a mesma cena em técnicas diferentes: risografia, fotográfico, cartoon, surreal (passarinho), aquarela, pixel art, argila 3D, nanquim |
| Finalidade | 4 | capa de apresentação, avatar, ilustração para artigo, cartaz vertical |
| Assunto | 8 | paisagens, cidade na chuva, natureza-morta, gato, lobo-guará em quatro técnicas |
| Teste rápido | 3 | imagens de 16, 32 e 64 px, para testar o fluxo em segundos |

O catálogo **já foi usado**, mas direto no gerador: as 5 imagens `lobo_guara_*` de 18/10 (13:07) têm exatamente o texto dos prompts `lobo_guara_*` do catálogo. Não passou por nenhum fluxo.

A categoria **Estilo** é uma **vitrine de técnicas**, não o estilo da marca. O próprio documento de planejamento diz que as cores do cartoon "são apenas inspiração temática" e que não há paleta obrigatória para a imagem. Três prompts têm vocabulário parecido com o que os fluxos usam (`ilustracao_artigo`: "flat vector style, limited warm palette"; `capa_apresentacao`: "soft gradient of deep blue and warm yellow"; `avatar_perfil`: "flat vector illustration"), mas isso é só parecença: nenhum fluxo lê o catálogo.

## 2. De onde vem o prompt que gera as imagens hoje

```
 CENA (inglês)                           ESTILO FIXO (inglês)
 campo prompt_imagem, escrito pela IA    texto estilo_comum, no nó Configuração
 do post (ou à mão, no arquivo de        de cada fluxo
 exemplo das Notícias)
            \                                  /
             "cena, estilo"   (nó "Montar pedidos de imagem")
                            |
          POST /api/v1/jobs/free  { prompt, width, height, nome_arquivo }
                            |            (pela ponte, scripts/ponte.py)
          gerador local: sd-cli --prompt "<exatamente esse texto>"
```

- O nó **Montar pedidos de imagem** faz `prompt = cena + ", " + estilo_comum`. O código é **o mesmo** nos três fluxos de arte (`noticias-2-arte`, `noticias-completo`, `dicionario-completo`).
- O pedido vai por `/jobs/free` (prompt livre). Ele traz só `prompt`, `width`, `height` (624 × 416) e `nome_arquivo`. **Não leva `prompt_id` nem `etiquetas`.**
- Sem etiquetas, o gerador devolve "o próprio prompt" e nem consulta a plataforma irmã (está no código: `CompositorInstrucoes.compor`).
- O comando do motor leva o texto em `--prompt` e, fora ele, só opções técnicas (tamanho, 8 passos, CFG 1,0, threads, modelos). Não há prompt negativo nem sufixo de estilo.

## 3. O que cada fluxo usa

| Conjunto | Fluxo | Quem escreve a **cena** | **Estilo** fixo | Imagens | Já gerou imagens? |
|---|---|---|---|---|---|
| Notícias | `completo/noticias-completo` | a IA do texto (Claude Sonnet 4.6), campo `prompt_imagem` | azul e amarelo | 1 por notícia (4 a 6) | **não**: nunca foi rodado |
| Notícias | `noticias-2-arte` | **à mão**, em `entradas/exemplo-noticias-10.json` (os 10 atuais foram escritos por Claude em 18/10) | o mesmo azul e amarelo, no próprio arquivo | 10 | **sim**: 5 execuções com esses prompts (19/10 e 20/10) |
| Dicionário | `completo/dicionario-completo` | a IA do texto (GPT-5.4-pro), campo `prompt_imagem` | vermelho-alaranjado e azul-marinho | 2 | **sim**, 20/10 às 14:32 (Mixture of Experts) |
| Hands on | `completo/hands_on-completo` | (não gera imagens) | (não há) | 0 | não se aplica |

Ou seja: **todas as imagens de Notícias geradas até hoje têm os prompts escritos à mão do arquivo de exemplo**, e não prompts da IA. A única geração com prompt escrito pela IA foi a do Dicionário. (Pelos metadados dá para saber *qual prompt* gerou cada imagem, não *por qual caminho* ele foi pedido; os textos e os nomes batem com o `noticias-2-arte`.)

## 4. Prova: o prompt que está gravado na imagem

O gerador grava o prompt e os parâmetros dentro de cada PNG (campo `parameters`). Na imagem do Dicionário gerada em 20/10 às 14:32:

```
a machine room with many connected modules and wires, only a few modules glowing and sending signals into one shared output channel, the other modules dim and inactive, flat vector editorial illustration, bold simple shapes, soft gradients, vivid red-orange and deep navy palette on a warm off-white background, clean composition, wide landscape framing, no text, no letters, no numbers, no logos, no watermark
Steps: 8, CFG scale: 1.0, Guidance: 3.5, Seed: 42, Size: 624x416, Unet: z_image_turbo-Q4_K.gguf, TE: Qwen3-4B-Instruct-2507-Q4_K_M.gguf, VAE: ae.safetensors, stable-diffusion.cpp
```

A primeira parte (até `inactive,`) é a **cena** que a IA escreveu; o resto é o `estilo_comum` do fluxo, palavra por palavra. Nas imagens de Notícias é igual: a cena do arquivo de exemplo, seguida do estilo azul e amarelo. Em todas as imagens inspecionadas a semente foi **42** (o gerador não envia `--seed`; é o padrão do motor).

## 5. Os prompts declarados estão sendo usados?

**Não.** Consequências práticas:

- Mudar o catálogo de prompts do gerador **não muda** nenhuma imagem dos fluxos.
- O estilo está **copiado em três lugares**: `Configuração` do `noticias-completo`, `Configuração` do `dicionario-completo` e `estilo_comum` do `entradas/exemplo-noticias-10.json`. Mudar o visual das Notícias exige mudar dois deles.
- O texto do estilo foi escrito por Claude (o das Notícias em 18/10, o do Dicionário em 20/10, este a partir das cores do card: fundo `#f2f2f1`, texto `#0e1626`, acento `#e63415`). Não saiu do catálogo nem de uma regra aprovada por você.

Caminhos possíveis, se você quiser que o estilo passe a ser declarado num lugar só (nada disso foi feito):

1. **Manter no fluxo e documentar** (o mais simples): o `estilo_comum` de cada Configuração vira o estilo oficial, e este documento é o registro.
2. **Catálogo do gerador:** criar entradas de estilo lá. Não serve direto: cada entrada do catálogo é um prompt **completo** (cena incluída), não um estilo para somar à cena de cada notícia.
3. **Etiquetas** (`estilo/noticias.md`): é o desenho original para declarar estilo, mas depende da plataforma irmã servir os arquivos (a API não existe; há um simulador para testes) e de os fluxos mandarem `etiquetas` no pedido.

## 6. Como conferir o prompt de uma imagem

- **No n8n:** a saída do nó **Montar pedidos de imagem** mostra, em `corpo.prompt`, o texto exato enviado ao gerador.
- **Na imagem pronta:** o prompt e os parâmetros estão gravados no PNG.

```bash
strings -n 80 ~/Imagens/geracao_local/2026-10-20/20261020-143258-dicionario_mixture_of_experts_moe_2.png | head -2
```

- **Na API do gerador:** `GET /api/v1/jobs/TICKET` devolve o texto final do pedido (`instrucao_final`).
