"use client";

/**
 * 관리자 웹 허브 페이지.
 *
 * 기존 대시보드(모니터링용)는 PyQt5 monitoring 앱으로 분리됨
 * (Confluence 17956894 결정). 이 페이지는 관리자 업무 네비게이션 역할만 수행.
 *
 * 2026-04-08 개편: 생산 계획(우선순위 계산)과 입출고 내역 페이지를
 * PyQt5로 이관하여 웹 카드에서도 제거. 생산 승인은 주문 관리 페이지에서
 * 수행한다.
 */

import Link from "next/link";
import { ClipboardList, FlaskConical, Monitor } from "lucide-react";

const cards = [
  {
    href: "/orders",
    label: "주문 관리",
    desc: "주문 검토·승인·생산 승인 (우선순위 계산 대상 등록)",
    icon: ClipboardList,
    color: "from-emerald-500 to-teal-600",
  },
  {
    href: "/quality",
    label: "품질 관리",
    desc: "검사 기준 설정, 불량 분석, 품질 리포트",
    icon: FlaskConical,
    color: "from-purple-500 to-pink-600",
  },
] as const;

export default function AdminHomePage() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">관리자 포털</h1>
        <p className="mt-2 text-gray-600">
          주물공장 관제 시스템 관리자 웹. 실시간 모니터링과 생산 계획(우선순위 계산)은
          관제실 PyQt5 데스크톱 앱을 사용하세요.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {cards.map(({ href, label, desc, icon: Icon, color }) => (
          <Link
            key={href}
            href={href}
            className="group relative overflow-hidden rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:-translate-y-0.5"
          >
            <div
              className={`absolute top-0 left-0 h-1 w-full bg-gradient-to-r ${color}`}
            />
            <div className="flex items-start gap-4">
              <div
                className={`rounded-lg bg-gradient-to-br ${color} p-3 text-white`}
              >
                <Icon className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h2 className="text-lg font-semibold text-gray-900">{label}</h2>
                <p className="mt-1 text-sm text-gray-600">{desc}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
        <div className="flex items-start gap-4">
          <div className="rounded-lg bg-blue-600 p-3 text-white">
            <Monitor className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-blue-900">
              관제 모니터링 앱 (PyQt5 데스크톱)
            </h2>
            <p className="mt-1 text-sm text-blue-700">
              실시간 대시보드, 생산 모니터링, <strong>생산 계획(우선순위 계산)</strong>,
              품질 검사, 물류 이송 화면은 관제실 PyQt5 데스크톱 앱에서 제공됩니다.
            </p>
            <div className="mt-3 rounded-md bg-white px-4 py-3 font-mono text-xs text-gray-700 border border-blue-100">
              cd monitoring && python main.py
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
