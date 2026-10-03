import { getJson } from "./client";
import type { Building } from "../types/Building";

export function listBuildings(): Promise<Building[]> {
  return getJson<Building[]>("/api/buildings");
}
