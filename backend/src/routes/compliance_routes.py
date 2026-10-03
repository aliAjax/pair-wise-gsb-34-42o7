from fastapi import APIRouter

from src.controllers.compliance_controller import (
    dashboard_controller,
    list_audit_logs_controller,
    monthly_report_controller,
)

router = APIRouter(prefix="/api", tags=["Compliance"])

router.get("/dashboard")(dashboard_controller)
router.get("/reports/monthly")(monthly_report_controller)
router.get("/audit-logs")(list_audit_logs_controller)
