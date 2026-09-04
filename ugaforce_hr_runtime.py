from __future__ import annotations
from pathlib import Path
from fastapi.responses import FileResponse
from ugaforce_hr_app import app
from ugaforce_hr.completion import router as completion_router
from ugaforce_hr.onboarding import router as onboarding_router
from ugaforce_hr.password_lifecycle import router as password_lifecycle_router
from ugaforce_hr.payroll import router as payroll_router
from ugaforce_hr.people_admin import router as people_admin_router
from ugaforce_hr.performance import router as performance_router
from ugaforce_hr.recruiting import public_router as careers_router, router as recruiting_router
from ugaforce_hr.time_attendance import router as time_attendance_router
from ugaforce_hr.workflow_analytics import router as workflow_analytics_router
from ugaforce_hr.ugacore_client import heartbeat
for r in (people_admin_router,recruiting_router,careers_router,onboarding_router,time_attendance_router,payroll_router,performance_router,workflow_analytics_router,completion_router,password_lifecycle_router): app.include_router(r)

BASE = Path(__file__).resolve().parent / 'ugaforce_hr'
PEOPLE_PAGE = BASE / 'people.html'
RECRUITING_PAGE = BASE / 'recruiting.html'
ONBOARDING_PAGE = BASE / 'onboarding.html'
TIME_PAGE = BASE / 'time_attendance.html'
PAYROLL_PAGE = BASE / 'payroll.html'

@app.get('/people', include_in_schema=False)
def people_page(): return FileResponse(PEOPLE_PAGE)
@app.get('/recruiting', include_in_schema=False)
def recruiting_page(): return FileResponse(RECRUITING_PAGE)
@app.get('/onboarding', include_in_schema=False)
def onboarding_page(): return FileResponse(ONBOARDING_PAGE)
@app.get('/time-attendance', include_in_schema=False)
def time_attendance_page(): return FileResponse(TIME_PAGE)
@app.get('/payroll', include_in_schema=False)
def payroll_page(): return FileResponse(PAYROLL_PAGE)

@app.on_event('startup')
def announce_startup()->None:
 heartbeat('online',version=app.version,capability='people-rbac,recruiting-ats,onboarding,time-attendance-leave,payroll-benefits,performance-management,workflow-approvals,analytics,notifications,offboarding,security-readiness,password-lifecycle,people-ui,recruiting-ui,onboarding-ui,time-attendance-ui,payroll-ui')
