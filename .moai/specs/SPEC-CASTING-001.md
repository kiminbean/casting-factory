# SPEC-CASTING-001: Casting Production Dashboard

## Overview
Casting factory production monitoring dashboard with real-time process tracking, order management, quality inspection, logistics control, and factory floor map visualization.

## Tech Stack
- Frontend: Next.js 16 (App Router) + TypeScript + Tailwind CSS
- Charts: Recharts (dynamic import, ssr: false)
- Icons: Lucide React
- Backend: FastAPI 0.115 + SQLAlchemy 2.0 + Pydantic v2
- DB: SQLite (casting_factory.db)
- WebSocket: /ws/dashboard (실시간 브로드캐스트)
- Python: 3.11 (venv)
- Network: allowedDevOrigins for LAN access

## Requirements Source
- User_Requirements.pdf (UR_01 ~ UR_20+)
- System_Requirements_v2.pdf (SR-01 ~ SR-30+)
- System_Requirements_v3.pdf (v3 updates)

## Implemented Pages

| Route | Page | Status |
|-------|------|--------|
| `/` | Dashboard overview | Done |
| `/production` | Production monitoring + Factory Map | Done |
| `/orders` | Order management (admin) | Done |
| `/quality` | Quality inspection & statistics | Done |
| `/logistics` | Transport, storage, shipping | Done |
| `/customer` | Customer order form (standalone layout) | Done |

## Functional Requirements

### FR-01: Production Monitoring Dashboard (R1)
- EARS: When the system starts, the dashboard SHALL display real-time status of all production stages
- Stages: Melting(용해) -> Molding(주형) -> Casting(주조/주탕) -> Cooling(냉각) -> Demolding(탈형) -> Post-processing(후처리) -> Inspection(검사) -> Classification(분류)
- Each stage shows: status, temperature, time, equipment state
- Process flow cards: uniform size (w-40 h-36)

### FR-02: Factory Layout Map (R1) [v3 NEW]
- EARS: When the admin opens production page, the system SHALL display a factory floor map with equipment and AMR positions
- 9-zone grid layout (3x3): raw material, melting, molding, casting, cooling, demolding, post-processing, inspection, storage/shipping
- AMR position indicators with animation (moving, idle, charging)
- Zone click shows equipment detail popover
- Dark background control-room style

### FR-03: Order Management (R1)
- EARS: When a customer submits an order, the system SHALL create an order record with product info, quantity, specs
- Order states: Pending -> Reviewing -> Approved -> In Production -> Shipping Ready -> Completed
- Admin can approve/reject/modify orders
- Standard product catalog (manhole covers, etc.)

### FR-04: Customer Order Form (R1)
- EARS: When a customer accesses /customer, the system SHALL provide a 5-step order form
- Steps: Product selection -> Spec input -> Quote review -> Customer info -> Order complete
- Independent layout (no admin sidebar)
- Auto price calculation with post-processing addons

### FR-05: Quality Inspection (R1)
- EARS: When a casting passes through inspection, the system SHALL classify it as pass/fail
- Show defect rate, total production count, good/bad counts
- 7 defect types tracked with distribution chart
- Cumulative result management with inspection history [v3 enhanced]
- Accuracy target: 95%+, Response time: < 1 second

### FR-06: Transport/Logistics (R2)
- EARS: When a transport request is created, the system SHALL assign an AMR and track delivery
- Transport states: Requested -> Assigned -> Moving -> Arrived -> Completed/Failed
- AMR resource management with battery level tracking
- Transport exception handling with failure reason logging [v3 enhanced]

### FR-07: Process Control (R1)
- EARS: When an admin issues a control command, the system SHALL start/stop/resume equipment per zone
- Emergency stop capability
- Equipment error detection and alerts
- Conveyor control: speed slider (1-100%), Auto/Manual mode toggle [v3 NEW]
- Classification device control: motor angle visualization (0deg/45deg) [v3 NEW]

### FR-08: Anomaly Detection & Alerts (R1)
- EARS: When an anomaly is detected, the system SHALL notify the admin immediately
- Alert types: Equipment error, Process delay, Defect rate anomaly
- Priority-based alert ordering [v3 enhanced]

### FR-09: Inventory & Storage (R2)
- EARS: When products are stored, the system SHALL manage a real-time storage map
- 7-state storage slots: empty, occupied, reserved, working, unavailable, mismatch, restricted [v3 enhanced]
- ABC grade classification for optimal placement [v3 NEW]
- Product relocation (Swap) with rollback on failure [v3 NEW]
- Storage exception handling [v3 NEW]

### FR-10: Shipping Management (R2) [v3 NEW]
- EARS: When a shipping order is created, the system SHALL verify stock, generate shipping docs, track LIFO
- Shipping order creation with stock validation
- LIFO-based shipping execution
- Shipping history and tracking

### FR-11: Post-Processing (R3) [v3 enhanced]
- EARS: When post-processing is complete, the system SHALL request pallet loading
- Conveyor integration control (advance conditions: product processed + previous step done)
- Pallet loading request within 3 seconds of completion
- Cleaning state management (before/cleaning/done)

## Non-Functional Requirements
- NFR-01: Response time < 1s for all monitoring data
- NFR-02: Quality inspection accuracy >= 95%
- NFR-03: Classification accuracy >= 99%
- NFR-04: Transport position accuracy +/- 5cm, heading +/- 5deg
- NFR-05: Storage map data consistency 100%
- NFR-06: Transport speed: straight 1.0m/s, turning 0.5m/s
- NFR-07: Conveyor speed: 1-100% range, Takt Time compliance
- NFR-08: Storage space utilization target >= 90%
- NFR-09: Position allocation response < 1s
- NFR-10: Shipping order restricted to stock <= inventory

## Acceptance Criteria
- [x] Dashboard shows all 8 production stages with real-time status
- [x] Factory layout map with 9 zones and AMR positions (v3)
- [x] Order CRUD with state machine transitions
- [x] Customer order form (5-step, standalone layout)
- [x] Quality metrics with charts (defect rate, production count, 7 defect types)
- [x] Transport tracking with AMR status and battery
- [x] Alert system for anomalies
- [x] Conveyor control (speed, mode) and classification device (v3)
- [x] Shipping management with order table and history (v3)
- [x] Storage map with 7-state visualization
- [x] Responsive layout for control room monitors
- [x] Korean language UI
- [x] LAN network access (allowedDevOrigins)
- [x] FastAPI REST API 22개 엔드포인트 (Phase 2)
- [x] SQLite DB with auto-seed data (Phase 2)
- [x] WebSocket /ws/dashboard 실시간 브로드캐스트 (Phase 3)
- [x] Swagger API 문서 (http://localhost:8000/docs)

## Phase Plan
- Phase 1: Frontend dashboard with mock data (DONE)
- Phase 2: FastAPI backend + SQLite DB + REST API 22개 (DONE)
- Phase 3: WebSocket 실시간 브로드캐스트 /ws/dashboard (DONE)

## Changelog
- v1.0 (2026-03-30): Initial implementation based on UR + SR v2
- v1.1 (2026-03-30): Mock data enhancement (30-day metrics, 30 inspections, 7 defect types)
- v1.2 (2026-03-30): Customer order page (/customer) with standalone layout
- v2.0 (2026-03-30): SR v3 updates - Factory Map, conveyor/classification control, shipping management
- v2.1 (2026-03-30): ESLint fixes, process flow card size unification
- v3.0 (2026-03-31): Phase 2+3 - FastAPI + SQLite DB + WebSocket 실시간 업데이트
