# 消防设施巡检维保平台

面向园区和物业公司的消防设备巡检、隐患整改、维保计划和合规台账系统。巡检任务、巡检结果、隐患整改单和消防设备接成一条**复核链**：提交带任务修订号，旧修订进冲突区，复核退回只放开被点名的检查项，隐患与设备状态随检查项实时重算。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

## 访问地址或 CLI 示例

前端：<http://localhost:20103>

后端健康检查：<http://localhost:21103/health>

复核链接口示例（角色通过请求头隔离）：

```bash
# 巡检员提交复核（带任务修订号 + 幂等提交号）
curl -X POST http://localhost:21103/api/inspection-task/1/submit \
  -H 'content-type: application/json' -H 'x-role: INSPECTOR' \
  -d '{"revision":1,"submission_id":"sub-1-r1","results":[{"device_id":1,"item_code":"PRESSURE","result_status":"ABNORMAL","severity":"HIGH"}]}'

# 审计员复核通过 / 退回点名检查项
curl -X POST http://localhost:21103/api/inspection-task/1/review -H 'x-role: AUDITOR'
curl -X POST http://localhost:21103/api/inspection-task/2/reject -H 'content-type: application/json' \
  -H 'x-role: AUDITOR' -d '{"item_codes":["ALARM_TEST"],"note":"复测"}'

# 维保商关闭隐患单（设备台账状态随即重算）
curl -X POST http://localhost:21103/api/hazard-ticket/1/close -H 'content-type: application/json' \
  -H 'x-role: MAINTAINER' -d '{"rectify_note":"已更换"}'

# 冲突区 / 合规报表 / 审计记录
curl http://localhost:21103/api/inspection-task/1/conflicts -H 'x-role: AUDITOR'
curl http://localhost:21103/api/reports/compliance -H 'x-role: AUDITOR'
curl http://localhost:21103/api/audit-logs -H 'x-role: AUDITOR'
```

## 复核链规则

1. **提交带任务修订号**：`POST /api/inspection-task/{id}/submit` 必须携带 `revision` 与 `submission_id`；修订号过期的提交进入冲突区（`GET .../conflicts`），返回 `REVISION_CONFLICT`，不能覆盖已复核结果。
2. **同一提交重试只生成一张隐患单**：`submission_id` 全链路幂等，断网重试直接重放首次处理结果；前端断网时把完整任务快照存入本地队列，恢复后按原 `submission_id` 续投。
3. **检查项修改后重算**：`PUT /api/inspection-result/{id}` 只允许改被退回点名（`REOPENED`）或待提交的项；改完隐患单自动开合、设备状态重算。
4. **复核退回只放开被点名的检查项**：`POST .../reject` 仅把 `item_codes` 点名的结果置为 `REOPENED`，其余结果保持原状；整包重投时未放开项被跳过（`skipped_items`）。
5. **未关闭高危隐患（HIGH/CRITICAL）**：设备台账与合规报表强制显示 `ABNORMAL`，不得显示正常；关单后自动恢复。
6. **权限隔离**：巡检员提交/改项，审计员复核/退回/查审计，维保商关单，越权返回 `RBAC_DENIED`。
7. **可追溯**：提交、复核、退回、冲突、关单、设备重算全部写入审计记录（`GET /api/audit-logs`），重开后仍可追到结果、隐患和审计链。

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`（`/api` 经 Vite 代理到 `http://localhost:21103`）
- 后端：`cd backend && pip install -r requirements.txt && uvicorn src.main:app --port 21103`，接口统一挂在 `/api`

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI + Redux Toolkit |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker Compose |

## 项目目录结构

```text
frontend/src/api, stores, types, constants, constructors, components/common, hooks, pages, router, utils, mocks
backend/src/routes, controllers, services, models, repositories, middlewares, constants, constructors, utils, types, config
```

## 环境变量说明

- `COMPOSE_PROJECT_NAME`: Compose 项目名，默认 `fire-inspect`
- `FRONTEND_PORT`: 前端端口，默认 `20103`
- `BACKEND_PORT`: 后端端口，默认 `21103`
- `DB_PORT`: 数据库宿主机端口
- `DB_USER/DB_PASSWORD/DB_NAME`: 本地数据库凭据
- `JWT_SECRET`: JWT 签名密钥

## Docker 部署说明

- 根 Compose 文件不写 `version`，顶层 `name: fire-inspect`。
- 容器名均使用 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 数据库使用命名卷，避免绑定中文路径。
- 常见问题：端口占用时修改 `.env` 中端口后重启；需要重置数据时执行 `docker compose down -v`。

## 枚举/常量出现位置清单

- DeviceType: `frontend/src/constants/DeviceType.ts`、`frontend/src/types/DeviceType.ts`、`backend/src/constants/device_type.py`、前后端 constructors、logTemplates、errorMessages、设备筛选与展示组件均有引用。
- InspectionStatus: `frontend/src/constants/InspectionStatus.ts`、`frontend/src/types/InspectionStatus.ts`、`backend/src/constants/inspection_status.py`（含 `TASK_SUBMITTABLE_STATUSES`/`TASK_FROZEN_STATUSES`）、constructors、logTemplates、errorMessages、任务筛选与展示组件均有引用。
- HazardSeverity: `frontend/src/constants/HazardSeverity.ts`、`frontend/src/types/HazardSeverity.ts`、`backend/src/constants/hazard_severity.py`（含 `HIGH_RISK_SEVERITIES`）、constructors、logTemplates、errorMessages、隐患筛选与 `HazardSeverityTag` 均有引用。
- ReviewState（复核链）: `frontend/src/constants/ReviewState.ts`、`backend/src/constants/review_state.py`、`useChecklistProgress`、`ChecklistPanel`、任务/结果服务。
- RectifyStatus: `frontend/src/constants/RectifyStatus.ts`、`backend/src/constants/rectify_status.py`、隐患服务与台账重算。
- DeviceStatus: `frontend/src/constants/DeviceStatus.ts`、`backend/src/constants/device_status.py`、设备台账与合规报表。
- Roles: `frontend/src/constants/roles.ts`、`backend/src/constants/roles.py`、`rbac_middleware.py`、前端按钮显隐。

## 为什么会牵一发动全身

实体字段、枚举、日志模板、错误消息、构造器、筛选器和展示组件被刻意拆散到多个目录；修改一个状态值通常需要同步类型、构造器、服务、控制器、store、页面、README 与数据库种子。复核链进一步把任务修订号、提交幂等号、隐患单和设备状态串在一起：改任何一环都要同时动 service、repository、常量、错误码、审计模板和前端 store/hook。

## License

MIT
