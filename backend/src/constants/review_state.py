class ReviewState:
    """单条检查项的复核链状态。

    DRAFT 巡检员暂存；SUBMITTED 已提交待复核；REVIEWED 已复核（受保护，
    不可被旧提交覆盖）；RETURNED 被复核退回，仅该检查项重新放开；
    DISCARDED 因检查项被修改而废弃，保留记录用于追溯。
    """

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"
    RETURNED = "RETURNED"
    DISCARDED = "DISCARDED"
    ALL = (DRAFT, SUBMITTED, REVIEWED, RETURNED, DISCARDED)


class ReviewDecision:
    APPROVE = "APPROVE"
    RETURN = "RETURN"
