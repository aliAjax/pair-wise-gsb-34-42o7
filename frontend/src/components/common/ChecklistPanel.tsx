import { StatusBadge } from "./StatusBadge";
import { HazardSeverityTag } from "./HazardSeverityTag";
import { ResultStatusText } from "../../constants/ResultStatus";
import type { FullInspectionTask } from "../../types/InspectionTask";
import type { InspectionResult } from "../../types/InspectionResult";

interface ChecklistPanelProps {
  task: FullInspectionTask;
  /** 可编辑检查项：DRAFT / SUBMITTED / RETURNED；REVIEWED 永远只读（复核保护） */
  editableResultStatusByCode?: Record<string, "PENDING" | "NORMAL" | "ABNORMAL">;
  onToggleResult?: (itemCode: string) => void;
  onNoteChange?: (itemCode: string, note: string) => void;
  readonly?: boolean;
  highlightCodes?: string[];
}

export function ChecklistPanel({
  task,
  editableResultStatusByCode,
  onToggleResult,
  onNoteChange,
  readonly = false,
  highlightCodes = [],
}: ChecklistPanelProps) {
  const resultByCode = new Map<string, InspectionResult>(
    task.results.map((r) => [r.item_code, r]),
  );

  return (
    <div className="checklist">
      <div className="row head">
        <span>检查项</span>
        <span>设备</span>
        <span>隐患等级</span>
        <span>结论</span>
        <span>复核状态</span>
      </div>
      {task.checklist_items
        .filter((item) => item.active)
        .map((item) => {
          const result = resultByCode.get(item.item_code);
          const reviewState = result?.review_state ?? "DRAFT";
          const protectedItem = reviewState === "REVIEWED";
          const draftStatus = editableResultStatusByCode?.[item.item_code];
          const displayStatus = draftStatus ?? result?.result_status ?? "PENDING";
          const highlighted = highlightCodes.includes(item.item_code);
          return (
            <div
              className={`row checklist-row${protectedItem ? " protected" : ""}${highlighted ? " returned" : ""}`}
              key={item.item_code}
            >
              <div>
                <strong>{item.title}</strong>
                <span className="muted small">{item.item_code}</span>
              </div>
              <span>#{item.device_id}</span>
              <HazardSeverityTag value={item.default_severity} />
              {readonly || protectedItem ? (
                <span>{ResultStatusText[displayStatus as keyof typeof ResultStatusText] ?? displayStatus}</span>
              ) : (
                <button
                  type="button"
                  className="inline-btn"
                  onClick={() => onToggleResult?.(item.item_code)}
                >
                  {ResultStatusText[displayStatus as keyof typeof ResultStatusText] ?? "待检"}（点击切换）
                </button>
              )}
              <StatusBadge value={reviewState} />
              {!readonly && !protectedItem && (
                <input
                  className="note-input"
                  placeholder="备注 / 测量值"
                  defaultValue={result?.note ?? ""}
                  onChange={(e) => onNoteChange?.(item.item_code, e.target.value)}
                />
              )}
              {protectedItem && <span className="lock-tag">已复核锁定</span>}
            </div>
          );
        })}
    </div>
  );
}
