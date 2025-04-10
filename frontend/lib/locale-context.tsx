"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

type Locale = "en" | "kz"

interface LocaleContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
}

const translations = {
  en: {
    // Common
    login: "Login",
    cancel: "Cancel",
    add: "Add",
    save: "Save Changes",
    signOut: "Sign Out",
    loading: "Loading...",
    error: "An error occurred",
    delete: "Delete",
    edit: "Edit",

    // Login page
    loginToAccount: "Login to your Account",
    learnThroughConversations: "Learn through joyful conversations!",
    continueWithGoogle: "Continue with Google",
    orSignInWithEmail: "or Sign in with Email",
    email: "Email",
    password: "Password",
    rememberMe: "Remember Me",
    forgotPassword: "Forgot Password?",
    notRegistered: "Not Registered Yet?",
    createAccount: "Create an account",

    // Dashboard
    personalizeLearn: "Personalize Learning",
    personalize: "Personalize",
    history: "History",
    manageProfile: "Manage Profile",
    addNewUser: "Add New User",
    addUserDescription: "Create a new user and set their learning prompt.",
    name: "Name",
    enterName: "Enter user name",
    learningPrompt: "Learning Prompt",
    enterPrompt: "Enter learning prompt",
    lastModified: "Last Modified",
    deletePrompt: "Delete Prompt",
    editPrompt: "Edit Prompt",
    confirmDelete: "Are you sure you want to delete this prompt?",

    // History
    learningHistory: "Learning History",
    completed: "Completed",
    prompt: "Prompt",
    summary: "Summary",

    // Profile
    fullName: "Full Name",
    emailAddress: "Email Address",
    phoneNumber: "Phone Number",
    changePassword: "Change Password",
    currentPassword: "Current Password",
    newPassword: "New Password",
    confirmPassword: "Confirm New Password",
    profileUpdated: "Profile updated successfully",
    passwordChanged: "Password changed successfully",

    // User specific
    emmasLearningPrompt: "Emma's Learning Prompt",
    marksLearningPrompt: "Mark's Learning Prompt",
    emmasLearningHistory: "Emma's Learning History",
    marksLearningHistory: "Mark's Learning History",
  },
  kz: {
    // Common
    login: "Кіру",
    cancel: "Болдырмау",
    add: "Қосу",
    save: "Өзгерістерді сақтау",
    signOut: "Шығу",
    loading: "Жүктелуде...",
    error: "Қате орын алды",
    delete: "Жою",
    edit: "Өңдеу",

    // Login page
    loginToAccount: "Аккаунтқа кіру",
    learnThroughConversations: "Қуанышты әңгімелер арқылы үйреніңіз!",
    continueWithGoogle: "Google арқылы жалғастыру",
    orSignInWithEmail: "немесе Email арқылы кіріңіз",
    email: "Электрондық пошта",
    password: "Құпия сөз",
    rememberMe: "Мені есте сақтау",
    forgotPassword: "Құпия сөзді ұмыттыңыз ба?",
    notRegistered: "Әлі тіркелмегенсіз бе?",
    createAccount: "Аккаунт жасау",

    // Dashboard
    personalizeLearn: "Оқуды жекелендіру",
    personalize: "Жекелендіру",
    history: "Тарих",
    manageProfile: "Профильді басқару",
    addNewUser: "Жаңа қолданушы қосу",
    addUserDescription: "Жаңа қолданушы жасап, оқу тапсырмасын орнатыңыз.",
    name: "Аты",
    enterName: "Қолданушы атын енгізіңіз",
    learningPrompt: "Оқу тапсырмасы",
    enterPrompt: "Оқу тапсырмасын енгізіңіз",
    lastModified: "Соңғы өзгерту",
    deletePrompt: "Тапсырманы жою",
    editPrompt: "Тапсырманы өңдеу",
    confirmDelete: "Бұл тапсырманы жойғыңыз келетініне сенімдісіз бе?",

    // History
    learningHistory: "Оқу тарихы",
    completed: "Аяқталды",
    prompt: "Тапсырма",
    summary: "Қорытынды",

    // Profile
    fullName: "Толық аты-жөні",
    emailAddress: "Электрондық пошта",
    phoneNumber: "Телефон нөмірі",
    changePassword: "Құпия сөзді өзгерту",
    currentPassword: "Ағымдағы құпия сөз",
    newPassword: "Жаңа құпия сөз",
    confirmPassword: "Жаңа құпия сөзді растау",
    profileUpdated: "Профиль сәтті жаңартылды",
    passwordChanged: "Құпия сөз сәтті өзгертілді",

    // User specific
    emmasLearningPrompt: "Эмманың оқу тапсырмасы",
    marksLearningPrompt: "Марктың оқу тапсырмасы",
    emmasLearningHistory: "Эмманың оқу тарихы",
    marksLearningHistory: "Марктың оқу тарихы",
  },
}

const LocaleContext = createContext<LocaleContextType | undefined>(undefined)

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en")

  // Load saved locale from localStorage on initial render
  useEffect(() => {
    const savedLocale = localStorage.getItem("locale") as Locale
    if (savedLocale && (savedLocale === "en" || savedLocale === "kz")) {
      setLocale(savedLocale)
    }
  }, [])

  // Save locale to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("locale", locale)
  }, [locale])

  const t = (key: string): string => {
    return translations[locale][key as keyof (typeof translations)[typeof locale]] || key
  }

  return <LocaleContext.Provider value={{ locale, setLocale, t }}>{children}</LocaleContext.Provider>
}

export function useLocale() {
  const context = useContext(LocaleContext)
  if (context === undefined) {
    throw new Error("useLocale must be used within a LocaleProvider")
  }
  return context
}

