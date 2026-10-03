# 消防设施巡检维保平台（fire-inspect）

面向园区和物业公司的消防设备巡检、隐患整改、维保计划与合规台账系统。本版本将**巡检任务 → 巡检结果 → 隐患整改单 → 消防设备台账**接成一条带修订号与复核保护的**复核链**。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

- 前端：<http://localhost:20103>
- 后端健康检查：<http://localhost:21103/health>
- API 文档：<http://localhost:21103/docs>

种子账号（角色权限相互隔离）：

| 角色 | 用户名 | 密码 | 能做什么 |
|---|---|---|---|
| 巡检员 | `inspector` | `inspect123` | 领取任务、提交/续传巡检结果 |
| 维保商 | `maintainer` | `maintain123` | 隐患整改提交 |
| 物业主管 | `supervisor` | `super123` | 复核、检查项修改、派单、复验关闭 |
| 审计员 | `auditor` | `audit123` | 全局只读、查审计日志 |

## 复核链：这条链如何解决“各改各的”

1. **提交带任务修订号（乐观锁）**
   任务有 `revision`，检查项修改、复核退回都会自增。提交体必须带 `base_revision`：
   - 与当前修订一致：受理，并把任务修订号再 +1；
   - 过期：**整包落入提交冲突区**（`submission_conflict`），返回 `409 STALE_TASK_REVISION`，**不覆盖任何现有结果**。“另一台设备送回旧内容”会停在这里。
2. **已复核结果受保护**
   即使修订号最新，`review_state=REVIEWED` 的检查项也逐项拒绝（冲突原因 `REVIEWED_PROTECTED`），其余检查项正常受理（部分受理 PARTIAL）。
3. **同一提交重试只生成一张隐患单**
   提交必须带客户端幂等键 `client_submission_id`（存 `submission_record`，`(task_id, client_submission_id)` 唯一）；重试直接回放首次结果。引擎与数据库（`uq_hazard_open_per_result` 部分唯一索引）双保险保证一个检查结果至多一张在途隐患单。
4. **检查项修改后隐患与设备状态重算**
   `PATCH /api/inspection-tasks/{id}/checklist` 新增检查项（PENDING/DRAFT）、删除检查项（结果置 DISCARDED、在途隐患单 CANCELLED，记录保留）、改默认等级（在途隐患单等级重判），任务修订号自增。
5. **复核退回只放开被点名的检查项**
   `POST /reviews` 的 `item_codes` 决定影响面；未点名结果保持原 `review_state`，任务状态按检查项聚合。全部复核后也可以对单项“重开”（REVIEWED→RETURNED）。
6. **未关闭高危隐患一票否决**
   设备台账 `status` 是由未关闭隐患实时重算的合规状态：存在 HIGH/CRITICAL 在途隐患时为 `HIGH_HAZARD_BLOCKED`，台账与 `/api/reports/monthly` 都不会显示“正常”；维保商整改后仍封锁，主管复验关闭才恢复 `ACTIVE`。
7. **断网恢复从完整任务继续**
   `GET /api/inspection-tasks/{id}/full` 返回修订号 + 完整检查单 + 全部结果；前端 `useReviewChain` 提交前强制刷新，失败不伪造成功，恢复后用原 `client_submission_id` 续传。
8. **重开后仍可追溯**
   DISCARDED 结果、CANCELLED 隐患单与全部 `audit_log` 均为软状态保留，可按目标对象在 `/api/audit-logs` 追溯。

### 接口流程示例

