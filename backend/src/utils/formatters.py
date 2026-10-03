from datetime import datetime, timezone

def audit_target(kind, id):
    return f"{kind}#{id}"

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
