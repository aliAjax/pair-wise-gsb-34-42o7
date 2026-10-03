CREATE TABLE IF NOT EXISTS building (
  id INTEGER PRIMARY KEY,
  name TEXT,
  campus TEXT,
  floor_count TEXT,
  fire_grade TEXT,
  manager_id TEXT,
  address_code TEXT
);

CREATE TABLE IF NOT EXISTS fire_device (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  device_code TEXT,
  device_type TEXT,
  floor TEXT,
  location_desc TEXT,
  install_date TEXT,
  status TEXT,
  next_maintenance_at TEXT
);

CREATE TABLE IF NOT EXISTS inspection_task (
  id INTEGER PRIMARY KEY,
  building_id TEXT,
  inspector_id TEXT,
  plan_date TEXT,
  task_type TEXT,
  status TEXT,
  checklist_version TEXT,
  revision INTEGER DEFAULT 1,
  finished_at TEXT
);

CREATE TABLE IF NOT EXISTS inspection_result (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  device_id TEXT,
  item_code TEXT,
  result_status TEXT,
  measured_value TEXT,
  photo_url TEXT,
  note TEXT,
  submission_id TEXT,
  task_revision INTEGER DEFAULT 1,
  review_state TEXT DEFAULT 'PENDING'
);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id INTEGER PRIMARY KEY,
  result_id TEXT,
  device_id TEXT,
  item_code TEXT,
  severity TEXT,
  owner_id TEXT,
  deadline TEXT,
  rectify_status TEXT,
  rectify_note TEXT,
  submission_id TEXT,
  closed_at TEXT
);

-- 同一 submission_id 的提交只处理一次，断网重试幂等
CREATE UNIQUE INDEX IF NOT EXISTS idx_hazard_ticket_submission
  ON hazard_ticket (submission_id, result_id);

-- 旧修订提交留在冲突区，不覆盖已复核结果
CREATE TABLE IF NOT EXISTS conflict_entry (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  submission_id TEXT,
  revision INTEGER,
  current_revision INTEGER,
  payload TEXT,
  reason TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS submission (
  submission_id TEXT PRIMARY KEY,
  task_id TEXT,
  revision INTEGER,
  response TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY,
  actor TEXT,
  role TEXT,
  action TEXT,
  entity TEXT,
  entity_id TEXT,
  detail TEXT,
  created_at TEXT
);
