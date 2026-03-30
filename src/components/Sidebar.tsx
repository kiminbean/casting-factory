"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Activity,
  ClipboardList,
  FlaskConical,
  Truck,
  Factory,
} from "lucide-react";

const navItems = [
  { href: "/", label: "대시보드", icon: LayoutDashboard },
  { href: "/production", label: "생산 모니터링", icon: Activity },
  { href: "/orders", label: "주문 관리", icon: ClipboardList },
  { href: "/quality", label: "품질 검사", icon: FlaskConical },
  { href: "/logistics", label: "물류/이송", icon: Truck },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-gray-900 text-white flex flex-col z-30">
      {/* Logo area */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-700">
        <Factory className="h-7 w-7 text-blue-400 shrink-0" />
        <span className="text-lg font-bold tracking-tight text-white">
          주물공장 관제
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={[
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white",
                  ].join(" ")}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
