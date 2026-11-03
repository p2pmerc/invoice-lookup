CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY,
  customer TEXT NOT NULL,
  number TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK (status IN ('draft', 'sent', 'paid', 'void')),
  total_cents INTEGER NOT NULL,
  issued_on TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS api_keys (
  id INTEGER PRIMARY KEY,
  owner TEXT NOT NULL,
  key TEXT NOT NULL UNIQUE
);
