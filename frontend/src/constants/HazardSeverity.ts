export const HazardSeverity = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
export type HazardSeverity = (typeof HazardSeverity)[number];
export const HazardSeverityText: Record<HazardSeverity, string> = {
  LOW: "低危",
  MEDIUM: "一般",
  HIGH: "高危",
  CRITICAL: "特高",
};
export const HIGH_RISK: HazardSeverity[] = ["HIGH", "CRITICAL"];
