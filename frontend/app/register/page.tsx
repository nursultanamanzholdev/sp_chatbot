"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LanguageSwitcher } from "@/components/language-switcher"
import { useLocale } from "@/lib/locale-context"
import { useRouter } from "next/navigation"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"

// Backend URL
const BACKEND_URL = "https://chatbot-backend-iskc.onrender.com"

export default function RegisterPage() {
  const { t } = useLocale()
  const router = useRouter()

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }
    
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${BACKEND_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Registration failed")
      }
      
      // Registration successful, redirect to login
      router.push("/")
    } catch (err: any) {
      setError(err.message || "An error occurred during registration")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left side with robot illustration */}
      <div className="hidden md:flex md:w-1/2 bg-[#f9f5ea] items-center justify-center p-8 relative">
        <div className="relative w-full h-full max-w-[600px] max-h-[600px]">
          <Image src="/robot-illustration3.png" alt="AI Learning Assistant" fill className="object-contain" priority />
        </div>
      </div>

      {/* Right side with registration form */}
      <div className="w-full md:w-1/2 flex flex-col items-center justify-center p-8 bg-[#ffffff]">
        <div className="absolute top-4 right-4">
          <LanguageSwitcher />
        </div>

        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800">{t("createAccount") || "Create an Account"}</h1>
            <p className="mt-2 text-gray-600">{t("learnThroughConversations") || "Learn through joyful conversations!"}</p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                {t("name") || "Name"}
              </label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                className="mt-1 block w-full"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                {t("email") || "Email"}
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
                {t("password") || "Password"}
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
            
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                {t("confirmPassword") || "Confirm Password"}
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••••"
                className="mt-1 block w-full"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full bg-[#e07a5f] hover:bg-[#d8684d] text-white" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {t("register") || "Register"}
            </Button>
          </form>

          <div className="text-center mt-6">
            <p className="text-sm text-gray-600">
              {t("alreadyHaveAccount") || "Already have an account?"}{" "}
              <Link href="/" className="font-medium text-[#e07a5f] hover:text-[#d8684d]">
                {t("login") || "Login"}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 