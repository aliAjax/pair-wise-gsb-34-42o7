import { useMemo } from "react";
import { EDITABLE_REVIEW_STATES } from "../constants/ReviewState";
import type { InspectionResult } from "../types/InspectionResult";

const FROZEN_TASK_STATUSES = ["SUBMITTED", "REVIEWED"];

export function useChecklistProgress(results: InspectionResult[] = [], taskStatus = "") {
  return useMemo(() => {
    const taskFrozen = FROZEN_TASK_STATUSES.includes(taskStatus);
    const isItemEditable = (row: InspectionResult) =>
      !taskFrozen && EDITABLE_REVIEW_STATES.includes(row.review_state as never);
    return {
      total: results.length,
      submitted: results.filter((row) => row.review_state === "SUBMITTED").length,
      reviewed: results.filter((row) => row.review_state === "REVIEWED").length,
      reopened: results.filter((row) => row.review_state === "REOPENED").length,
      editable: results.filter(isItemEditable).length,
      taskFrozen,
      isItemEditable
    };
  }, [results, taskStatus]);
}
