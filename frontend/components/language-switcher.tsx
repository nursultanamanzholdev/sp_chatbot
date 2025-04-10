"use client"

import { useLocale } from "@/lib/locale-context"
import Link from "next/link"

export function LanguageSwitcher() {
  const { locale, setLocale } = useLocale()

  return (
    <div className="flex gap-4">
      <Link
        href="#"
        className={locale === "kz" ? "font-medium text-gray-900" : "text-gray-700 hover:text-gray-900"}
        onClick={(e) => {
          e.preventDefault()
          setLocale("kz")
        }}
      >
        Kaz
      </Link>
      <Link
        href="#"
        className={locale === "en" ? "font-medium text-gray-900" : "text-gray-700 hover:text-gray-900"}
        onClick={(e) => {
          e.preventDefault()
          setLocale("en")
        }}
      >
        Eng
      </Link>
    </div>
  )
}

