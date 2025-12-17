# Smart Market Dashboard (Vite + React)

This frontend is a production-ready starter for the Smart Market Platform dashboard.

Features
- Responsive layout (sidebar + header)
- Realtime line chart (Recharts)
- Simulation manager to emit /ingest payloads (mock or send to backend)
- Proxy configuration for dev to backend (Vite)

Quick start
1. Install deps:
   cd frontend
   npm install

2. Run dev server:
   npm run dev
   Open: http://localhost:5173

3. Build for production:
   npm run build
   Copy `dist` into backend static folder:
   mkdir -p ../smart_market_platform/static/dashboard
   cp -r dist/* ../smart_market_platform/static/dashboard/
   Restart backend.

Configuration
- API base: set VITE_API_BASE env var for dev/build:
  VITE_API_BASE="http://your.backend:6969" npm run dev
or create .env with VITE_API_BASE value.

Notes
- Controls -> Save writes simulation config to localStorage (used by SimulationManager)
- SimulationManager will attempt to POST to /ingest if "Send to backend" is enabled.
- If you need authentication, modify `api.js` to include tokens (Authorization header).

Design & Extensibility
- Replace styles.css with Tailwind or component library if desired.
- Add WebSocket connection for true realtime updates from backend.
- Hook DataTable to a persistence/store if needed.
