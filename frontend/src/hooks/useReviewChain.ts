import { useCallback, useState } from "react";
import { getFullTask, submitTask } from "../api/InspectionTask";
import { ApiError, newSubmissionId } from "../api/client";
import type { FullInspectionTask } from "../types/InspectionTask";
import type { SubmitItem, SubmissionOutcome } from "../types/InspectionResult";

/**
 * 复核链提交 hook：
 * - 提交前强制刷新完整任务，保证 base_revision 最新（断网恢复语义）；
 * - 同一草稿 clientSubmissionId 复用 → 重试只生成一张隐患单；
 * - STALE_TASK_REVISION / REVIEWED_PROTECTED 错误向调用方透传。
 */
export function useReviewChain(taskId: number) {
  const [task, setTask] = useState<FullInspectionTask | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastOutcome, setLastOutcome] = useState<SubmissionOutcome | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const full = await getFullTask(taskId);
      setTask(full);
      return full;
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  const submit = useCallback(
    async (items: SubmitItem[], clientSubmissionId?: string) => {
      setError(null);
      // 断网恢复：永远先从完整任务拿到当前修订号
      const full = task ?? (await refresh());
      const submissionId = clientSubmissionId ?? newSubmissionId();
      setLoading(true);
      try {
        const outcome = await submitTask(taskId, {
          client_submission_id: submissionId,
          base_revision: full.revision,
          items,
        });
        setLastOutcome(outcome);
        await refresh();
        return { outcome, submissionId };
      } catch (err) {
        if (err instanceof ApiError) setError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [task, taskId, refresh],
  );

  return { task, loading, lastOutcome, error, refresh, submit };
}
