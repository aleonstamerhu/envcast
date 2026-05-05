# envcast

> Diff and sync environment variables across multiple deployment targets.

---

## Installation

```bash
pip install envcast
```

---

## Usage

Compare environment variables between two deployment targets:

```bash
envcast diff staging production
```

Sync missing variables from one target to another:

```bash
envcast sync staging production --dry-run
```

Pull current environment variables from a target into a local `.env` file:

```bash
envcast pull staging --output .env.staging
```

### Example Output

```
$ envcast diff staging production

  KEY                  STAGING         PRODUCTION
  ─────────────────────────────────────────────────
  DATABASE_URL         ✔ set           ✔ set
  REDIS_URL            ✔ set           ✘ missing
  SECRET_KEY           ✔ set           ✔ set
  NEW_RELIC_LICENSE    ✘ missing       ✔ set

2 variable(s) out of sync.
```

---

## Configuration

Define your targets in `envcast.yml`:

```yaml
targets:
  staging:
    provider: heroku
    app: my-app-staging
  production:
    provider: heroku
    app: my-app-production
```

---

## License

[MIT](LICENSE)