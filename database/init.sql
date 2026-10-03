-- 消防设施巡检维保平台 - 复核链结构（PostgreSQL 15）
-- 后端 SQLAlchemy create_all 使用 IF NOT EXISTS，可与本脚本共存。

CREATE TABLE IF NOT EXISTS building (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  campus VARCHAR(128) NOT NULL DEFAULT '',
  floor_count INTEGER NOT NULL DEFAULT 1,
  fire_grade VARCHAR(32) NOT NULL DEFAULT 'GRADE_2',
  manager_id BIGINT,
  address_code VARCHAR(64) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS fire_device (
  id BIGSERIAL PRIMARY KEY,
  building_id BIGINT NOT NULL,
  device_code VARCHAR(64) NOT NULL UNIQUE,
  device_type VARCHAR(32) NOT NULL,
  floor VARCHAR(16) NOT NULL DEFAULT '1',
  location_desc VARCHAR(255) NOT NULL DEFAULT '',
  install_date VARCHAR(32) NOT NULL DEFAULT '',
  status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  next_maintenance_at VARCHAR(32),
  owner_id BIGINT
);
CREATE INDEX IF NOT EXISTS ix_fire_device_building_id ON fire_device(building_id);

CREATE TABLE IF NOT EXISTS user_account (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  display_name VARCHAR(64) NOT NULL DEFAULT '',
  role VARCHAR(32) NOT NULL DEFAULT 'INSPECTOR',
  password_sha256 VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS inspection_task (
  id BIGSERIAL PRIMARY KEY,
  building_id BIGINT NOT NULL,
  inspector_id BIGINT NOT NULL,
  plan_date VARCHAR(32) NOT NULL,
  task_type VARCHAR(32) NOT NULL DEFAULT 'ROUTINE',
  status VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
  checklist_version VARCHAR(32) NOT NULL DEFAULT 'v1',
  finished_at VARCHAR(32),
  revision INTEGER NOT NULL DEFAULT 1,
  checklist_items JSONB NOT NULL DEFAULT '[]'::jsonb,
  note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS ix_inspection_task_building_id ON inspection_task(building_id);
CREATE INDEX IF NOT EXISTS ix_inspection_task_inspector_id ON inspection_task(inspector_id);

CREATE TABLE IF NOT EXISTS inspection_result (
  id BIGSERIAL PRIMARY KEY,
  task_id BIGINT NOT NULL,
  device_id BIGINT NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  result_status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  measured_value VARCHAR(255) NOT NULL DEFAULT '',
  photo_url VARCHAR(255) NOT NULL DEFAULT '',
  note TEXT NOT NULL DEFAULT '',
  review_state VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
  severity_hint VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
  revision INTEGER NOT NULL DEFAULT 1,
  submitted_at VARCHAR(32),
  reviewed_at VARCHAR(32),
  returned_at VARCHAR(32)
);
CREATE INDEX IF NOT EXISTS ix_inspection_result_task_id ON inspection_result(task_id);
CREATE INDEX IF NOT EXISTS ix_inspection_result_device_id ON inspection_result(device_id);
-- 在途（非 DISCARDED）结果同一任务同一检查项唯一，DISCARDED 历史保留可追溯
CREATE UNIQUE INDEX IF NOT EXISTS uq_result_active_item
  ON inspection_result(task_id, item_code)
  WHERE review_state <> 'DISCARDED';

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id BIGSERIAL PRIMARY KEY,
  result_id BIGINT NOT NULL,
  device_id BIGINT NOT NULL,
  task_id BIGINT NOT NULL,
  severity VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
  owner_id BIGINT NOT NULL DEFAULT 0,
  deadline VARCHAR(32) NOT NULL DEFAULT '',
  rectify_status VARCHAR(16) NOT NULL DEFAULT 'OPEN',
  rectify_note TEXT NOT NULL DEFAULT '',
  closed_at VARCHAR(32),
  created_at VARCHAR(32),
  active_key VARCHAR(16)
);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_result_id ON hazard_ticket(result_id);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_device_id ON hazard_ticket(device_id);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_task_id ON hazard_ticket(task_id);
-- 一条检查结果至多一张在途隐患单（同一提交重试不重复生成）
CREATE UNIQUE INDEX IF NOT EXISTS uq_hazard_open_per_result
  ON hazard_ticket(result_id)
  WHERE active_key = 'ACTIVE';

CREATE TABLE IF NOT EXISTS submission_record (
  id BIGSERIAL PRIMARY KEY,
  task_id BIGINT NOT NULL,
  client_submission_id VARCHAR(128) NOT NULL,
  inspector_id BIGINT NOT NULL,
  base_revision INTEGER NOT NULL,
  outcome_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at VARCHAR(32) NOT NULL,
  CONSTRAINT uq_submission_idempotency UNIQUE (task_id, client_submission_id)
);

CREATE TABLE IF NOT EXISTS submission_conflict (
  id BIGSERIAL PRIMARY KEY,
  task_id BIGINT NOT NULL,
  client_submission_id VARCHAR(128) NOT NULL,
  base_revision INTEGER NOT NULL,
  current_revision INTEGER NOT NULL,
  reason VARCHAR(32) NOT NULL,
  payload_preview TEXT NOT NULL DEFAULT '',
  created_at VARCHAR(32) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_submission_conflict_task_id ON submission_conflict(task_id);
CREATE INDEX IF NOT EXISTS ix_submission_conflict_reason ON submission_conflict(reason);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  actor_id BIGINT NOT NULL,
  actor_role VARCHAR(32) NOT NULL,
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id VARCHAR(64) NOT NULL,
  detail TEXT NOT NULL DEFAULT '',
  created_at VARCHAR(32) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_log_actor_id ON audit_log(actor_id);
CREATE INDEX IF NOT EXISTS ix_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS ix_audit_log_target_id ON audit_log(target_id);
CREATE INDEX IF NOT EXISTS ix_audit_log_created_at ON audit_log(created_at);
