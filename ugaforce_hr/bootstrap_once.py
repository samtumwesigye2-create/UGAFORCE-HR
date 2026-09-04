from __future__ import annotations

import os
import psycopg2

from ugaforce_hr.security import hash_password

DATABASE_URL = os.getenv("UGAFORCE_HR_DATABASE_URL") or os.getenv("DATABASE_URL")
USERNAME = os.getenv("UGAFORCE_HR_INITIAL_ADMIN_USERNAME", "").strip()
PASSWORD = os.getenv("UGAFORCE_HR_INITIAL_ADMIN_PASSWORD", "")


def main() -> None:
    if not DATABASE_URL or not USERNAME or not PASSWORD:
        print("UGAFORCE-HR first-admin init: skipped")
        return
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from ugaforce_hr_users")
            if cur.fetchone()[0] > 0:
                print("UGAFORCE-HR first-admin init: already initialized")
                return
            cur.execute(
                "insert into ugaforce_hr_users(username,password_hash,role_name) values(%s,%s,'HR_ADMIN') returning id::text",
                (USERNAME, hash_password(PASSWORD)),
            )
            uid = cur.fetchone()[0]
            cur.execute(
                "insert into ugaforce_hr_audit_log(actor_id,action,entity_type,entity_id,after_json) values(null,'bootstrap_admin','user',%s,%s::jsonb)",
                (uid, '{"role":"HR_ADMIN"}'),
            )
        conn.commit()
    print("UGAFORCE-HR first-admin init: created")


if __name__ == "__main__":
    main()
