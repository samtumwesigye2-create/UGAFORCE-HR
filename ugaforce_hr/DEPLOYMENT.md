# UGAFORCE-HR deployment

UGAFORCE-HR is deployed as an independent Railway service with a dedicated PostgreSQL database.

Production start command:

```bash
bash ugaforce_hr/entrypoint.sh
```

Required variables:
- `UGAFORCE_HR_DATABASE_URL`
- `UGAFORCE_HR_BOOTSTRAP_KEY`
- `UGAFORCE_HR_ALLOWED_ORIGINS` (non-wildcard)

The entrypoint validates production settings, applies pending migrations, and starts `ugaforce_hr_runtime:app`.

Verify `/health` after Railway reports the service healthy. Do not share the UGAMAP database.
