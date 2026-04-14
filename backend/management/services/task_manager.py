"""Task Manager — 승인된 주문을 work_order + items 로 분해.

Confluence DB v47 스키마 기준:
- order (status='approved') → work_order 1건 + items N건 (N = order_detail.qty 합계)
- 각 item 은 cur_stage='QUE' 로 시작
- 동일 주문에 대한 중복 시작 방지

@MX:ANCHOR: Phase 2 산출물. PyQt 의 [▶ 생산 시작] 버튼이 호출하는 핵심 진입점.
@MX:REASON: V6 아키텍처에서 Interface Service 가 우회되므로 본 모듈이 트랜잭션 경계.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable

from app.models.models import Item, Order, OrderDetail, WorkOrder
from db_session import SessionLocal

logger = logging.getLogger(__name__)


class TaskManager:
    """주문 → work_order + items 분해."""

    def start_production(self, order_ids: list[str]) -> list[WorkOrder]:
        """승인 주문들을 생산 개시 (work_order + items 생성).

        Args:
            order_ids: 시작할 주문 ID 리스트. status='approved' 만 처리.

        Returns:
            생성된 WorkOrder ORM 객체 리스트 (items 관계 미사전 로드 — caller 가 별도 조회).

        Raises:
            ValueError: 빈 리스트
        """
        if not order_ids:
            raise ValueError("order_ids 가 비어있습니다")

        now = datetime.now(timezone.utc).isoformat()
        created: list[WorkOrder] = []

        with SessionLocal() as db:
            orders = (
                db.query(Order)
                .filter(Order.id.in_(order_ids), Order.status == "approved")
                .all()
            )
            if not orders:
                logger.warning("시작 가능한 승인 주문 없음: %s", order_ids)
                return []

            for order in orders:
                # 중복 시작 방지: 이미 work_order 가 있으면 스킵
                exists = (
                    db.query(WorkOrder)
                    .filter(WorkOrder.order_id == order.id)
                    .first()
                )
                if exists:
                    logger.info("이미 work_order 존재: %s (id=%s)", order.id, exists.id)
                    created.append(exists)
                    continue

                # order_detail 의 수량 합산 → item 발급 수
                details = (
                    db.query(OrderDetail).filter(OrderDetail.order_id == order.id).all()
                )
                total_qty = sum(int(d.quantity or 0) for d in details)
                if total_qty <= 0:
                    logger.warning(
                        "주문 %s 의 order_details qty 합계가 0 — work_order 미생성", order.id
                    )
                    continue

                wo = WorkOrder(
                    order_id=order.id,
                    pattern_id=None,  # TODO: order_detail 에 pattern_id 추가 후 매핑
                    qty=total_qty,
                    status="QUE",
                    plan_start=now,
                )
                db.add(wo)
                db.flush()  # wo.id 확보

                # item 1개당 1 row 생성, 모두 cur_stage='QUE'
                items = [
                    Item(
                        order_id=order.id,
                        work_order_id=wo.id,
                        cur_stage="QUE",
                        curr_res=None,
                        insp_id=None,
                        mfg_at=now,
                    )
                    for _ in range(total_qty)
                ]
                db.add_all(items)

                # 주문 상태 전환
                order.status = "in_production"
                order.updated_at = now

                created.append(wo)

            db.commit()
            for wo in created:
                db.refresh(wo)

        logger.info(
            "start_production 완료: %d 건 work_order, 총 %d items",
            len(created),
            sum(wo.qty for wo in created),
        )
        return created

    def list_items(
        self,
        order_id: str | None,
        stage: str | None,
        limit: int,
    ) -> Iterable[Item]:
        with SessionLocal() as db:
            q = db.query(Item)
            if order_id:
                q = q.filter(Item.order_id == order_id)
            if stage:
                q = q.filter(Item.cur_stage == stage)
            return q.order_by(Item.id.asc()).limit(limit or 100).all()