```bash
# 1) 登录拿 token
curl -sX POST http://localhost:21103/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"inspector","password":"inspect123"}'

# 2) 断网恢复：拉完整任务（记录返回的 revision）
curl -s http://localhost:21103/api/inspection-tasks/1/full -H "Authorization: Bearer <token>"

# 3) 提交（base_revision 必须等于当前 revision；重试保持同一 client_submission_id）
curl -sX POST http://localhost:21103/api/inspection-tasks/1/submissions \
  -H "Authorization: Bearer <inspector-token>" -H 'Content-Type: application/json' \
  -d '{"client_submission_id":"7b1f...","base_revision":1,"items":[
        {"item_code":"CHK-PRESSURE-1F","result_status":"ABNORMAL","measured_value":"0.2MPa"}]}'

# 4) 主管逐项复核（退回只点名）
curl -sX POST http://localhost:21103/api/inspection-tasks/1/reviews \
  -H "Authorization: Bearer <supervisor-token>" -H 'Content-Type: application/json' \
  -d '{"decision":"RETURN","item_codes":["CHK-PRESSURE-1F"],"note":"照片不清"}'

# 5) 维保商整改 → 主管复验关闭
curl -sX POST http://localhost:21103/api/hazards/1/rectify \
  -H "Authorization: Bearer <maintainer-token>" -H 'Content-Type: application/json' \
  -d '{"rectify_note":"已更换水带并复测"}'
curl -sX POST http://localhost:21103/api/hazards/1/verify \
  -H "Authorization: Bearer <supervisor-token>" -H 'Content-Type: application/json' \
  -d '{"approved":true,"note":"复验合格"}'
```

## 本地开发方式

- 后端（Python 3.11 + FastAPI + SQLAlchemy 2.0）：

  ```bash
  cd backend
  pip install -r requirements.txt
  # 无 PostgreSQL 时可用 SQLite 跑：
  DATABASE_URL='sqlite:///./fire_inspect.db' uvicorn src.main:app --reload --port 8000
  ```

- 复核链规则测试为**零第三方依赖**的纯 Python（CI/无网络环境可直接跑）：

  ```bash
  cd backend
  python3 tests/test_review_chain.py    # 领域引擎 10 个场景
  python3 tests/test_chain_service.py   # 服务编排（幂等/冲突/重开/权限）5 个场景
  ```

- 前端（React 18 + TypeScript + Vite）：

  ```bash
  cd frontend && npm install && npm run dev
  ```

  前端统一请求 `/api`，由 Nginx 反代到 `http://backend:8000/`，不硬编码 localhost。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI + Zustand |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 + python-jose(JWT) |
| 数据库 | PostgreSQL 15（部分唯一索引 + JSONB），测试可换 SQLite |
| 部署 | Docker Compose（db healthcheck / 后端健康依赖 / 命名卷） |

## 项目目录结构

```text
backend/src/
├── domain/                 # 复核链纯领域层（零三方依赖，可直接单测）
│   ├── review_chain_engine.py   # 提交/冲突/复核/检查项修改/隐患联动核心
│   ├── compliance.py            # 设备合规状态重算（高危一票否决）
│   ├── records.py / errors.py
├── routes/ controllers/ services/ repositories/   # 四层严格分离
├── models/                 # SQLAlchemy 2.0 ORM（含部分唯一索引）
├── middlewares/            # auth/rate_limit/audit_log/request_logger/error_handler
├── constants/              # 枚举、错误码、错误消息、日志模板
├── constructors/           # DTO 构造器、ORM↔领域映射器
├── types/                  # Pydantic 请求模型
└── config/                 # settings、database
backend/tests/              # test_review_chain.py / test_chain_service.py
frontend/src/
├── api/ client.ts          # 统一 /api 封装、JWT、幂等键、错误码透传
├── stores/                 # Zustand（含 AuthStore）
├── hooks/                  # useReviewChain / useChecklistProgress / useHazardFlow / usePagination
├── pages/                  # Dashboard/Devices/Tasks/Hazards/Reports/Audit/Login
├── components/common/      # StatusBadge/ChecklistPanel/HazardSeverityTag 等
├── constants/ types/ constructors/ router/ utils/ mocks/
database/init.sql           # PostgreSQL 15 全量结构（与 ORM 对齐）
```

## 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `fire-inspect` | Compose 项目/容器名前缀 |
| `FRONTEND_PORT` | `20103` | 前端宿主端口 |
| `BACKEND_PORT` | `21103` | 后端宿主端口（容器内 8000） |
| `DB_PORT` | `54320` | PostgreSQL 宿主端口 |
| `DB_NAME / DB_USER / DB_PASSWORD` | `app_db/app_user/app_password` | 数据库凭据 |
| `JWT_SECRET` | `local-dev-secret` | JWT 签名密钥（生产请覆盖） |
| `JWT_EXPIRE_MINUTES` | `480` | Token 有效期 |
| `RATE_LIMIT_PER_MINUTE` | `120` | 每 IP+路径限流 |
| `SEED_ON_START` | `true` | 启动自动建表并写入种子数据 |
| `DATABASE_URL` | 空（用 PG 拼接串） | 设置后可切 SQLite 等其他库 |

