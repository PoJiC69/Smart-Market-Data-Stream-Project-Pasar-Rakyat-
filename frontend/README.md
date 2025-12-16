```markdown
# Smart Market Dashboard (React, Vite)

This is a minimal React dashboard scaffold using Vite. It demonstrates:
- Fetching OpenAPI paths from backend at /openapi.json
- Posting a sample ingest payload to /ingest
- Dev server with proxy to backend for CORS-less development
- Build output ready to be copied to backend static folder

Quick start
1. From repo root, create folder `frontend` and place files here (package.json, vite.config.js, index.html, src/*).
2. Install dependencies:
   cd frontend
   npm install
3. Run dev server:
   npm run dev
   Open http://localhost:5173

Configuring API base URL
- In development the Vite dev server proxies `/ingest`, `/api/*`, `/openapi.json` to the backend default `http://localhost:6969`.
- To override the API base for build, set environment variable `VITE_API_BASE` when building or previewing:
  VITE_API_BASE="http://192.168.1.10:6969" npm run build

Build & deploy to FastAPI static folder
1. Build:
   npm run build
   This produces `frontend/dist` (per vite config outDir "dist").

2. Copy build to backend static folder expected by server:
   mkdir -p ../smart_market_platform/static/dashboard
   cp -r dist/* ../smart_market_platform/static/dashboard/

3. Restart backend (if running):
   uvicorn smart_market_platform.main:app --reload --port 6969

4. Open dashboard:
   http://localhost:6969/dashboard

Notes
- If you prefer Vue, you can create a Vite Vue project quickly:
  npm create vite@latest frontend-vue -- --template vue
  Then configure `vite.config.js` proxy similarly and build to `dist` to copy into backend static folder.
```