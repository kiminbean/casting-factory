import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AdminShell from "@/components/AdminShell";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "주물공장 생산 관제 시스템",
  description: "주물 생산 공정 실시간 모니터링 대시보드",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${inter.variable} h-full`}>
      <body className="h-full bg-gray-50 antialiased">
        <AdminShell>{children}</AdminShell>
      </body>
    </html>
  );
}
