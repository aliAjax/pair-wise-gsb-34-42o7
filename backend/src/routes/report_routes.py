from fastapi import APIRouter, Depends
from src.controllers.report_controller import compliance_report
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/reports", tags=["Report"])
router.get("/compliance", dependencies=[Depends(allow_roles("AUDITOR", "ADMIN", "INSPECTOR", "MAINTAINER"))])(compliance_report)
