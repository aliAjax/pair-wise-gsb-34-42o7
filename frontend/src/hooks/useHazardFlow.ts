import { useCallback, useState } from "react";
import {
  assignHazard,
  rectifyHazard,
  verifyHazard,
} from "../api/HazardTicket";
import { ApiError } from "../api/client";
import type { HazardTicket } from "../types/HazardTicket";

/** 隐患整改流：派单(主管) → 整改(维保商) → 复验关闭/退回(主管)。 */
export function useHazardFlow(onChanged?: () => void) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const run = useCallback(
    async (action: () => Promise<HazardTicket>) => {
      setLoading(true);
      setError("");
      try {
        const result = await action();
        onChanged?.();
        return result;
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "操作失败";
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [onChanged],
  );

  return {
    loading,
    error,
    assign: (hazardId: number, ownerId: number) =>
      run(() => assignHazard(hazardId, ownerId)),
    rectify: (hazardId: number, note: string) =>
      run(() => rectifyHazard(hazardId, note)),
    verify: (hazardId: number, approved: boolean, note: string) =>
      run(() => verifyHazard(hazardId, approved, note)),
  };
}
