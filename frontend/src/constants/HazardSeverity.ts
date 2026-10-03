export const HazardSeverity = ["LOW","MEDIUM","HIGH","CRITICAL"] as const;
export type HazardSeverity = (typeof HazardSeverity)[number];
export const HazardSeverityText: Record<HazardSeverity, string> = Object.fromEntries(HazardSeverity.map((value) => [value, value.replace(/_/g, " ")])) as Record<HazardSeverity, string>;
