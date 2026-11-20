# React frontend

The user interface for University FAQ Chatbot. See the [root README](../README.md)
for backend setup, document ingestion and the full architecture.

Requires Node.js 24 LTS. From this directory:

```bash
cp .env.example .env
npm ci
npm run dev -- --host 127.0.0.1
```

`VITE_API_URL` selects the FastAPI server and is public configuration. Restart Vite
or rebuild after changing it. Never store Groq keys in frontend environment files.

Checks: `npm run lint`, `npm test`, `npm run build`, `npm audit`.

Conversations live in this browser's localStorage, not in a shared backend history.
Retrieved filenames and pages are shown under each answer. They identify context
supplied to the model, not independently verified claims.
