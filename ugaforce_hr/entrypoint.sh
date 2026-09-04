#!/usr/bin/env bash
set -euo pipefail

echo "UGAFORCE-HR: validating production environment"
python -m ugaforce_hr.acceptance --environment

echo "UGAFORCE-HR: applying pending database migrations"
python ugaforce_hr/migrate.py

echo "UGAFORCE-HR: ensuring first admin initialization"
python -m ugaforce_hr.bootstrap_once

echo "UGAFORCE-HR: checking one-time admin credential repair"
python -m ugaforce_hr.reset_admin_once

echo "UGAFORCE-HR: applying production UI upgrade"
python ugaforce_hr/ui_upgrade.py

echo "UGAFORCE-HR: starting API"
exec uvicorn ugaforce_hr_runtime:app --host 0.0.0.0 --port "${PORT:-8000}"
