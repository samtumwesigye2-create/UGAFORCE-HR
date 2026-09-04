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
BASE=Path(__file__).resolve().parent/'ugaforce_hr'
PAGES={'people':'people.html','recruiting':'recruiting.html','onboarding':'onboarding.html','time-attendance':'time_attendance.html','payroll':'payroll.html','performance':'performance.html','approvals':'approvals.html','analytics':'analytics.html','admin':'admin.html','offboarding':'offboarding.html'}
@app.get('/people',include_in_schema=False)
def people_page(): return FileResponse(BASE/PAGES['people'])
@app.get('/recruiting',include_in_schema=False)
def recruiting_page(): return FileResponse(BASE/PAGES['recruiting'])
@app.get('/onboarding',include_in_schema=False)
def onboarding_page(): return FileResponse(BASE/PAGES['onboarding'])
@app.get('/time-attendance',include_in_schema=False)
def time_attendance_page(): return FileResponse(BASE/PAGES['time-attendance'])
@app.get('/payroll',include_in_schema=False)
def payroll_page(): return FileResponse(BASE/PAGES['payroll'])
@app.get('/performance',include_in_schema=False)
def performance_page(): return FileResponse(BASE/PAGES['performance'])
@app.get('/approvals',include_in_schema=False)
def approvals_page(): return FileResponse(BASE/PAGES['approvals'])
@app.get('/analytics',include_in_schema=False)
def analytics_page(): return FileResponse(BASE/PAGES['analytics'])
@app.get('/admin',include_in_schema=False)
def admin_page(): return FileResponse(BASE/PAGES['admin'])
@app.get('/offboarding',include_in_schema=False)
def offboarding_page(): return FileResponse(BASE/PAGES['offboarding'])
@app.on_event('startup')
def announce_startup()->None:
 heartbeat('online',version=app.version,capability='people-rbac,recruiting-ats,onboarding,time-attendance-leave,payroll-benefits,performance-management,workflow-approvals,analytics,notifications,offboarding,security-readiness,password-lifecycle,people-ui,recruiting-ui,onboarding-ui,time-attendance-ui,payroll-ui,performance-ui,approvals-ui,analytics-ui,admin-ui,offboarding-ui')
