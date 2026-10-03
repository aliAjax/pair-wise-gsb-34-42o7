import { StatusBadge } from "./StatusBadge";
import { ReviewStateText } from "../../constants/ReviewState";
import type { InspectionResult } from "../../types/InspectionResult";

interface Props {
  results: InspectionResult[];
  isItemEditable: (row: InspectionResult) => boolean;
  drafts: Record<string, { result_status: string; severity: string }>;
  onDraftChange: (itemCode: string, patch: { result_status?: string; severity?: string }) => void;
}

// 检查项面板：被退回点名的项可改，其余项只读保持原状
export function ChecklistPanel({ results, isItemEditable, drafts, onDraftChange }: Props) {
  if (results.length === 0) return <div className="empty">暂无检查项</div>;
  return <div className="table">
    {results.map((row) => {
      const editable = isItemEditable(row);
      const draft = drafts[row.item_code];
      return <article key={row.id} className="row checklist-row">
        <strong>{row.item_code}</strong>
        <StatusBadge value={row.review_state} />
        <span>{ReviewStateText[row.review_state as keyof typeof ReviewStateText] ?? row.review_state}</span>
        {editable ? (
          <>
            <select
              value={draft?.result_status ?? row.result_status}
              onChange={(e) => onDraftChange(row.item_code, { result_status: e.target.value })}>
              <option value="NORMAL">正常</option>
              <option value="ABNORMAL">异常</option>
            </select>
            <select
              value={draft?.severity ?? "MEDIUM"}
              onChange={(e) => onDraftChange(row.item_code, { severity: e.target.value })}>
              <option value="LOW">低</option>
              <option value="MEDIUM">中</option>
              <option value="HIGH">高</option>
              <option value="CRITICAL">严重</option>
            </select>
          </>
        ) : (
          <span>{row.result_status === "ABNORMAL" ? "异常" : "正常"}</span>
        )}
      </article>;
    })}
  </div>;
}
