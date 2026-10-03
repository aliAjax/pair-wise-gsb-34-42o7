class InspectionStatus:
    """巡检任务状态（任务级修订链）。

    PLANNED 已排期；IN_PROGRESS 巡检中；SUBMITTED 已提交待复核；
    REVIEWED 全部检查项复核通过；RETURNED 复核退回重开（仅被点名检查项放开）；
    OVERDUE 逾期。
    """

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    ALL = (PLANNED, IN_PROGRESS, SUBMITTED, REVIEWED, RETURNED, OVERDUE)


# 兼容旧引用
InspectionStatusList = list(InspectionStatus.ALL)
