import { ReviewStateText } from "../../constants/ReviewState";
import { HazardRectifyStatusText } from "../../constants/HazardRectifyStatus";
import { DeviceComplianceText } from "../../constants/DeviceCompliance";
import { InspectionStatusText } from "../../constants/InspectionStatus";
import { ResultStatusText } from "../../constants/ResultStatus";

const TEXT_MAPS: Record<string, Record<string, string>> = {
  DRAFT: ReviewStateText,
  SUBMITTED: { ...InspectionStatusText, ...ReviewStateText, ...HazardRectifyStatusText },
  REVIEWED: ReviewStateText,
  RETURNED: { ...ReviewStateText, ...InspectionStatusText },
  DISCARDED: ReviewStateText,
  PENDING: { ...ResultStatusText, ...HazardRectifyStatusText },
  NORMAL: ResultStatusText,
  ABNORMAL: ResultStatusText,
  OPEN: HazardRectifyStatusText,
  RECTIFIED: HazardRectifyStatusText,
  CLOSED: HazardRectifyStatusText,
  CANCELLED: HazardRectifyStatusText,
  ACTIVE: DeviceComplianceText,
  HAZARD_PENDING: DeviceComplianceText,
  HIGH_HAZARD_BLOCKED: DeviceComplianceText,
  MAINTENANCE: DeviceComplianceText,
  RETIRED: DeviceComplianceText,
  PLANNED: InspectionStatusText,
  IN_PROGRESS: InspectionStatusText,
  OVERDUE: InspectionStatusText,
};

const DANGER = new Set(["ABNORMAL", "OPEN", "OVERDUE", "HIGH_HAZARD_BLOCKED", "RETURNED"]);
const SUCCESS = new Set(["NORMAL", "REVIEWED", "CLOSED", "ACTIVE"]);

export function StatusBadge({ value }: { value: string }) {
  const text = TEXT_MAPS[value]?.[value] ?? String(value).replace(/_/g, " ");
  const tone = DANGER.has(value) ? " danger" : SUCCESS.has(value) ? " success" : "";
  return <span className={`badge${tone}`}>{text}</span>;
}
