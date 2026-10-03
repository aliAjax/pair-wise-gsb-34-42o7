from src.services.inspection_result_service import InspectionResultService
service = InspectionResultService()
def list_inspection_result():
    return service.list()
