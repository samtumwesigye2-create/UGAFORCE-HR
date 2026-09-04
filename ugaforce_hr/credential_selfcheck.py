from __future__ import annotations

import os
import psycopg2

from ugaforce_hr.security import verify_password

DATABASE_URL = os.getenv("UGAFORCE_HR_DATABASE_URL") or os.getenv("DATABASE_URL")
USERNAME = os.getenv("UGAFORCE_HR_RESET_ADMIN_USERNAME", "").strip()
PASSWORD = os.getenv("UGAFORCE_HR_RESET_ADMIN_PASSWORD", "")


def main() -> None:
    if not DATABASE_URL or not USERNAME or not PASSWORD:
        print("UGAFORCE-HR credential self-check: skipped")
        return
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("select password_hash, active, locked_until from ugaforce_hr_users where lower(username)=lower(%s) and role_name='HR_ADMIN'", (USERNAME,))
            row = cur.fetchone()
            if not row:
                raise RuntimeError("credential self-check failed: HR_ADMIN account not found")
            password_hash, active, locked_until = row
            if not active:
                raise RuntimeError("credential self-check failed: account disabled")
            if locked_until is not None:
                raise RuntimeError("credential self-check failed: account locked")
            if not verify_password(PASSWORD, password_hash):
                raise RuntimeError("credential self-check failed: password hash mismatch")
    print("UGAFORCE-HR credential self-check: PASSED")


if __name__ == "__main__":
    main()
