from __future__ import annotations

import os
import psycopg2
from ugaforce_hr.security import hash_password

DATABASE_URL = os.getenv("UGAFORCE_HR_DATABASE_URL") or os.getenv("DATABASE_URL")
USERNAME = os.getenv("UGAFORCE_HR_RESET_ADMIN_USERNAME", "").strip()
PASSWORD = os.getenv("UGAFORCE_HR_RESET_ADMIN_PASSWORD", "")


def main() -> None:
    if not DATABASE_URL or not USERNAME or not PASSWORD:
        print("UGAFORCE-HR admin repair: skipped")
        return
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id::text,must_change_password,password_changed_at from ugaforce_hr_users where lower(username)=lower(%s) and role_name='HR_ADMIN'",
                (USERNAME,),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("HR_ADMIN account not found")
            _, must_change_password, password_changed_at = row
            if password_changed_at is not None and not must_change_password:
                print("UGAFORCE-HR admin repair: skipped; administrator already owns a user-defined password")
                return
            cur.execute(
                "update ugaforce_hr_users set password_hash=%s, active=true, failed_signins=0, locked_until=null, must_change_password=true, password_changed_at=null, updated_at=now() where lower(username)=lower(%s) and role_name='HR_ADMIN' returning id::text",
                (hash_password(PASSWORD), USERNAME),
            )
            if not cur.fetchone():
                raise RuntimeError("HR_ADMIN account not found")
        conn.commit()
    print("UGAFORCE-HR admin repair: completed")


if __name__ == "__main__":
    main()
