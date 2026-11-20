# Validation results

Run date: 20 November 2026. Environment: Python 3.12.14, Node.js 24.22.3,
Linux. This records checks performed on the proposed branch; it does not claim
production readiness or a benchmark score.

| Check | Result |
| --- | --- |
| Backend `pytest -q` | 26 tests passed |
| Ruff lint and format checks | Passed |
| Frontend API client `npm test` | 3 tests passed |
| Frontend ESLint | Passed |
| Frontend production build | Passed with Vite 8.3.8 |
| Python `pip check` | No broken requirements |
| Full frontend `npm audit` | Zero known vulnerabilities after compatible lockfile updates |
| Unfiltered Python `pip-audit` | Four unique unresolved Chroma advisories (one duplicated record) |
| Scoped Python audit used in CI | Passed with the four documented advisory IDs excluded |
| Tracked files + original reachable history scan | Zero heuristic findings; 44 historical blobs inspected |
| Actual FAQ ingestion with default ONNX model | 3 entries indexed |
| Actual seven-PDF ingestion with default ONNX model | 316 chunks indexed |
| Shared local Chroma collection | 319 records total |
| API liveness via FastAPI TestClient | HTTP 200 |
| Relevant question with no Groq key | HTTP 503, sanitized configuration message |

## Retrieval smoke checks with actual embeddings

These were run against the bundled corpus using the real downloaded local ONNX
model, shared persistent collection, cosine search and final distance threshold 0.5.
They supplement the offline tests, which use deterministic test-only embeddings.

| Question | First retrieved source | Distance (rounded) |
| --- | --- | --- |
| Comment se fait l'inscription universitaire ? | `faq.json` | 0.1402 |
| Comment consulter les notes ? | `faq.json` | 0.2656 |
| Que faire en cas d'absence à un examen ? | `faq.json` | 0.2698 |
| Quel est le calendrier universitaire 2025-2026 ? | Calendar PDF, page 2 | 0.4326 |
| Comment cuisiner une pizza ? | No passage retained | Nearest distance exceeded 0.5 |

This small smoke set is not a labelled evaluation dataset. The threshold is an
initial demonstration setting and may reject relevant questions or admit irrelevant
excerpts. Retrieval precision/recall, answer faithfulness and multilingual quality
have not been benchmarked.

## Groq verification scope

The tests exercise the official Groq SDK through an `httpx.MockTransport`, verifying
the provider URL, model, system/user messages, retrieved context and completion limit.
They cover successful generation, empty completions, HTTP 400/401/429/500, connection
errors, timeouts, missing credentials, and the no-context branch that skips Groq.

**No live Groq generation was performed:** a real provider key was not available.
Provider account permissions, model availability for that account and actual generated
answer quality remain to be verified using a private `backend/.env`.

## UI verification scope

The frontend API client tests cover request serialization, source payloads, provider
error display inputs and malformed/non-JSON responses. Lint and the production build
passed. Automated browser interaction was attempted but Chromium could not launch
under the environment's process/socket restrictions. Visual layout and complete
browser interactions therefore remain unverified.

## Security scope

See [SECURITY.md](SECURITY.md) for the exact scan limitations, corpus review,
remaining Git history, and Chroma advisory exceptions. No assertion of complete
absence of sensitive data or known dependency vulnerabilities is made.
