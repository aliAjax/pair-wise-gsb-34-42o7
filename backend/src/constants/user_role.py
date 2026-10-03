class UserRole:
    """平台角色：巡检员 / 维保商 / 物业主管 / 审计员。"""

    INSPECTOR = "INSPECTOR"
    MAINTAINER = "MAINTAINER"
    SUPERVISOR = "SUPERVISOR"
    AUDITOR = "AUDITOR"
    ALL = (INSPECTOR, MAINTAINER, SUPERVISOR, AUDITOR)


class UserRoleText:
    INSPECTOR = "巡检员"
    MAINTAINER = "维保商"
    SUPERVISOR = "物业主管"
    AUDITOR = "审计员"
