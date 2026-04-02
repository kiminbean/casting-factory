"use client";

import { useState, useEffect, useCallback } from "react";
import {
  CalendarClock,
  CheckCircle2,
  ChevronUp,
  ChevronDown,
  Factory,
  AlertTriangle,
  Loader2,
  Play,
  Calculator,
  ShieldAlert,
  Clock,
  Package,
  Building2,
  Sparkles,
  XCircle,
  Info,
} from "lucide-react";
import {
  fetchOrders,
  calculatePriority,
  startProduction,
  createPriorityLog,
} from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import type { Order, PriorityResult } from "@/lib/types";

// ────────────────────────────────────────
// 지연 위험도 배지
// ────────────────────────────────────────

const RISK_BADGE: Record<string, { label: string; color: string; icon: typeof AlertTriangle }> = {
  high: { label: "높음", color: "bg-red-100 text-red-700 border-red-200", icon: AlertTriangle },
  medium: { label: "보통", color: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: Clock },
  low: { label: "낮음", color: "bg-green-100 text-green-700 border-green-200", icon: CheckCircle2 },
};

// ────────────────────────────────────────
// 점수 바 컴포넌트
// ────────────────────────────────────────

function ScoreBar({ score, maxScore, label }: { score: number; maxScore: number; label: string }) {
  const pct = Math.round((score / maxScore) * 100);
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-28 text-gray-500 shrink-0 truncate">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            pct >= 80 ? "bg-blue-500" : pct >= 50 ? "bg-yellow-400" : "bg-gray-300",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-14 text-right text-gray-600 font-mono text-xs">
        {score}/{maxScore}
      </span>
    </div>
  );
}

// ────────────────────────────────────────
// 사유 입력 모달
// ────────────────────────────────────────

function ReasonModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => void;
}) {
  const [reason, setReason] = useState("");
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-[440px] p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3">우선순위 변경 사유</h3>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="변경 사유를 입력하세요 (필수)"
          className="w-full h-24 border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
        />
        <div className="flex justify-end gap-2 mt-4">
          <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
            취소
          </button>
          <button
            type="button"
            disabled={!reason.trim()}
            onClick={() => { onSubmit(reason.trim()); setReason(""); }}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-40"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}

// ────────────────────────────────────────
// 생산 시작 확인 모달
// ────────────────────────────────────────

function ConfirmStartModal({
  open,
  count,
  onClose,
  onConfirm,
  loading,
}: {
  open: boolean;
  count: number;
  onClose: () => void;
  onConfirm: () => void;
  loading: boolean;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-[420px] p-6 text-center">
        <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
          <Factory className="w-7 h-7 text-blue-600" />
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">생산 개시 확인</h3>
        <p className="text-sm text-gray-500 mb-5">
          선택된 <strong className="text-blue-600">{count}건</strong>의 주문을
          <br />
          <strong className="text-blue-600">[승인] → [생산 중]</strong>으로 전환하고 공정에 할당합니다.
        </p>
        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="flex-1 py-2.5 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">
            취소
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={onConfirm}
            className="flex-1 py-2.5 text-sm bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            생산 시작
          </button>
        </div>
      </div>
    </div>
  );
}

// ────────────────────────────────────────
// 메인 페이지
// ────────────────────────────────────────

export default function ProductionSchedulePage() {
  // 데이터 상태
  const [approvedOrders, setApprovedOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 선택/계산 상태
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [priorityResults, setPriorityResults] = useState<PriorityResult[]>([]);
  const [calculating, setCalculating] = useState(false);
  const [calculated, setCalculated] = useState(false);

  // 모달 상태
  const [reasonModal, setReasonModal] = useState<{ open: boolean; orderId: string; oldRank: number; newRank: number }>({
    open: false, orderId: "", oldRank: 0, newRank: 0,
  });
  const [confirmModal, setConfirmModal] = useState(false);
  const [starting, setStarting] = useState(false);

  // 승인 주문 로드
  const loadOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const all = await fetchOrders();
      setApprovedOrders(all.filter((o) => o.status === "approved"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "데이터 로드 실패");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  // 체크박스 토글
  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
    setCalculated(false);
    setPriorityResults([]);
  };

  // 전체 선택/해제
  const toggleAll = () => {
    if (selectedIds.size === approvedOrders.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(approvedOrders.map((o) => o.id)));
    }
    setCalculated(false);
    setPriorityResults([]);
  };

  // 우선순위 계산
  const handleCalculate = async () => {
    if (selectedIds.size === 0) return;
    try {
      setCalculating(true);
      const res = await calculatePriority(Array.from(selectedIds));
      setPriorityResults(res.results);
      setCalculated(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : "우선순위 계산 실패");
    } finally {
      setCalculating(false);
    }
  };

  // 순서 변경 (위/아래)
  const moveItem = (index: number, direction: "up" | "down") => {
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= priorityResults.length) return;

    const item = priorityResults[index];
    setReasonModal({
      open: true,
      orderId: item.orderId,
      oldRank: item.rank,
      newRank: priorityResults[newIndex].rank,
    });

    // 실제 이동은 사유 입력 후 수행
    const pendingSwap = { index, newIndex };
    setReasonModal((prev) => ({ ...prev, _swap: pendingSwap } as typeof prev));
  };

  const handleReasonSubmit = async (reason: string) => {
    const swap = (reasonModal as { _swap?: { index: number; newIndex: number } })._swap;
    if (swap) {
      const updated = [...priorityResults];
      [updated[swap.index], updated[swap.newIndex]] = [updated[swap.newIndex], updated[swap.index]];
      // 순위 재부여
      updated.forEach((r, i) => { r.rank = i + 1; });
      setPriorityResults(updated);

      // 이력 기록
      try {
        await createPriorityLog({
          order_id: reasonModal.orderId,
          old_rank: reasonModal.oldRank,
          new_rank: reasonModal.newRank,
          reason,
        });
      } catch {
        // 이력 기록 실패는 무시 (비차단)
      }
    }
    setReasonModal({ open: false, orderId: "", oldRank: 0, newRank: 0 });
  };

  // 생산 개시
  const handleStartProduction = async () => {
    try {
      setStarting(true);
      const orderIds = priorityResults.map((r) => r.orderId);
      await startProduction(orderIds);
      setConfirmModal(false);
      setPriorityResults([]);
      setSelectedIds(new Set());
      setCalculated(false);
      await loadOrders();
    } catch (err) {
      alert(err instanceof Error ? err.message : "생산 개시 실패");
    } finally {
      setStarting(false);
    }
  };

  // ────── 로딩/에러 ──────

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={36} className="animate-spin text-blue-500" />
          <p className="text-base text-gray-500">승인 주문 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3 text-center">
          <AlertTriangle size={36} className="text-red-400" />
          <p className="text-base text-red-600">{error}</p>
          <button type="button" onClick={loadOrders} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-[1400px] mx-auto space-y-6">
        {/* 페이지 헤더 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center">
              <CalendarClock className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">생산 계획</h1>
              <p className="text-base text-gray-500 mt-0.5">
                승인된 주문의 생산 우선순위를 계산하고 공정에 할당합니다.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              disabled={selectedIds.size === 0 || calculating}
              onClick={handleCalculate}
              className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 text-white rounded-xl font-semibold text-base hover:bg-amber-600 disabled:opacity-40 transition-colors shadow-sm"
            >
              {calculating ? <Loader2 size={16} className="animate-spin" /> : <Calculator size={16} />}
              우선순위 계산 ({selectedIds.size}건)
            </button>
            {calculated && priorityResults.length > 0 && (
              <button
                type="button"
                onClick={() => setConfirmModal(true)}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-base hover:bg-blue-700 transition-colors shadow-sm"
              >
                <Play size={16} />
                생산 시작 ({priorityResults.length}건)
              </button>
            )}
          </div>
        </div>

        {/* ====== 우선순위 계산 결과 (상단) ====== */}
        {calculated && priorityResults.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <h2 className="text-xl font-bold text-gray-900">추천 생산 순서</h2>
              <span className="text-sm text-gray-400 ml-2">드래그 또는 화살표로 순서를 조정할 수 있습니다</span>
            </div>

            <div className="space-y-3">
              {priorityResults.map((result, index) => {
                const risk = RISK_BADGE[result.delayRisk] || RISK_BADGE.low;
                const RiskIcon = risk.icon;
                const isNotReady = result.readyStatus === "not_ready";

                return (
                  <div
                    key={result.orderId}
                    className={cn(
                      "bg-white rounded-xl border shadow-sm overflow-hidden transition-all",
                      isNotReady ? "border-red-300 ring-1 ring-red-200" : "border-gray-200",
                    )}
                  >
                    <div className="p-5">
                      <div className="flex items-start gap-4">
                        {/* 순위 */}
                        <div className="flex flex-col items-center gap-1">
                          <button
                            type="button"
                            disabled={index === 0}
                            onClick={() => moveItem(index, "up")}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-20"
                          >
                            <ChevronUp size={16} />
                          </button>
                          <div className={cn(
                            "w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold",
                            index === 0 ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600",
                          )}>
                            {result.rank}
                          </div>
                          <button
                            type="button"
                            disabled={index === priorityResults.length - 1}
                            onClick={() => moveItem(index, "down")}
                            className="p-1 rounded hover:bg-gray-100 disabled:opacity-20"
                          >
                            <ChevronDown size={16} />
                          </button>
                        </div>

                        {/* 주문 정보 */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-sm font-mono text-gray-400">{result.orderId}</span>
                            <span className="text-lg font-bold text-gray-900">{result.companyName}</span>

                            {/* 배지들 */}
                            <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border", risk.color)}>
                              <RiskIcon size={12} />
                              {risk.label}
                            </span>
                            {isNotReady && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700 border border-red-200">
                                <ShieldAlert size={12} />
                                착수 불가
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                            <span>{result.productSummary}</span>
                            <span>{result.totalQuantity.toLocaleString()}개</span>
                            <span>납기: {result.requestedDelivery || "미정"}</span>
                            <span>예상 {result.estimatedDays}일</span>
                          </div>

                          {/* 차단 사유 */}
                          {isNotReady && result.blockingReasons.length > 0 && (
                            <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-3">
                              <p className="text-xs font-semibold text-red-700 flex items-center gap-1 mb-1">
                                <XCircle size={12} /> 착수 불가 사유
                              </p>
                              {result.blockingReasons.map((reason, i) => (
                                <p key={i} className="text-xs text-red-600 ml-4">- {reason}</p>
                              ))}
                            </div>
                          )}

                          {/* 추천 사유 */}
                          <div className="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 mb-3">
                            <p className="text-xs text-blue-700 flex items-center gap-1">
                              <Info size={12} />
                              <span className="font-semibold">추천 사유:</span> {result.recommendationReason}
                            </p>
                          </div>

                          {/* 점수 분석 */}
                          <div className="grid grid-cols-2 gap-x-6 gap-y-1.5">
                            {result.factors.map((f) => (
                              <ScoreBar key={f.name} score={f.score} maxScore={f.maxScore} label={f.name} />
                            ))}
                          </div>
                        </div>

                        {/* 총점 */}
                        <div className="text-center shrink-0 pl-4 border-l border-gray-100">
                          <p className="text-xs text-gray-400 mb-1">총점</p>
                          <p className={cn(
                            "text-3xl font-bold",
                            result.totalScore >= 70 ? "text-blue-600" : result.totalScore >= 50 ? "text-amber-600" : "text-gray-500",
                          )}>
                            {result.totalScore}
                          </p>
                          <p className="text-xs text-gray-400">/ 100</p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ====== 승인 주문 선택 (하단) ====== */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">승인된 주문 목록</h2>
              <span className="ml-2 px-2.5 py-0.5 rounded-full text-sm font-semibold bg-blue-100 text-blue-700">
                {approvedOrders.length}건
              </span>
            </div>
            <button type="button" onClick={toggleAll} className="text-sm text-blue-600 hover:text-blue-800 font-medium">
              {selectedIds.size === approvedOrders.length ? "전체 해제" : "전체 선택"}
            </button>
          </div>

          {approvedOrders.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <CheckCircle2 size={40} strokeWidth={1.5} />
              <p className="mt-3 text-base">승인 대기 중인 주문이 없습니다.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {approvedOrders.map((order) => {
                const isSelected = selectedIds.has(order.id);
                return (
                  <button
                    key={order.id}
                    type="button"
                    onClick={() => toggleSelect(order.id)}
                    className={cn(
                      "w-full text-left px-5 py-4 flex items-center gap-4 transition-colors",
                      isSelected ? "bg-blue-50" : "hover:bg-gray-50",
                    )}
                  >
                    <div className={cn(
                      "w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors",
                      isSelected ? "bg-blue-600 border-blue-600" : "border-gray-300",
                    )}>
                      {isSelected && <CheckCircle2 size={14} className="text-white" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-mono text-gray-400">{order.id}</span>
                        <span className="text-base font-semibold text-gray-900">{order.companyName}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1"><Building2 size={12} /> {order.customerName}</span>
                        <span className="flex items-center gap-1"><Clock size={12} /> 납기: {order.requestedDelivery || "미정"}</span>
                        <span className="font-semibold text-gray-700">{formatCurrency(order.totalAmount)}</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* 모달 */}
      <ReasonModal
        open={reasonModal.open}
        onClose={() => setReasonModal({ open: false, orderId: "", oldRank: 0, newRank: 0 })}
        onSubmit={handleReasonSubmit}
      />
      <ConfirmStartModal
        open={confirmModal}
        count={priorityResults.length}
        onClose={() => setConfirmModal(false)}
        onConfirm={handleStartProduction}
        loading={starting}
      />
    </div>
  );
}
