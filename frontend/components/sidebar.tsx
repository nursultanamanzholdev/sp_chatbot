"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Clock, Sparkles, User } from "lucide-react"
import { useLocale } from "@/lib/locale-context"

export function Sidebar() {
  const pathname = usePathname()
  const { t } = useLocale()

  return (
    <div className="w-[280px] border-r border-gray-200 bg-white">
      <div className="p-6">
        <button className="md:hidden mb-6">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M3 12H21M3 6H21M3 18H21"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <nav className="px-4 py-2">
        <Link
          href="/dashboard"
          className={`flex items-center px-4 py-3 rounded-lg ${
            pathname === "/dashboard" ? "text-gray-900 bg-gray-100" : "text-gray-700 hover:bg-gray-100"
          }`}
        >
          <Sparkles className="w-5 h-5 mr-3" />
          <span className="text-lg font-medium">{t("personalize")}</span>
        </Link>

        <Link
          href="/history"
          className={`flex items-center px-4 py-3 rounded-lg ${
            pathname === "/history" ? "text-gray-900 bg-gray-100" : "text-gray-700 hover:bg-gray-100"
          }`}
        >
          <Clock className="w-5 h-5 mr-3" />
          <span className="text-lg font-medium">{t("history")}</span>
        </Link>

        <Link
          href="/profile"
          className={`flex items-center px-4 py-3 rounded-lg ${
            pathname === "/profile" ? "text-gray-900 bg-gray-100" : "text-gray-700 hover:bg-gray-100"
          }`}
        >
          <User className="w-5 h-5 mr-3" />
          <span className="text-lg font-medium">{t("manageProfile")}</span>
        </Link>
      </nav>
    </div>
  )
}

