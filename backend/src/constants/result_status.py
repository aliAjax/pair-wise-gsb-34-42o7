class ResultStatus:
    """检查项结论：待检 / 正常 / 异常。异常结果会触发隐患单。"""

    PENDING = "PENDING"
    NORMAL = "NORMAL"
    ABNORMAL = "ABNORMAL"
    ALL = (PENDING, NORMAL, ABNORMAL)
