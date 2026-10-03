# 巡检结果在复核链中的状态：待提交 / 已提交 / 已复核 / 被退回重开
ReviewState = ["PENDING","SUBMITTED","REVIEWED","REOPENED"]
# 只有这些状态下检查项允许被修改或随提交覆盖
EDITABLE_REVIEW_STATES = ["PENDING","REOPENED"]
