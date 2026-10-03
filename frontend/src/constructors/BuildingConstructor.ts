import type { Building } from "../types/Building";

export const createDefaultBuilding = (overrides: Partial<Building> = {}): Building => ({
  id: 1 as never,
  name: "name 1" as never,
  campus: "campus 1" as never,
  floor_count: "floor count 1" as never,
  fire_grade: "fire grade 1" as never,
  manager_id: 1 as never,
  address_code: "address code 1" as never,
  ...overrides
});

export const createBuildingForm = createDefaultBuilding;
export const createBuildingResponse = createDefaultBuilding;
