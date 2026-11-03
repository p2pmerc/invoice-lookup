# invoice-lookup

A small read-only invoice search API: Flask and SQLite, API-key authenticated.

## Endpoints

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/health` | no auth |
| GET | `/invoices?customer=&status=&limit=` | substring match on customer, optional exact status |
| GET | `/invoices/<number>` | one invoice |

Send your key in `X-Api-Key`.

## Run

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Keys live in the `api_keys` table; add one with `sqlite3 invoices.db "INSERT INTO api_keys (owner, key) VALUES ('me', 'dev-key')"`.

## Tests

```sh
python -m unittest discover tests
```
