# SPEC-CASTING-001: Casting Production Dashboard

## Overview
Casting factory production monitoring dashboard with real-time process tracking, order management, quality inspection, and logistics control.

## Tech Stack
- Frontend: Next.js 16 (App Router) + TypeScript + Tailwind CSS
- Charts: Recharts
- Icons: Lucide React
- Backend: Mock data (Phase 1), FastAPI (Phase 2)
- DB: PostgreSQL + pgvector (Phase 2)

## Requirements Source
- User_Requirements.pdf (UR_01 ~ UR_20+)
- System_Requirements_v2.pdf (SR-01 ~ SR-30+)

## Functional Requirements

### FR-01: Production Monitoring Dashboard (R1)
- EARS: When the system starts, the dashboard SHALL display real-time status of all production stages
- Stages: Melting(용해) -> Molding(주형) -> Casting(주조/주탕) -> Cooling(냉각) -> Demolding(탈형) -> Post-processing(후처리) -> Inspection(검사) -> Classification(분류)
- Each stage shows: status, temperature, time, equipment state

### FR-02: Order Management (R1)
- EARS: When a customer submits an order, the system SHALL create an order record with product info, quantity, specs
- Order states: Pending -> Reviewing -> Approved -> In Production -> Shipping Ready -> Completed
- Admin can approve/reject/modify orders
- Standard product catalog (manhole covers, etc.)

### FR-03: Quality Inspection (R1)
- EARS: When a casting passes through inspection, the system SHALL classify it as pass/fail
- Show defect rate, total production count, good/bad counts
- Accuracy target: 95%+
- Response time: < 1 second

### FR-04: Transport/Logistics (R2)
- EARS: When a transport request is created, the system SHALL assign an AMR and track delivery
- Transport states: Requested -> Assigned -> Moving -> Arrived -> Completed/Failed
- AMR resource management with status tracking

### FR-05: Process Control (R1)
- EARS: When an admin issues a control command, the system SHALL start/stop/resume equipment per zone
- Emergency stop capability
- Equipment error detection and alerts

### FR-06: Anomaly Detection & Alerts (R1)
- EARS: When an anomaly is detected, the system SHALL notify the admin immediately
- Alert types: Equipment error, Process delay, Defect rate anomaly

### FR-07: Inventory & Shipping (R2)
- EARS: When a shipping order is created, the system SHALL verify stock, generate shipping docs, track LIFO
- Pallet loading status, storage map
- Shipping history

## Non-Functional Requirements
- NFR-01: Response time < 1s for all monitoring data
- NFR-02: Quality inspection accuracy >= 95%
- NFR-03: Classification accuracy >= 99%
- NFR-04: Transport position accuracy +/- 5cm
- NFR-05: Storage map data consistency 100%

## Acceptance Criteria
- [ ] Dashboard shows all 8 production stages with real-time status
- [ ] Order CRUD with state machine transitions
- [ ] Quality metrics with charts (defect rate, production count)
- [ ] Transport tracking with AMR status
- [ ] Alert system for anomalies
- [ ] Responsive layout for control room monitors
- [ ] Korean language UI

## Phase Plan
- Phase 1: Frontend dashboard with mock data (current)
- Phase 2: FastAPI backend + PostgreSQL integration
- Phase 3: Real-time WebSocket updates + sensor integration