## Docker 部署说明

- 顶层 `name: fire-inspect`，容器名统一 `${COMPOSE_PROJECT_NAME:-fire-inspect}-*`；不写 `version:`。
- 数据库使用命名卷 `db_data`，不绑定挂载（中文目录名也安全）。
- db 配置 `pg_isready` healthcheck，backend `depends_on: condition: service_healthy`；frontend 依赖 backend `/health`。
- 端口冲突：改 `.env` 后 `docker compose up -d`；重置数据：`docker compose down -v`。
- 校验编排：`docker compose config --quiet`。

## 枚举/常量出现位置清单

| 枚举 | 后端 | 前端 |
|---|---|---|
| DeviceType（EXTINGUISHER/HYDRANT/SMOKE_DETECTOR/SPRINKLER/EXIT_LIGHT） | `constants/device_type.py`、ORM 默认值 `models/fire_device.py`、种子 `seed.py`、合规计算、error/log 模板 | `constants/DeviceType.ts`、`types/DeviceType.ts`、设备台账筛选/展示、构造器 |
| InspectionStatus（PLANNED/IN_PROGRESS/SUBMITTED/REVIEWED/RETURNED/OVERDUE） | `constants/inspection_status.py`、引擎聚合 `domain/review_chain_engine.py`、ORM、控制器、日志模板 | `constants/InspectionStatus.ts`、`types/InspectionStatus.ts`、任务页 StatusBadge/筛选、store |
| HazardSeverity（LOW/MEDIUM/HIGH/CRITICAL） | `constants/hazard_severity.py`、引擎建单/重判、`compliance.py` 高危判定、种子、日志模板 | `constants/HazardSeverity.ts`、HazardSeverityTag、隐患筛选、检查项面板、总览 |
| ReviewState（DRAFT/SUBMITTED/REVIEWED/RETURNED/DISCARDED） | `constants/review_state.py`、引擎守卫、ORM 部分唯一索引、DTO、审计 | `constants/ReviewState.ts`、ChecklistPanel 锁定态、任务进度、类型 |
| HazardRectifyStatus（OPEN/RECTIFIED/CLOSED/CANCELLED） | `constants/hazard_severity.py`、引擎整改流、合规口径、索引 `active_key` | `constants/HazardRectifyStatus.ts`、隐患页按钮/筛选、总览 |
| DeviceCompliance（ACTIVE/HAZARD_PENDING/HIGH_HAZARD_BLOCKED/MAINTENANCE/RETIRED） | `constants/device_compliance.py`、`compliance.py`、设备 DTO、合规报表 | `constants/DeviceCompliance.ts`、台账/报表展示 |
| UserRole（INSPECTOR/MAINTAINER/SUPERVISOR/AUDITOR） | `constants/user_role.py`、JWT、`auth_deps`、RBAC 矩阵、种子账号 | `constants/UserRole.ts`、AuthStore、路由守卫、按钮显隐 |
| ConflictReason（STALE_TASK_REVISION/REVIEWED_PROTECTED） | `constants/submission_conflict.py`、引擎冲突区、错误码 | `constants/DeviceCompliance.ts`、任务冲突区列表、提交错误提示 |

## 为什么会牵一发动全身

- 新增一个检查项状态：要同步引擎守卫与聚合、ORM/DTO、Pydantic 模型、错误码/错误消息、日志模板、前端常量/类型、ChecklistPanel 与 StatusBadge。
- 改一次提交协议（如修订号语义）：`review_chain_engine`、`chain_service`、幂等表、冲突区、前端 `useReviewChain`/API/类型、README 流程要一起动。
- 调整“高危”范围（如把 MEDIUM 纳入封锁）：引擎重判、`compliance` 单一口径、设备台账 DTO、Dashboard/Reports、HazardSeverityTag 颜色会同时受影响——这正是跨文件协同能力的验证目标。

## License

MIT
