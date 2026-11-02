# Atlas React workspace

React + Vite + Tailwind CSS, Radix tabs/confirmation dialogs, and React Flow.

`npm ci --prefix frontend` installs the locked frontend environment.
`npm run build --prefix frontend` bundles into `src/atlas/static/workspace/`, served at `/` by FastAPI.
`npm run dev --prefix frontend` starts Vite with local API proxies to port 8030.

The new workspace replaces the old DOM-driven dashboard at `/`. Earlier browser scripts target that earlier interface and are historical checks, not validation of this React application. The new interface supports scenario settings, round playback, matrix and ledger tabs, network editing, connector-based loans, bank inspection, draft recovery, and experiment export. Combined graph/matrix and the rehearsal recorder from the earlier interface are not migrated yet.

Design guidance: UI Skills `anthropics/frontend-design` and `ibelick/baseline-ui`. Dark slate surfaces, restrained blue accents, compact hierarchy, one primary canvas, inline bank inspector, explicit destructive-action confirmation. No decorative motion.
