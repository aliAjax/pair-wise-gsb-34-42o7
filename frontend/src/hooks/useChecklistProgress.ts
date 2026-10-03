import { useMemo } from "react";
import type { FullInspectionTask } from "../types/InspectionTask";

/**
 * 检查单进度：按复核状态统计。
 * total 取任务中 active 检查项；已完成 = REVIEWED 数量。
 */
export function useChecklistProgress(task: FullInspectionTask | null) {
  return useMemo(() => {
    if (!task) {
      return { total: 0, reviewed: 0, submitted: 0, returned: 0, draft: 0, percent: 0 };
    }
    const activeCodes = new Set(
      task.checklist_items.filter((item) => item.active).map((item) => item.item_code),
    );
    const activeResults = task.results.filter((r) => activeCodes.has(r.item_code));
    const reviewed = activeResults.filter((r) => r.review_state === "REVIEWED").length;
    const submitted = activeResults.filter((r) => r.review_state === "SUBMITTED").length;
    const returned = activeResults.filter((r) => r.review_state === "RETURNED").length;
    const draft = activeResults.filter((r) => r.review_state === "DRAFT").length;
    const total = activeCodes.size;
    return {
      total,
      reviewed,
      submitted,
      returned,
      draft,
      percent: total === 0 ? 0 : Math.round((reviewed / total) * 100),
    };
  }, [task]);
}
