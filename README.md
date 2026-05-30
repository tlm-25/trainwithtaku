# TRAIN WITH TAKU WEBSITE

## TECH STACK

| Layer | Technology |
|---|---|
| Frontend | React, Vite, React Router, React Markdown, React Hot Toast |
| Backend | FastAPI, Python 3.12, uvicorn, uv |
| Database | MongoDB Atlas |
| Auth | JWT access tokens (in-memory) + refresh tokens (httpOnly cookies) |
| Rate Limiting | slowapi + Redis |
| LLM | OpenAI API |
| Containerisation | Docker, Docker Compose, nginx |

---

## RUNNING LOCALLY

### Option 1 — Dev servers (hot reload)

**Backend**
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`. Vite proxies `/api/*` requests to the backend at `http://localhost:8000`.

---

### Option 2 — Docker Compose (production-like)

Builds and runs both services in containers:
```bash
docker compose up --build
```

- Frontend available at `http://localhost:3000` (nginx serving built static files)
- Backend available at `http://localhost:8000`
- Backend secrets are injected from `backend/.env` at runtime
- `VITE_BASE_URL` defaults to `http://localhost:8000` if not set in shell

To pass a custom backend URL:
```bash
VITE_BASE_URL=https://your-backend.com docker compose up --build
```

---

## DOCKER — INDIVIDUAL IMAGE BUILDS

**Frontend** — `VITE_BASE_URL` must be passed at build time as Vite bakes it into the JS bundle:
```bash
# local (from root directory)
docker build --build-arg VITE_BASE_URL=http://localhost:8000 ./frontend

# production
docker build --build-arg VITE_BASE_URL=https://your-backend.com ./frontend
```

**Backend** — env vars are injected at runtime, no build args needed:
```bash
# local (load from .env file)
docker build ./backend
docker run --env-file backend/.env -p 8000:8000 <image-id>

# production (env vars set in cloud platform dashboard — GCP, Railway etc.)
docker build ./backend
docker run -e MONGO_DB_CONNECTION_STRING=... -e OPENAI_API_KEY=... -e JWT_SECRET_KEY=... -p 8000:8000 <image-id>
```
In practice on a cloud platform you set secrets in the dashboard and they are injected automatically — you don't pass `-e` flags manually.

---

## BACKEND

### Auth
- Access tokens are stored in-memory on the client (not localStorage) to prevent XSS attacks
- Refresh tokens are stored in httpOnly cookies so JavaScript cannot read them
- `fetchWithAuth` in `AuthContext.jsx` automatically refreshes expired access tokens and retries the original request

### Rate Limiting
- Two rate limiters: one keyed by IP (unauthenticated routes), one keyed by authenticated user (chat routes)
- Factory pattern used in `app_setup.py` to create the app with a configurable Redis URI — makes testing rate limits against an isolated Redis instance straightforward

### Chat Streaming
- Chat responses stream token-by-token from the LLM via FastAPI's `StreamingResponse`
- Retrieved source documents are sent as a final `__REFS__` chunk after the answer finishes streaming

---

## FRONTEND

### Chat Streaming
- A shared buffer (in `ChatContext`) accumulates streamed tokens per conversation ID
- This prevents data loss when switching between chats mid-stream — the buffer continues receiving even if the user navigates away
- `currentChatIDRef` (a ref, not state) lets the async stream loop read the latest active chat ID without stale closures

### Environment / API URL
- `VITE_BASE_URL` controls the backend URL
- In dev (`npm run dev`): not set — falls back to `http://localhost:8000` via `api.js`
- In Docker / production: injected as a build arg so Vite bakes it into the bundle at build time

### Multi-stage Docker Build
- Stage 1 (node): installs dependencies and runs `vite build`
- Stage 2 (nginx): copies only the built `/dist` folder — keeps the final image small
- `.dockerignore` excludes `node_modules` and `.env` files from the build context
