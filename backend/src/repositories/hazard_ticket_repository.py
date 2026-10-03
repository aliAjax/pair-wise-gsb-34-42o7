from src.seed import seed
from src.constants.rectify_status import OPEN_RECTIFY_STATUSES
class HazardTicketRepository:
    def __init__(self):
        self.rows = seed["hazardTicket"]
    def find_all(self):
        return list(self.rows)
    def find_by_id(self, ticket_id):
        return next((row for row in self.rows if row["id"] == ticket_id), None)
    def find_open_by_result(self, result_id):
        return [row for row in self.rows if row["result_id"] == result_id and row["rectify_status"] in OPEN_RECTIFY_STATUSES]
    def find_open_by_device(self, device_id):
        return [row for row in self.rows if row["device_id"] == device_id and row["rectify_status"] in OPEN_RECTIFY_STATUSES]
    def find_by_submission(self, submission_id, result_id):
        return next((row for row in self.rows if row["submission_id"] == submission_id and row["result_id"] == result_id), None)
    def next_id(self):
        return max((row["id"] for row in self.rows), default=0) + 1
    def save(self, row):
        existing = self.find_by_id(row["id"])
        if existing:
            existing.update(row)
            return existing
        self.rows.append(row)
        return row
