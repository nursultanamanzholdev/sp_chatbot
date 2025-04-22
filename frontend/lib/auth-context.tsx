"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { useRouter } from "next/navigation"

// Backend URL
const BACKEND_URL = "https://chatbot-backend-iskc.onrender.com"

interface User {
  id: string
  name: string
  email: string
  phone?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem("auth_token")
      if (storedToken) {
        try {
          setIsLoading(true)
          const response = await fetch(`${BACKEND_URL}/api/users/profile`, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          })

          if (response.ok) {
            const userData = await response.json()
            setUser(userData)
            setToken(storedToken)
          } else {
            // Token is invalid or expired
            localStorage.removeItem("auth_token")
          }
        } catch (err) {
          console.error("Authentication error:", err)
        } finally {
          setIsLoading(false)
        }
      } else {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true)
      setError(null)

      const formData = new FormData()
      formData.append("username", email)
      formData.append("password", password)

      const response = await fetch(`${BACKEND_URL}/token`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Login failed")
      }

      const data = await response.json()
      localStorage.setItem("auth_token", data.access_token)
      setToken(data.access_token)
      
      // Get user profile
      const userResponse = await fetch(`${BACKEND_URL}/api/users/profile`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      })
      
      if (!userResponse.ok) {
        throw new Error("Failed to get user profile")
      }
      
      const userData = await userResponse.json()
      setUser(userData)
      router.push("/dashboard")
    } catch (err: any) {
      setError(err.message || "An error occurred during login")
    } finally {
      setIsLoading(false)
    }
  }

  const loginWithGoogle = async () => {
    try {
      setIsLoading(true)
      setError(null)
      // TODO: Implement Google login
      throw new Error("Google login not implemented yet")
    } catch (err: any) {
      setError(err.message || "An error occurred during Google login")
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem("auth_token")
    setToken(null)
    setUser(null)
    router.push("/")
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        error,
        login,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

