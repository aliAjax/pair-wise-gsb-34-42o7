from pydantic import BaseModel

HazardTicketPayload = dict

class CloseHazardPayload(BaseModel):
    rectify_note: str = ""
