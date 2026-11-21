# University FAQ Chatbot

Projet académique de chatbot universitaire développé avec React, FastAPI,
ChromaDB et Groq. Il recherche des informations dans une FAQ et des PDF
avant de générer une réponse en français.

## Architecture

Question → API FastAPI → recherche ChromaDB → extraits → Groq → réponse.

Les FAQ et les extraits PDF sont indexés avec les embeddings locaux
par défaut de ChromaDB.

## Technologies

- Frontend : React, Vite
- Backend : Python, FastAPI
- Recherche vectorielle : ChromaDB
- Génération : API Groq
- Documents : JSON et PDF

## Installation du backend

Prérequis : Python 3.12.

Créer et activer un environnement virtuel, puis exécuter :

```bash
python -m pip install -r backend/requirements.txt
```

Copier `backend/.env.example` vers `backend/.env`, puis renseigner
une clé Groq personnelle. Ne jamais publier ce fichier.

## Indexation et démarrage

Depuis le dossier `backend` :

```bash
python -m app.rag.ingest_faq
python -m app.rag.ingest_pdf
uvicorn app.main:app --reload
```

Documentation API : http://127.0.0.1:8000/docs

## Frontend

Avec Node.js 24, depuis le dossier `frontend` :

```bash
npm ci
npm run dev
```

## Exemple

Question : « Comment consulter les notes ? »

Le système recherche les extraits pertinents, puis transmet le contexte
et la question au modèle configuré dans `GROQ_MODEL`.

## Limites

- Démonstration locale, sans authentification.
- Historique serveur partagé en mémoire dans cette version.
- Les documents peuvent concerner des années universitaires anciennes.
- Les PDF scannés nécessitent une étape OCR.
- La pertinence de la recherche et les réponses générées restent à vérifier.
- Les questions et les extraits sélectionnés sont transmis à Groq.
