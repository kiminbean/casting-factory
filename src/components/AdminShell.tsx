"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

export default function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isCustomerPage = pathname.startsWith("/customer");

  if (isCustomerPage) {
    return <>{children}</>;
  }

  return (
    <>
      <Sidebar />
      <div className="ml-64 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </>
  );
}
