// Roda o código de um nó Code do n8n fora do n8n (simulação).
// Entrada (stdin, JSON): { codigo, contexto: { "Nome do nó": {json…} }, entrada: {json…} }
// Saída (stdout, JSON): { ok: true, itens: [...] } ou { ok: false, erro: "mensagem" }
const lido = require("fs").readFileSync(0, "utf8");
const { codigo, contexto = {}, entrada = {} } = JSON.parse(lido);
const $ = (nome) => {
  if (!(nome in contexto)) throw new Error("o nó «" + nome + "» não rodou (simulação sem contexto para ele)");
  return { first: () => ({ json: contexto[nome] }), all: () => [{ json: contexto[nome] }] };
};
const $input = { first: () => ({ json: entrada }), all: () => [{ json: entrada }] };
const $now = { toISODate: () => "2026-10-21" };
try {
  const f = new Function("$", "$input", "$now", codigo);
  const itens = f($, $input, $now).map((i) => i.json);
  process.stdout.write(JSON.stringify({ ok: true, itens }));
} catch (e) {
  process.stdout.write(JSON.stringify({ ok: false, erro: String(e.message) }));
}
