"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { LanguageSwitcher } from "@/components/language-switcher"
import { useLocale } from "@/lib/locale-context"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"

export default function LoginPage() {
  const { t } = useLocale()
  const { login, loginWithGoogle, isLoading, error } = useAuth()
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await login(email, password)
  }

  const handleGoogleLogin = async () => {
    await loginWithGoogle()
  }

  return (
    <div className="flex min-h-screen">
      {/* Left side with robot illustration */}
      <div className="hidden md:flex md:w-1/2 bg-[#f9f5ea] items-center justify-center p-8 relative">
        <div className="relative w-full h-full max-w-[600px] max-h-[600px]">
          <Image src="/robot-illustration3.png" alt="AI Learning Assistant" fill className="object-contain" priority />
        </div>
      </div>

      {/* Right side with login form */}
      <div className="w-full md:w-1/2 flex flex-col items-center justify-center p-8 bg-[#ffffff]">
        <div className="absolute top-4 right-4">
          <LanguageSwitcher />
        </div>

        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800">{t("loginToAccount")}</h1>
            <p className="mt-2 text-gray-600">{t("learnThroughConversations")}</p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button
            variant="outline"
            className="w-full border border-gray-300 py-6"
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Image src="/google-icon.svg" alt="Google" width={20} height={20} className="mr-2" />
            )}
            {t("continueWithGoogle")}
          </Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">{t("orSignInWithEmail")}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                {t("email")}
              </label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                className="mt-1 block w-full"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                {t("password")}
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••••"
                className="mt-1 block w-full"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Checkbox
                  id="remember"
                  checked={rememberMe}
                  onCheckedChange={(checked) => setRememberMe(checked === true)}
                />
                <label htmlFor="remember" className="ml-2 block text-sm text-gray-700">
                  {t("rememberMe")}
                </label>
              </div>
              <Link href="#" className="text-sm text-gray-600 hover:text-gray-900">
                {t("forgotPassword")}
              </Link>
            </div>

            <Button type="submit" className="w-full bg-[#e07a5f] hover:bg-[#d8684d] text-white" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {t("login")}
            </Button>
          </form>

          <div className="text-center mt-6">
            <p className="text-sm text-gray-600">
              {t("notRegistered")}{" "}
              <Link href="/register" className="font-medium text-[#e07a5f] hover:text-[#d8684d]">
                {t("createAccount")}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

