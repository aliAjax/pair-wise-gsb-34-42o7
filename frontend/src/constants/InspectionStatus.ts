export const InspectionStatus = ["PLANNED","IN_PROGRESS","SUBMITTED","REVIEWED","OVERDUE"] as const;
export type InspectionStatus = (typeof InspectionStatus)[number];
export const InspectionStatusText: Record<InspectionStatus, string> = Object.fromEntries(InspectionStatus.map((value) => [value, value.replace(/_/g, " ")])) as Record<InspectionStatus, string>;
