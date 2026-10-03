from src.services.inspection_task_service import InspectionTaskService
service = InspectionTaskService()
def list_inspection_task():
    return service.list()
