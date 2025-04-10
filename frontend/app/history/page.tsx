"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import { useLocale } from "@/lib/locale-context"
import { historyApi } from "@/lib/api"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { useToast } from "@/components/ui/use-toast"

interface HistoryItem {
  id: string
  userName: string
  title: string
  completedDate: string
  prompt: string
  summary: string
}

interface UserHistory {
  [userName: string]: HistoryItem[]
}

export default function HistoryPage() {
  const { t } = useLocale()
  const { toast } = useToast()
  const [history, setHistory] = useState<UserHistory>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setIsLoading(true)
        const data = await historyApi.getHistory()

        // Group history items by user name
        const groupedHistory: UserHistory = {}
        data.forEach((item: HistoryItem) => {
          if (!groupedHistory[item.userName]) {
            groupedHistory[item.userName] = []
          }
          groupedHistory[item.userName].push(item)
        })

        setHistory(groupedHistory)
      } catch (err: any) {
        setError(err.message || "Failed to load history")
        toast({
          variant: "destructive",
          title: "Error",
          description: err.message || "Failed to load history",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchHistory()
  }, [toast])

  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 bg-[#f8f5f2]">
        <Header title={t("learningHistory")} />

        <main className="p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Loading state */}
            {isLoading && (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
                <span className="ml-2 text-gray-500">{t("loading")}</span>
              </div>
            )}

            {/* Error state */}
            {error && !isLoading && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">{error}</div>
            )}

            {/* Empty state */}
            {!isLoading && !error && Object.keys(history).length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No learning history found.</p>
              </div>
            )}

            {/* History by user */}
            {!isLoading &&
              Object.entries(history).map(([userName, items]) => (
                <div key={userName}>
                  <h2 className="text-xl font-bold mb-4">{`${userName}'s ${t("learningHistory")}`}</h2>

                  <div className="space-y-4">
                    {items.map((item) => (
                      <Card key={item.id} className="bg-white shadow-sm p-6">
                        <div className="mb-2">
                          <h3 className="text-lg font-medium">{item.title}</h3>
                          <p className="text-sm text-gray-500">
                            {t("completed")}: {item.completedDate}
                          </p>
                        </div>

                        <div className="mt-4 bg-[#f8f5f2] p-4 rounded-md">
                          <p className="font-medium mb-2">{t("prompt")}:</p>
                          <p>{item.prompt}</p>
                        </div>

                        <div className="mt-4">
                          <p className="font-medium mb-2">{t("summary")}:</p>
                          <p className="text-gray-700">{item.summary}</p>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        </main>
      </div>
    </div>
  )
}

