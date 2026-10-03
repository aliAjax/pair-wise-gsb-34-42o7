from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.constants.rectify_status import OPEN_RECTIFY_STATUSES
from src.constants.log_templates import LOG_TEMPLATES
from src.utils.errors import BusinessError
from src.utils.formatters import now_iso

class HazardTicketService:
    """隐患整改单：同一提交幂等去重，关单后触发设备状态重算。"""
    def __init__(self):
        self.repo = HazardTicketRepository()
    def list(self):
        return self.repo.find_all()
    def get(self, ticket_id):
        return self.repo.find_by_id(ticket_id)
    def ensure_for_result(self, result, severity, submission_id, audit=None, actor=None):
        """同一 submission_id + result_id 的未关闭隐患单只生成一张，重试安全；
        旧单已关闭则派生新提交号另开新单，保留关单历史。"""
        existing = self.repo.find_by_submission(submission_id, result["id"])
        if existing and existing["rectify_status"] in OPEN_RECTIFY_STATUSES:
            if audit:
                audit.record(LOG_TEMPLATES["HazardTicket"][5], actor or {}, "HazardTicket", existing["id"],
                             f"dedup submission={submission_id}")
            return existing
        if existing:
            siblings = [t for t in self.repo.find_all() if t["result_id"] == result["id"]]
            submission_id = f"{submission_id}-re{len(siblings)}"
        row = {
            "id": self.repo.next_id(),
            "result_id": result["id"],
            "device_id": result["device_id"],
            "item_code": result["item_code"],
            "severity": severity,
            "owner_id": 0,
            "deadline": "",
            "rectify_status": "OPEN",
            "rectify_note": "",
            "submission_id": submission_id,
            "closed_at": ""
        }
        self.repo.save(row)
        if audit:
            audit.record(LOG_TEMPLATES["HazardTicket"][0], actor or {}, "HazardTicket", row["id"],
                         f"severity={severity} result={result['id']}")
        return row
    def sync_for_result(self, result, severity, submission_id, audit=None, actor=None):
        """检查项修改后重算：异常确保有未关闭隐患单，恢复正常则自动关闭。"""
        open_tickets = self.repo.find_open_by_result(result["id"])
        if result["result_status"] == "ABNORMAL":
            if open_tickets:
                return open_tickets[0]
            return self.ensure_for_result(result, severity, submission_id, audit, actor)
        for ticket in open_tickets:
            ticket["rectify_status"] = "CLOSED"
            ticket["rectify_note"] = "检查项修正为正常，系统自动关闭"
            ticket["closed_at"] = now_iso()
            self.repo.save(ticket)
            if audit:
                audit.record(LOG_TEMPLATES["HazardTicket"][4], actor or {}, "HazardTicket", ticket["id"],
                             "auto-close by result fix")
        return None
    def close(self, ticket_id, rectify_note, audit=None, actor=None):
        ticket = self.repo.find_by_id(ticket_id)
        if not ticket:
            raise BusinessError("NOT_FOUND", 404)
        if ticket["rectify_status"] == "CLOSED":
            return ticket
        ticket["rectify_status"] = "CLOSED"
        ticket["rectify_note"] = rectify_note
        ticket["closed_at"] = now_iso()
        self.repo.save(ticket)
        if audit:
            audit.record(LOG_TEMPLATES["HazardTicket"][4], actor or {}, "HazardTicket", ticket_id,
                         rectify_note)
        return ticket
