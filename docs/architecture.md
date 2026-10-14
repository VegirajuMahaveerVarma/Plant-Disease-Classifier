# Architecture

The browser UI is Next.js and calls a separate FastAPI service for readiness, disease references, image predictions, and history. The API resizes images to 224×224 and normalizes them like the training pipeline. ResNet18 weights load only when a valid checkpoint and class mapping exist.

SQLite is the default local database; PostgreSQL is supported through `DATABASE_URL`. Records store filenames and scores, not image bytes.

## Before production
- Implement authentication and per-user authorization on each scan endpoint.
- Use migrations rather than `create_all`.
- Add data-retention semantics if object storage is introduced.
- Add rate limits, structured logs, lockfiles, vulnerability scans, and reverse-proxy request limits.
- Externally validate the model and complete the model card.
