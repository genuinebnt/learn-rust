# End-to-end tests

Browser tests of the screens built from the UX proposals (docs/COURSE_UX_PROPOSALS.md): the track table, the Tests pane run strip,
the course Run tab and stage page, and the comparison tables.

They need the API running with the built web app and a database you do not mind adding runs to:

```sh
cd web && pnpm build
ANNEAL_DATABASE_URL=postgres://anneal:anneal@localhost:5435/anneal_e2e ANNEAL_SANDBOX=host ANNEAL_ADDR=127.0.0.1:8791 cargo run -p anneal-api
cd web && pnpm exec playwright install chromium && pnpm e2e
```

`E2E_BASE_URL` points the tests elsewhere; `E2E_CHROME=1` uses the installed Chrome. The tests only add failing course runs, so no progress changes.
