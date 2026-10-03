from src.services.report_service import ReportService
service = ReportService()
def compliance_report():
    return service.compliance()
