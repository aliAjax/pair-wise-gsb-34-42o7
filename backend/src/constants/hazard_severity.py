class HazardRectifyStatus:
    """隐患整改单状态：OPEN 待整改；RECTIFIED 维保商已整改待复验；
    CLOSED 复验通过关闭；CANCELLED 关联检查项恢复正常或检查项废弃后撤销。"""

    OPEN = "OPEN"
    RECTIFIED = "RECTIFIED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    ALL = (OPEN, RECTIFIED, CLOSED, CANCELLED)
    OPEN_LIKE = (OPEN, RECTIFIED)


class HazardSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    ALL = (LOW, MEDIUM, HIGH, CRITICAL)
    HIGH_RISK = (HIGH, CRITICAL)
