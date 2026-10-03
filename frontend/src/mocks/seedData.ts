export const mockData = {
  "building": [
    {
      "id": 1,
      "name": "name 1",
      "campus": "campus 1",
      "floor_count": "floor count 1",
      "fire_grade": "fire grade 1",
      "manager_id": 1,
      "address_code": "address code 1"
    },
    {
      "id": 2,
      "name": "name 2",
      "campus": "campus 2",
      "floor_count": "floor count 2",
      "fire_grade": "fire grade 2",
      "manager_id": 2,
      "address_code": "address code 2"
    },
    {
      "id": 3,
      "name": "name 3",
      "campus": "campus 3",
      "floor_count": "floor count 3",
      "fire_grade": "fire grade 3",
      "manager_id": 3,
      "address_code": "address code 3"
    }
  ],
  "fireDevice": [
    {
      "id": 1,
      "building_id": 1,
      "device_code": "device code 1",
      "device_type": "HYDRANT",
      "floor": "floor 1",
      "location_desc": "location desc 1",
      "install_date": "2026-06-11T09:00:00Z",
      "status": "NORMAL",
      "next_maintenance_at": "2026-06-11T09:00:00Z",
      "open_hazard_count": 0,
      "open_high_hazard_count": 0
    },
    {
      "id": 2,
      "building_id": 2,
      "device_code": "device code 2",
      "device_type": "SMOKE_DETECTOR",
      "floor": "floor 2",
      "location_desc": "location desc 2",
      "install_date": "2026-06-12T09:00:00Z",
      "status": "ABNORMAL",
      "next_maintenance_at": "2026-06-12T09:00:00Z",
      "open_hazard_count": 1,
      "open_high_hazard_count": 1
    },
    {
      "id": 3,
      "building_id": 3,
      "device_code": "device code 3",
      "device_type": "SPRINKLER",
      "floor": "floor 3",
      "location_desc": "location desc 3",
      "install_date": "2026-06-13T09:00:00Z",
      "status": "NORMAL",
      "next_maintenance_at": "2026-06-13T09:00:00Z",
      "open_hazard_count": 0,
      "open_high_hazard_count": 0
    }
  ],
  "inspectionTask": [
    {
      "id": 1,
      "building_id": 1,
      "inspector_id": 1,
      "plan_date": "2026-06-11T09:00:00Z",
      "task_type": "HYDRANT",
      "status": "IN_PROGRESS",
      "checklist_version": "checklist version 1",
      "revision": 1,
      "finished_at": ""
    },
    {
      "id": 2,
      "building_id": 2,
      "inspector_id": 2,
      "plan_date": "2026-06-12T09:00:00Z",
      "task_type": "SMOKE_DETECTOR",
      "status": "SUBMITTED",
      "checklist_version": "checklist version 2",
      "revision": 1,
      "finished_at": "2026-06-12T09:00:00Z"
    },
    {
      "id": 3,
      "building_id": 3,
      "inspector_id": 3,
      "plan_date": "2026-06-13T09:00:00Z",
      "task_type": "SPRINKLER",
      "status": "PLANNED",
      "checklist_version": "checklist version 3",
      "revision": 1,
      "finished_at": ""
    }
  ],
  "inspectionResult": [
    {
      "id": 1,
      "task_id": 1,
      "device_id": 1,
      "item_code": "PRESSURE",
      "result_status": "ABNORMAL",
      "measured_value": "measured value 1",
      "photo_url": "/mock/photo_url-1.png",
      "note": "note 1",
      "submission_id": "",
      "task_revision": 1,
      "review_state": "PENDING"
    },
    {
      "id": 2,
      "task_id": 2,
      "device_id": 2,
      "item_code": "ALARM_TEST",
      "result_status": "ABNORMAL",
      "measured_value": "measured value 2",
      "photo_url": "/mock/photo_url-2.png",
      "note": "note 2",
      "submission_id": "seed-sub-2",
      "task_revision": 1,
      "review_state": "SUBMITTED"
    },
    {
      "id": 3,
      "task_id": 3,
      "device_id": 3,
      "item_code": "FLOW_TEST",
      "result_status": "NORMAL",
      "measured_value": "measured value 3",
      "photo_url": "/mock/photo_url-3.png",
      "note": "note 3",
      "submission_id": "",
      "task_revision": 1,
      "review_state": "PENDING"
    },
    {
      "id": 4,
      "task_id": 2,
      "device_id": 2,
      "item_code": "INDICATOR_LIGHT",
      "result_status": "ABNORMAL",
      "measured_value": "measured value 4",
      "photo_url": "/mock/photo_url-4.png",
      "note": "note 4",
      "submission_id": "seed-sub-2",
      "task_revision": 1,
      "review_state": "SUBMITTED"
    }
  ],
  "hazardTicket": [
    {
      "id": 1,
      "result_id": 2,
      "device_id": 2,
      "item_code": "ALARM_TEST",
      "severity": "HIGH",
      "owner_id": 1,
      "deadline": "2026-10-10T09:00:00Z",
      "rectify_status": "OPEN",
      "rectify_note": "",
      "submission_id": "seed-sub-2",
      "closed_at": ""
    },
    {
      "id": 2,
      "result_id": 4,
      "device_id": 2,
      "item_code": "INDICATOR_LIGHT",
      "severity": "LOW",
      "owner_id": 2,
      "deadline": "2026-09-10T09:00:00Z",
      "rectify_status": "CLOSED",
      "rectify_note": "rectify note 2",
      "submission_id": "seed-sub-2",
      "closed_at": "2026-09-01T09:00:00Z"
    }
  ]
} as const;
