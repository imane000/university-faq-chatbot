# Security and data review

Review date: 20 November 2026. Baseline: `5ea614c` on `main`.

## Repository contents and history

- Reviewed the tracked files and all 44 unique historical blobs reachable from the
  original repository refs for common provider tokens, private key headers and
  credential-bearing URLs. No matching credential was found.
- Extended the reproducible scan to include AWS access keys, long literal credential
  assignments and extracted PDF text. `scripts/check_repository.py --history` reports
  paths and finding types only, never the matched values. Run it with dependencies
  installed and after staging additions, so new files are covered.
- The previously tracked `chroma_db/chroma.sqlite3` was an empty generated database:
  zero embedding rows and no stored document metadata. It is removed from the proposed
  branch and ignored at every directory level. It remains in the existing Git history;
  no history rewrite was performed.
- The three FAQ entries are generic demonstration content. The seven PDFs contain
  university rules, calendars, fees and guides. Extracted text includes published
  institutional/association contacts and named representatives. No private student
  record or filled personal dossier was identified. This is a text/metadata review,
  not an exhaustive inspection of PDF images, attachments or hidden data.
- Original source URLs and redistribution permissions were not recorded. The
  [corpus inventory](../backend/data/README.md) states this limitation and the
  academic years, rather than implying current official guidance.

A heuristic scan cannot prove that a repository contains no sensitive data. Enable
GitHub secret scanning/push protection where available and review new corpus files.
If a credential is ever discovered, revoke/rotate it first; deleting a current file
alone does not remove it from Git history or earlier clones.

## Application changes

- Removed unauthenticated shared `/history` GET/DELETE endpoints and server-side
  conversation retention. They now return 404. The existing UI uses localStorage.
- Restricted CORS to explicitly configured origins and disabled credentialed CORS.
  CORS is a browser policy, not authentication.
- Groq credentials stay in the backend environment. Templates contain no key, and
  secret values use `SecretStr` to redact configuration representations.
- Provider error bodies and filesystem diagnostics are not returned to clients.
- Requests are validated and bounded; retrieved text and completion length are bounded.
- Groq receives the question and selected excerpts. Do not use private data without
  reviewing provider data handling and obtaining appropriate authorization.
- Prompts treat retrieved content as untrusted data. This reduces accidental instruction
  following but does not guarantee resistance to prompt injection or hallucination.

## Dependency audit and unresolved Chroma advisories

The frontend lockfile was refreshed with compatible security updates. `npm audit`
reported **zero known vulnerabilities**, including development dependencies, at review.
Unused OpenAI/LangChain integration packages and the duplicate Chroma requirement were
removed; the small text-splitter package remains alongside direct pypdf extraction.
Direct Python runtime and development dependencies are pinned to tested versions;
transitive Python dependencies are still resolved by pip and are not fully locked.

An unfiltered `pip-audit` still reports these **four unique ChromaDB advisories**
for `chromadb==1.5.9`, with no patched version listed at review:

| Advisory | Reported attack surface |
| --- | --- |
| [PYSEC-2026-311 / CVE-2026-45829](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c) | Remote code injection through server collection creation and untrusted model configuration |
| [PYSEC-2026-3814 / CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Remote code injection through server collection updates and untrusted model configuration |
| [PYSEC-2026-3815 / CVE-2026-45831](https://github.com/advisories/GHSA-xph7-9rjv-w5fr) | Cross-tenant scope checks in the server RBAC provider |
| [PYSEC-2026-3813 / CVE-2026-45830](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr) | Server collection authorization bypass |

This repository uses **embedded `PersistentClient` only**, with a fixed local ONNX
embedding implementation. It does not launch Chroma's HTTP server, accept collection
configuration from API users, or enable `trust_remote_code`. The reported server
endpoints and tenant authorization surfaces are therefore absent from this demo.
This is a scope-based mitigation, **not a dependency fix or a clean audit**.
Do not expose a Chroma server based on this setup.

CI explicitly excludes only these four advisory IDs while continuing to fail on other
known dependency findings. The exception must be reassessed when Chroma is upgraded,
a patched release becomes available, or the deployment topology changes.

Run the full audit (expected to report the unresolved advisories):

```bash
pip-audit --progress-spinner off
```

Run the scoped CI audit:

```bash
pip-audit --progress-spinner off \
  --ignore-vuln PYSEC-2026-311 --ignore-vuln PYSEC-2026-3814 \
  --ignore-vuln PYSEC-2026-3815 --ignore-vuln PYSEC-2026-3813
```

## Deployment scope

This is a local portfolio demo. Bind the API to `127.0.0.1`. Before public deployment,
add authentication, rate limiting/quotas, HTTPS, a reviewed corpus and deployment-specific
logging/privacy controls. A liveness response is not a readiness or security check.
