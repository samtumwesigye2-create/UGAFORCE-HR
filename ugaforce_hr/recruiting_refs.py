from __future__ import annotations
import os
from typing import Any
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ugaforce_hr.security import current_user, require_role

DATABASE_URL=os.getenv('UGAFORCE_HR_DATABASE_URL') or os.getenv('DATABASE_URL')
router=APIRouter(prefix='/api/v1/recruiting/refs',tags=['UGAFORCE-HR Recruiting References'])

def db():
    if not DATABASE_URL: raise HTTPException(503,'HR database is not configured')
    return psycopg2.connect(DATABASE_URL,connect_timeout=5)

class PostingFromRequisition(BaseModel):
    requisition_number:str=Field(min_length=5,max_length=32)
    title:str=Field(min_length=2,max_length=180)
    description_md:str=Field(min_length=10)
    location:str|None=None
    remote_policy:str='onsite'

@router.get('/requisitions')
def requisitions(user:dict[str,Any]=Depends(current_user)):
    require_role(user,'MANAGER')
    with db() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""select r.id::text,r.requisition_number,r.title,r.status,r.headcount,r.employment_type,r.target_pay_min,r.target_pay_max,r.justification,r.created_at,r.approved_at,d.name department_name,concat(m.first_name,' ',m.last_name) hiring_manager from ugaforce_hr_job_requisitions r left join ugaforce_hr_departments d on d.id=r.department_id join ugaforce_hr_employees m on m.id=r.hiring_manager_id order by r.created_at desc""")
        rows=[dict(x) for x in cur.fetchall()]
    return {'count':len(rows),'results':rows}

@router.get('/requisitions/{requisition_number}')
def requisition(requisition_number:str,user:dict[str,Any]=Depends(current_user)):
    require_role(user,'MANAGER')
    with db() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""select r.id::text,r.requisition_number,r.title,r.status,r.headcount,r.employment_type,r.target_pay_min,r.target_pay_max,r.justification,d.name department_name,concat(m.first_name,' ',m.last_name) hiring_manager from ugaforce_hr_job_requisitions r left join ugaforce_hr_departments d on d.id=r.department_id join ugaforce_hr_employees m on m.id=r.hiring_manager_id where upper(r.requisition_number)=upper(%s)""",(requisition_number.strip(),))
        row=cur.fetchone()
    if not row: raise HTTPException(404,'Requisition ID not found')
    return dict(row)

@router.get('/postings')
def postings(user:dict[str,Any]=Depends(current_user)):
    require_role(user,'MANAGER')
    with db() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""select p.id::text,p.job_number,p.requisition_id::text,r.requisition_number,p.title,p.location,p.remote_policy,p.status,p.public_slug,p.published_at,p.created_at,d.name department_name from ugaforce_hr_job_postings p join ugaforce_hr_job_requisitions r on r.id=p.requisition_id left join ugaforce_hr_departments d on d.id=r.department_id order by p.created_at desc""")
        rows=[dict(x) for x in cur.fetchall()]
    return {'count':len(rows),'results':rows}

@router.post('/postings')
def create_posting(payload:PostingFromRequisition,user:dict[str,Any]=Depends(current_user)):
    require_role(user,'HR_SPECIALIST')
    with db() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('select id,status from ugaforce_hr_job_requisitions where upper(requisition_number)=upper(%s)',(payload.requisition_number.strip(),))
        req=cur.fetchone()
        if not req: raise HTTPException(404,'Requisition ID not found')
        if req['status']!='approved': raise HTTPException(409,'Requisition must be approved before a job posting can be created')
        cur.execute('select job_number from ugaforce_hr_job_postings where requisition_id=%s and status not in (\'closed\',\'cancelled\') order by created_at desc limit 1',(req['id'],))
        existing=cur.fetchone()
        if existing: raise HTTPException(409,f"An active job posting already exists for this requisition: {existing['job_number']}")
        cur.execute("""insert into ugaforce_hr_job_postings(requisition_id,title,description_md,location,remote_policy,public_slug) values(%s,%s,%s,%s,%s,%s) returning id::text,job_number,requisition_id::text,title,status,public_slug,created_at""",(req['id'],payload.title.strip(),payload.description_md,payload.location,payload.remote_policy,None))
        row=dict(cur.fetchone())
        for order,name,kind in [(1,'Resume Screen','screen'),(2,'Interview','interview'),(3,'Final Review','interview'),(4,'Offer','offer')]: cur.execute('insert into ugaforce_hr_pipeline_stages(job_posting_id,name,stage_order,stage_type) values(%s,%s,%s,%s)',(row['id'],name,order,kind))
        cur.execute("insert into ugaforce_hr_event_outbox(event_type,payload_json) values('job_posting.created',jsonb_build_object('job_posting_id',%s,'job_number',%s,'requisition_number',%s))",(row['id'],row['job_number'],payload.requisition_number.upper()))
        conn.commit()
    row['requisition_number']=payload.requisition_number.upper()
    return row
