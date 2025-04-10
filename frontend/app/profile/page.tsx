"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"
import { useLocale } from "@/lib/locale-context"
import { userApi } from "@/lib/api"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { useToast } from "@/components/ui/use-toast"

interface ProfileData {
  name: string
  email: string
  phone: string
}

export default function ProfilePage() {
  const { t } = useLocale()
  const { toast } = useToast()

  const [profile, setProfile] = useState<ProfileData>({
    name: "",
    email: "",
    phone: "",
  })

  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true)
        const data = await userApi.getProfile()
        setProfile({
          name: data.name || "",
          email: data.email || "",
          phone: data.phone || "",
        })
      } catch (err: any) {
        setError(err.message || "Failed to load profile")
        toast({
          variant: "destructive",
          title: "Error",
          description: err.message || "Failed to load profile",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfile()
  }, [toast])

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setProfile((prev) => ({ ...prev, [name]: value }))
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setPasswords((prev) => ({ ...prev, [name]: value }))
  }

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      setIsSaving(true)
      await userApi.updateProfile(profile)
      toast({
        title: "Success",
        description: t("profileUpdated"),
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to update profile",
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (passwords.newPassword !== passwords.confirmPassword) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "New passwords do not match",
      })
      return
    }

    try {
      setIsChangingPassword(true)
      await userApi.changePassword({
        currentPassword: passwords.currentPassword,
        newPassword: passwords.newPassword,
      })

      // Reset password fields
      setPasswords({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })

      toast({
        title: "Success",
        description: t("passwordChanged"),
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to change password",
      })
    } finally {
      setIsChangingPassword(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 bg-[#f8f5f2]">
        <Header title={t("manageProfile")} />

        <main className="p-6">
          <div className="max-w-2xl mx-auto">
            {/* Loading state */}
            {isLoading && (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
                <span className="ml-2 text-gray-500">{t("loading")}</span>
              </div>
            )}

            {/* Error state */}
            {error && !isLoading && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{error}</div>
            )}

            {!isLoading && (
              <Card className="bg-white shadow-sm p-8">
                <form onSubmit={handleProfileSubmit} className="space-y-6">
                  <div className="space-y-1">
                    <Label htmlFor="name">{t("fullName")}</Label>
                    <Input
                      id="name"
                      name="name"
                      value={profile.name}
                      onChange={handleProfileChange}
                      placeholder={t("enterName")}
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="email">{t("emailAddress")}</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={profile.email}
                      onChange={handleProfileChange}
                      placeholder="name@example.com"
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="phone">{t("phoneNumber")}</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={profile.phone}
                      onChange={handleProfileChange}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>

                  <div className="flex justify-end pt-4">
                    <Button type="submit" className="bg-[#e07a5f] hover:bg-[#d8684d] text-white" disabled={isSaving}>
                      {isSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                      {t("save")}
                    </Button>
                  </div>
                </form>

                <div className="pt-8 border-t border-gray-200 mt-8">
                  <h3 className="text-lg font-medium mb-4">{t("changePassword")}</h3>

                  <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <div className="space-y-1">
                      <Label htmlFor="currentPassword">{t("currentPassword")}</Label>
                      <Input
                        id="currentPassword"
                        name="currentPassword"
                        type="password"
                        value={passwords.currentPassword}
                        onChange={handlePasswordChange}
                        placeholder="••••••••••"
                        required
                      />
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="newPassword">{t("newPassword")}</Label>
                      <Input
                        id="newPassword"
                        name="newPassword"
                        type="password"
                        value={passwords.newPassword}
                        onChange={handlePasswordChange}
                        placeholder="••••••••••"
                        required
                      />
                    </div>

                    <div className="space-y-1">
                      <Label htmlFor="confirmPassword">{t("confirmPassword")}</Label>
                      <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        value={passwords.confirmPassword}
                        onChange={handlePasswordChange}
                        placeholder="••••••••••"
                        required
                      />
                    </div>

                    <div className="flex justify-end pt-4">
                      <Button
                        type="submit"
                        className="bg-[#e07a5f] hover:bg-[#d8684d] text-white"
                        disabled={isChangingPassword}
                      >
                        {isChangingPassword ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                        {t("changePassword")}
                      </Button>
                    </div>
                  </form>
                </div>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

