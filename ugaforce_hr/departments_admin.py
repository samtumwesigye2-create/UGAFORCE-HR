from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from ugaforce_hr.security import current_user, require_role
from ugaforce_hr_app import audit, db

router = APIRouter(prefix="/api/v1/departments", tags=["departments"])


class DepartmentPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=140)
    parent_dept_id: Optional[str] = None


def _row(cur: Any, department_id: str) -> dict[str, Any]:
    cur.execute(
        """select d.id::text,d.name,d.parent_dept_id::text,p.name parent_name,d.created_at
           from ugaforce_hr_departments d
           left join ugaforce_hr_departments p on p.id=d.parent_dept_id
           where d.id=%s""",
        (department_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Department not found")
    return dict(row)


@router.patch("/{department_id}")
def update_department(
    department_id: str,
    payload: DepartmentPatch,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    require_role(user, "HR_SPECIALIST")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No department changes supplied")
    with db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            before = _row(cur, department_id)
            new_name = (changes.get("name") or before["name"]).strip()
            parent_id = changes.get("parent_dept_id", before.get("parent_dept_id"))
            if parent_id == "":
                parent_id = None
            if parent_id == department_id:
                raise HTTPException(status_code=400, detail="A department cannot be its own parent")
            cur.execute("select id from ugaforce_hr_departments where lower(name)=lower(%s) and id<>%s", (new_name, department_id))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Department already exists")
            if parent_id:
                cur.execute("select id from ugaforce_hr_departments where id=%s", (parent_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=400, detail="Parent department does not exist")
                cur.execute(
                    """with recursive descendants as (
                           select id from ugaforce_hr_departments where parent_dept_id=%s
                           union all
                           select d.id from ugaforce_hr_departments d join descendants x on d.parent_dept_id=x.id
                       ) select 1 from descendants where id=%s limit 1""",
                    (department_id, parent_id),
                )
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Parent selection would create an organization cycle")
            cur.execute("update ugaforce_hr_departments set name=%s,parent_dept_id=%s where id=%s", (new_name, parent_id, department_id))
            after = _row(cur, department_id)
            audit(conn, user.get("employee_id"), "updated", "department", department_id, before=before, after=after)
        conn.commit()
    return after


@router.delete("/{department_id}")
def delete_department(
    department_id: str,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, bool]:
    require_role(user, "HR_MANAGER")
    with db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            before = _row(cur, department_id)
            cur.execute("select count(*) from ugaforce_hr_departments where parent_dept_id=%s", (department_id,))
            children = cur.fetchone()["count"]
            cur.execute("select count(*) from ugaforce_hr_employees where department_id=%s", (department_id,))
            employees = cur.fetchone()["count"]
            if children or employees:
                raise HTTPException(status_code=409, detail=f"Department is in use ({children} child departments, {employees} employees). Reassign them first.")
            cur.execute("delete from ugaforce_hr_departments where id=%s", (department_id,))
            audit(conn, user.get("employee_id"), "deleted", "department", department_id, before=before)
        conn.commit()
    return {"deleted": True}
