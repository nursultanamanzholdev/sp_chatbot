"use client"
import { useAuth } from "@/lib/auth-context"
import { LanguageSwitcher } from "@/components/language-switcher"
import { useLocale } from "@/lib/locale-context"
import { Button } from "@/components/ui/button"
import { LogOut } from "lucide-react"

interface HeaderProps {
  title: string
}

export function Header({ title }: HeaderProps) {
  const { logout } = useAuth()
  const { t } = useLocale()

  return (
    <header className="flex justify-between items-center p-6 border-b border-gray-200 bg-[#f8f5f2]">
      <button className="md:hidden">
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

      <h1 className="text-2xl font-bold text-center flex-1 md:text-left md:flex-none">{title}</h1>

      <div className="flex items-center gap-4">
        <LanguageSwitcher />
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-2 text-gray-700 hover:text-gray-900"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          <span>{t("signOut")}</span>
        </Button>
      </div>
    </header>
  )
}

