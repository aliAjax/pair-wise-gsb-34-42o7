/**
 * 本地种子数据（仅离线演示用，业务数据全部来自后端 /api）。
 * 结构与后端 GET /api/inspection-tasks/{id}/full 等接口保持一致。
 */

export const mockData = {
  buildings: [
    { id: 1, name: "A 座研发楼", campus: "江北科技园", floor_count: 12 },
  ],
  fireDevices: [
    {
      id: 1,
      building_id: 1,
      device_code: "FE-HYDRANT-001",
      device_type: "HYDRANT",
      floor: "1",
      location_desc: "大堂东侧消火栓",
      install_date: "2024-05-01",
      status: "HIGH_HAZARD_BLOCKED",
      base_status: "NORMAL",
      next_maintenance_at: "2026-11-01",
      owner_id: 2,
    },
  ],
  inspectionTasks: [
    {
      id: 1,
      building_id: 1,
      inspector_id: 1,
      plan_date: "2026-10-03",
      task_type: "ROUTINE",
      status: "SUBMITTED",
      checklist_version: "v1",
      finished_at: null,
      revision: 2,
      checklist_items: [
        { item_code: "CHK-PRESSURE-1F", device_id: 1, title: "消火栓静水压力", default_severity: "HIGH", active: true },
      ],
    },
  ],
  inspectionResults: [
    {
      id: 1,
      task_id: 1,
      device_id: 1,
      item_code: "CHK-PRESSURE-1F",
      result_status: "ABNORMAL",
      measured_value: "0.2MPa",
      photo_url: "",
      note: "压力不足",
      review_state: "SUBMITTED",
      severity_hint: "HIGH",
      revision: 2,
      submitted_at: "2026-10-03T02:00:00Z",
      reviewed_at: null,
      returned_at: null,
    },
  ],
  hazardTickets: [
    {
      id: 1,
      result_id: 1,
      device_id: 1,
      task_id: 1,
      severity: "HIGH",
      owner_id: 2,
      deadline: "2026-10-10",
      rectify_status: "OPEN",
      rectify_note: "",
      closed_at: null,
      created_at: "2026-10-03T02:00:00Z",
    },
  ],
};
