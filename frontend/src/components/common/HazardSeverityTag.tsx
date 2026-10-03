import { StatusBadge } from "./StatusBadge";
import { formatRisk } from "../../utils/formatters";

export function HazardSeverityTag({ value }: { value: string }) {
  return <span className="severity"><StatusBadge value={value} />{formatRisk(value)}</span>;
}
