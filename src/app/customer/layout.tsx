import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "../globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "주물공장 온라인 발주 시스템",
  description: "주물공장 온라인 발주 시스템 - 제품 선택부터 주문 완료까지",
};

export default function CustomerLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${inter.variable} h-full`}>
      <body className="h-full bg-gray-50 antialiased">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link
                href="/customer"
                className="flex items-center gap-2 text-blue-600 font-bold text-lg hover:text-blue-700 transition-colors"
              >
                <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                    />
                  </svg>
                </div>
                주물공장 온라인 발주
              </Link>

              {/* Navigation Links */}
              <nav>
                <Link
                  href="/customer/orders"
                  className="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors px-3 py-2 rounded-md hover:bg-blue-50"
                >
                  주문 조회
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="min-h-[calc(100vh-4rem-5rem)]">{children}</main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  주물공장
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  고품질 주물 제품 전문 제조업체
                  <br />
                  KS 인증 제품 공급
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  연락처
                </h3>
                <ul className="space-y-1 text-sm text-gray-500">
                  <li>전화: 02-1234-5678</li>
                  <li>팩스: 02-1234-5679</li>
                  <li>이메일: order@castingfactory.co.kr</li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  영업시간
                </h3>
                <ul className="space-y-1 text-sm text-gray-500">
                  <li>평일 09:00 - 18:00</li>
                  <li>토요일 09:00 - 13:00</li>
                  <li>일요일 및 공휴일 휴무</li>
                </ul>
              </div>
            </div>
            <div className="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-400">
              © 2026 주물공장. All rights reserved.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
