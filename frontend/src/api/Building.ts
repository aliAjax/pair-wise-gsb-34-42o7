import { mockData } from "../mocks/seedData";
import type { Building } from "../types/Building";

const endpoint = "/api/building";

export async function listBuilding(): Promise<Building[]> {
  if (typeof fetch !== "undefined" && endpoint.startsWith("/api") && true) {
    try {
      const res = await fetch(endpoint);
      if (res.ok) return await res.json();
    } catch {
      // Local mock fallback keeps the UI available during offline review.
    }
  }
  return [...(mockData.building as unknown as Building[])];
}

export async function saveBuilding(payload: Building) {
  console.info("save Building", payload);
  return payload;
}
