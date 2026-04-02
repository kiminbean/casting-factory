"""생산 스케줄링 API — SR-CTL-04 생산 개시 + SR-CTL-05 우선순위 계산."""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Equipment,
    Order,
    OrderDetail,
    PriorityChangeLog,
    ProcessStage,
    ProductionJob,
)
from app.schemas.schemas import (
    PriorityCalculateRequest,
    PriorityCalculateResponse,
    PriorityFactor,
    PriorityLogCreate,
    PriorityLogResponse,
    PriorityResult,
    ProductionJobResponse,
    ProductionStartRequest,
)

router = APIRouter(prefix="/api/production/schedule", tags=["schedule"])


# ---------------------------------------------------------------------------
# 우선순위 계산 엔진
# ---------------------------------------------------------------------------

def _calc_delivery_urgency(requested_delivery: str | None) -> tuple[float, str]:
    """납기일 긴급도 (25점 만점)."""
    if not requested_delivery:
        return 5.0, "납기일 미지정"
    try:
        deadline = datetime.fromisoformat(requested_delivery.replace("Z", "+00:00"))
        # timezone-naive인 경우 UTC로 보정
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            deadline = datetime.strptime(requested_delivery, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return 5.0, "납기일 파싱 불가"

    now = datetime.now(timezone.utc)
    days_left = (deadline - now).days

    if days_left <= 3:
        return 25.0, f"납기 {days_left}일 이내 (긴급)"
    if days_left <= 7:
        return 20.0, f"납기 {days_left}일 이내"
    if days_left <= 14:
        return 15.0, f"납기 {days_left}일 이내"
    if days_left <= 30:
        return 10.0, f"납기 {days_left}일 이내 (여유)"
    return 5.0, f"납기 {days_left}일 이상 남음"


def _calc_readiness(
    stages: list[ProcessStage], equipment: list[Equipment],
) -> tuple[float, str, bool, list[str]]:
    """착수 가능 여부 (20점 만점). (score, detail, is_ready, blocking_reasons)"""
    blocking: list[str] = []

    # 공정 라인 확인: running 상태가 아닌 공정이 하나라도 있으면 할당 가능
    running_stages = [s for s in stages if s.status == "running"]
    idle_stages = [s for s in stages if s.status == "idle"]

    if len(idle_stages) == 0 and len(running_stages) == len(stages):
        blocking.append("전체 공정 라인 가동 중 (빈 라인 없음)")

    # 주요 설비 확인
    furnaces = [e for e in equipment if e.type == "furnace"]
    available_furnaces = [e for e in furnaces if e.status in ("idle", "running")]
    if len(available_furnaces) == 0:
        blocking.append("용해로 전체 비가용 (정비/오류)")

    mold_presses = [e for e in equipment if e.type == "mold_press"]
    available_presses = [e for e in mold_presses if e.status in ("idle", "running")]
    if len(available_presses) == 0:
        blocking.append("조형기 전체 비가용")

    # AMR 가용성
    amrs = [e for e in equipment if e.type == "amr"]
    available_amrs = [
        e for e in amrs
        if e.status == "idle" or (e.status == "charging" and (e.battery or 0) > 50)
    ]
    if len(available_amrs) == 0:
        blocking.append("AMR 전체 사용 불가")

    is_ready = len(blocking) == 0
    if is_ready:
        score = 20.0
        detail = "전 공정 착수 가능"
    elif len(blocking) <= 1:
        score = 10.0
        detail = f"일부 제한: {blocking[0]}"
    else:
        score = 0.0
        detail = f"{len(blocking)}개 차단 요인"

    return score, detail, is_ready, blocking


def _calc_order_age(created_at: str) -> tuple[float, str]:
    """주문 체류 시간 (15점 만점)."""
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
    except ValueError:
        return 2.0, "생성일 파싱 불가"

    now = datetime.now(timezone.utc)
    days = (now - created).days

    if days >= 7:
        return 15.0, f"승인 후 {days}일 경과 (오래됨)"
    if days >= 3:
        return 10.0, f"승인 후 {days}일 경과"
    if days >= 1:
        return 5.0, f"승인 후 {days}일 경과"
    return 2.0, "당일 승인"


def _calc_delay_risk(
    requested_delivery: str | None, total_quantity: int,
) -> tuple[float, str, str]:
    """지연 위험도 (15점 만점). (score, detail, risk_level)"""
    # 예상 생산일: 기본 3일 + 50개당 1일
    estimated_days = 3 + (total_quantity // 50)

    if not requested_delivery:
        return 5.0, "납기 미지정 (위험 평가 불가)", "medium"

    try:
        deadline = datetime.fromisoformat(requested_delivery.replace("Z", "+00:00"))
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            deadline = datetime.strptime(requested_delivery, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return 5.0, "납기일 파싱 불가", "medium"

    now = datetime.now(timezone.utc)
    days_left = (deadline - now).days
    margin = days_left - estimated_days

    if margin < 0:
        return 15.0, f"납기 초과 위험 (예상 {estimated_days}일, 잔여 {days_left}일)", "high"
    if margin <= 3:
        return 10.0, f"지연 위험 (여유 {margin}일)", "medium"
    return 5.0, f"여유 있음 (마진 {margin}일)", "low"


def _calc_customer_importance(total_amount: float, all_amounts: list[float]) -> tuple[float, str]:
    """고객 중요도 (10점 만점) — 주문 금액 기반."""
    if not all_amounts:
        return 6.0, "비교 데이터 없음"

    sorted_amounts = sorted(all_amounts, reverse=True)
    top_20_threshold = sorted_amounts[max(0, len(sorted_amounts) // 5 - 1)] if len(sorted_amounts) >= 5 else sorted_amounts[0]

    if total_amount >= top_20_threshold:
        return 10.0, f"고액 주문 ({total_amount:,.0f}원)"
    if total_amount >= sorted_amounts[len(sorted_amounts) // 2]:
        return 6.0, f"중간 규모 ({total_amount:,.0f}원)"
    return 3.0, f"소액 주문 ({total_amount:,.0f}원)"


def _calc_quantity_efficiency(total_quantity: int) -> tuple[float, str]:
    """수량 효율 (10점 만점) — 소량 주문 우선."""
    if total_quantity <= 50:
        return 10.0, f"{total_quantity}개 (소량, 빠른 회전)"
    if total_quantity <= 100:
        return 7.0, f"{total_quantity}개 (중량)"
    if total_quantity <= 200:
        return 4.0, f"{total_quantity}개 (대량)"
    return 2.0, f"{total_quantity}개 (초대량)"


def _calc_setup_cost(product_names: list[str], prev_products: list[str]) -> tuple[float, str]:
    """세팅 변경 비용 (5점 만점)."""
    if not prev_products:
        return 3.0, "이전 작업 없음 (기본)"

    # 직전 작업과 동일 제품이면 보너스
    overlap = set(product_names) & set(prev_products)
    if overlap:
        return 5.0, f"동일 제품 연속 ({', '.join(overlap)})"
    return 0.0, "제품 변경 필요 (세팅 비용 발생)"


def _build_recommendation(factors: list[PriorityFactor]) -> str:
    """상위 2-3개 요인으로 추천 사유 생성."""
    top_factors = sorted(factors, key=lambda f: f.score / f.max_score, reverse=True)[:3]
    reasons = [f.detail for f in top_factors if f.score > 0]
    return " + ".join(reasons) if reasons else "기본 우선순위"


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.post("/calculate", response_model=PriorityCalculateResponse)
async def calculate_priority(
    payload: PriorityCalculateRequest, db: Session = Depends(get_db),
):
    """선택한 주문들의 생산 우선순위를 계산하여 반환."""
    if not payload.order_ids:
        raise HTTPException(status_code=400, detail="주문을 1개 이상 선택하세요.")

    orders = db.query(Order).filter(Order.id.in_(payload.order_ids)).all()
    if not orders:
        raise HTTPException(status_code=404, detail="선택한 주문을 찾을 수 없습니다.")

    # 공정/설비 상태 조회
    stages = db.query(ProcessStage).all()
    equipment = db.query(Equipment).all()

    # 전체 주문 금액 목록 (중요도 비교용)
    all_amounts = [float(o.total_amount) for o in db.query(Order).all()]

    # 직전 생산 작업의 제품 목록 (세팅 변경 비용 비교)
    prev_jobs = (
        db.query(ProductionJob)
        .filter(ProductionJob.status.in_(["running", "completed"]))
        .order_by(ProductionJob.created_at.desc())
        .limit(3)
        .all()
    )
    prev_order_ids = [j.order_id for j in prev_jobs]
    prev_details = (
        db.query(OrderDetail).filter(OrderDetail.order_id.in_(prev_order_ids)).all()
        if prev_order_ids else []
    )
    prev_products = list({d.product_name for d in prev_details})

    results: list[PriorityResult] = []

    for order in orders:
        details = db.query(OrderDetail).filter(OrderDetail.order_id == order.id).all()
        total_qty = sum(d.quantity for d in details)
        product_names = list({d.product_name for d in details})
        product_summary = ", ".join(product_names) if product_names else "제품 미정"

        factors: list[PriorityFactor] = []

        # 1. 납기일 긴급도
        s1, d1 = _calc_delivery_urgency(order.requested_delivery)
        factors.append(PriorityFactor(name="납기일 긴급도", score=s1, max_score=25.0, detail=d1))

        # 2. 착수 가능 여부
        s2, d2, is_ready, blocking = _calc_readiness(stages, equipment)
        factors.append(PriorityFactor(name="착수 가능 여부", score=s2, max_score=20.0, detail=d2))

        # 3. 주문 체류 시간
        s3, d3 = _calc_order_age(order.created_at)
        factors.append(PriorityFactor(name="주문 체류 시간", score=s3, max_score=15.0, detail=d3))

        # 4. 지연 위험도
        s4, d4, delay_risk = _calc_delay_risk(order.requested_delivery, total_qty)
        factors.append(PriorityFactor(name="지연 위험도", score=s4, max_score=15.0, detail=d4))

        # 5. 고객 중요도
        s5, d5 = _calc_customer_importance(float(order.total_amount), all_amounts)
        factors.append(PriorityFactor(name="고객 중요도", score=s5, max_score=10.0, detail=d5))

        # 6. 수량 효율
        s6, d6 = _calc_quantity_efficiency(total_qty)
        factors.append(PriorityFactor(name="수량 효율", score=s6, max_score=10.0, detail=d6))

        # 7. 세팅 변경 비용
        s7, d7 = _calc_setup_cost(product_names, prev_products)
        factors.append(PriorityFactor(name="세팅 변경 비용", score=s7, max_score=5.0, detail=d7))

        total_score = round(sum(f.score for f in factors), 1)
        estimated_days = 3 + (total_qty // 50)

        results.append(PriorityResult(
            order_id=order.id,
            company_name=order.company_name,
            product_summary=product_summary,
            total_quantity=total_qty,
            requested_delivery=order.requested_delivery,
            total_score=total_score,
            rank=0,  # 정렬 후 설정
            factors=factors,
            recommendation_reason=_build_recommendation(factors),
            delay_risk=delay_risk,
            ready_status="ready" if is_ready else "not_ready",
            blocking_reasons=blocking,
            estimated_days=estimated_days,
        ))

    # 점수 높은 순으로 정렬 후 순위 부여
    results.sort(key=lambda r: r.total_score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1

    return PriorityCalculateResponse(results=results)


@router.post("/start", response_model=List[ProductionJobResponse])
async def start_production(
    payload: ProductionStartRequest, db: Session = Depends(get_db),
):
    """선택된 주문의 생산을 개시하고 ProductionJob 레코드를 생성."""
    if not payload.order_ids:
        raise HTTPException(status_code=400, detail="주문을 1개 이상 선택하세요.")

    orders = db.query(Order).filter(
        Order.id.in_(payload.order_ids),
        Order.status == "approved",
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="승인 상태인 주문을 찾을 수 없습니다.")

    now = datetime.now(timezone.utc).isoformat()

    # 기존 최대 JOB 번호 조회
    last_job = (
        db.query(ProductionJob)
        .order_by(ProductionJob.id.desc())
        .first()
    )
    next_num = 1
    if last_job:
        try:
            next_num = int(last_job.id.split("-")[-1]) + 1
        except (ValueError, IndexError):
            next_num = db.query(ProductionJob).count() + 1

    jobs: list[ProductionJob] = []

    for rank, order in enumerate(orders, start=1):
        # 주문 상태 전환
        order.status = "in_production"
        order.updated_at = now

        # 예상 완료일 계산
        details = db.query(OrderDetail).filter(OrderDetail.order_id == order.id).all()
        total_qty = sum(d.quantity for d in details)
        est_days = 3 + (total_qty // 50)
        est_dt = datetime.now(timezone.utc)
        from datetime import timedelta
        est_completion = (est_dt + timedelta(days=est_days)).isoformat()

        job = ProductionJob(
            id=f"JOB-2026-{next_num:03d}",
            order_id=order.id,
            priority_score=0.0,
            priority_rank=rank,
            assigned_stage="melting",
            status="queued",
            estimated_completion=est_completion,
            started_at=now,
            created_at=now,
        )
        db.add(job)
        jobs.append(job)
        next_num += 1

    db.commit()
    for job in jobs:
        db.refresh(job)

    return jobs


@router.get("/jobs", response_model=List[ProductionJobResponse])
async def list_production_jobs(db: Session = Depends(get_db)):
    """생산 작업 목록을 생성일 역순으로 반환."""
    jobs = db.query(ProductionJob).order_by(ProductionJob.created_at.desc()).all()
    return jobs


@router.post("/priority-log", response_model=PriorityLogResponse, status_code=201)
async def create_priority_log(
    payload: PriorityLogCreate, db: Session = Depends(get_db),
):
    """우선순위 수동 변경 이력을 기록."""
    now = datetime.now(timezone.utc).isoformat()
    log = PriorityChangeLog(
        order_id=payload.order_id,
        old_rank=payload.old_rank,
        new_rank=payload.new_rank,
        reason=payload.reason,
        changed_by="admin",
        changed_at=now,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/priority-log/{order_id}", response_model=List[PriorityLogResponse])
async def get_priority_logs(order_id: str, db: Session = Depends(get_db)):
    """특정 주문의 우선순위 변경 이력 조회."""
    logs = (
        db.query(PriorityChangeLog)
        .filter(PriorityChangeLog.order_id == order_id)
        .order_by(PriorityChangeLog.changed_at.desc())
        .all()
    )
    return logs
