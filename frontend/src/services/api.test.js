import assert from "node:assert/strict";
import { test, afterEach } from "node:test";
import { sendMessage } from "./api.js";

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test("sends the question and returns sources", async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "http://127.0.0.1:8000/chat");
    assert.deepEqual(JSON.parse(options.body), { question: "Inscription ?" });
    return new Response(JSON.stringify({ response: "Réponse", sources: [] }));
  };
  assert.deepEqual(await sendMessage("Inscription ?"), { response: "Réponse", sources: [] });
});

test("surfaces an API error instead of displaying an empty answer", async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Service indisponible" }), { status: 503 });
  await assert.rejects(sendMessage("Question"), /Service indisponible/);
});

test("handles a non-JSON error page and malformed success payload", async () => {
  globalThis.fetch = async () => new Response("Bad gateway", { status: 502 });
  await assert.rejects(sendMessage("Question"), /échoué/);
  globalThis.fetch = async () => new Response("{}");
  await assert.rejects(sendMessage("Question"), /invalide/);
});
