import { HazardSeverityText } from "../../constants/HazardSeverity";

const TONE: Record<string, string> = {
  LOW: "severity-low",
  MEDIUM: "severity-medium",
  HIGH: "severity-high",
  CRITICAL: "severity-critical",
};

export function HazardSeverityTag({ value }: { value: string }) {
  return (
    <span className={`badge ${TONE[value] ?? ""}`}>
      {HazardSeverityText[value as keyof typeof HazardSeverityText] ?? value}
    </span>
  );
}
