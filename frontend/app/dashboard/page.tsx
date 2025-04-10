"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Pencil, Plus, Trash2, Loader2 } from "lucide-react"
import { AddUserModal } from "@/components/add-user-modal"
import { useLocale } from "@/lib/locale-context"
import { promptsApi, pdfBooksApi } from "@/lib/api"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"

interface LearningPrompt {
  id: string
  name: string
  prompt: string
  lastModified: string
  pdf_book?: {
    id: number
    book_reference: string
    filename: string
  } | null
}

export default function DashboardPage() {
  const { t } = useLocale()
  const { toast } = useToast()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [prompts, setPrompts] = useState<LearningPrompt[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPrompt, setSelectedPrompt] = useState<LearningPrompt | null>(null)
  const [editPromptText, setEditPromptText] = useState("")

  // Fetch prompts on component mount
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setIsLoading(true)
        const data = await promptsApi.getPrompts()
        setPrompts(data)
      } catch (err: any) {
        setError(err.message || "Failed to load prompts")
        toast({
          variant: "destructive",
          title: "Error",
          description: err.message || "Failed to load prompts",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchPrompts()
  }, [toast])

  const handleAddUser = async (name: string, prompt: string, pdfFile: File | null, bookReference: string) => {
    try {
      setIsLoading(true)
      
      // First create the prompt
      const newPrompt = await promptsApi.createPrompt({ name, prompt })
      
      // If PDF file and reference are provided, upload the PDF
      if (pdfFile && bookReference.trim()) {
        try {
          const pdfBook = await pdfBooksApi.uploadPDFBook(pdfFile, bookReference, parseInt(newPrompt.id))
          newPrompt.pdf_book = pdfBook
          toast({
            title: "Success",
            description: "User prompt and PDF book added successfully",
          })
        } catch (pdfErr: any) {
          // If PDF upload fails, still show success for prompt but warn about PDF
          toast({
            variant: "destructive",
            title: "Warning",
            description: `User prompt added but PDF upload failed: ${pdfErr.message || "Unknown error"}`
          })
        }
      } else {
        toast({
          title: "Success",
          description: "New user prompt added successfully",
        })
      }
      
      setPrompts([...prompts, newPrompt])
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to add user",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeletePDFBook = async (promptId: string, pdfId: number) => {
    try {
      setIsLoading(true)
      await pdfBooksApi.deletePDFBook(pdfId)
      
      // Update the local state to remove the PDF book reference
      setPrompts(prompts.map(p => {
        if (p.id === promptId) {
          return { ...p, pdf_book: null }
        }
        return p
      }))
      
      toast({
        title: "Success",
        description: "PDF book deleted successfully",
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to delete PDF book",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeletePrompt = async () => {
    if (!selectedPrompt) return

    try {
      setIsLoading(true)
      await promptsApi.deletePrompt(selectedPrompt.id)
      setPrompts(prompts.filter((p) => p.id !== selectedPrompt.id))
      setIsDeleteDialogOpen(false)
      setSelectedPrompt(null)
      toast({
        title: "Success",
        description: "Prompt deleted successfully",
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to delete prompt",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleEditPrompt = async () => {
    if (!selectedPrompt || !editPromptText.trim()) return

    try {
      setIsLoading(true)
      const updatedPrompt = await promptsApi.updatePrompt(selectedPrompt.id, { prompt: editPromptText })
      setPrompts(
        prompts.map((p) =>
          p.id === selectedPrompt.id
            ? {
                ...p,
                prompt: editPromptText,
                lastModified: new Date().toISOString().split("T")[0],
              }
            : p,
        ),
      )
      setIsEditDialogOpen(false)
      setSelectedPrompt(null)
      toast({
        title: "Success",
        description: "Prompt updated successfully",
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to update prompt",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const openDeleteDialog = (prompt: LearningPrompt) => {
    setSelectedPrompt(prompt)
    setIsDeleteDialogOpen(true)
  }

  const openEditDialog = (prompt: LearningPrompt) => {
    setSelectedPrompt(prompt)
    setEditPromptText(prompt.prompt)
    setIsEditDialogOpen(true)
  }

  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 bg-[#f8f5f2]">
        <Header title={t("personalizeLearn")} />

        <main className="p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex justify-between items-start">
              <div className="flex-1"></div>
              <Button
                className="bg-[#1d3557] hover:bg-[#152538] text-white"
                onClick={() => setIsModalOpen(true)}
                disabled={isLoading}
              >
                <Plus className="w-5 h-5 mr-2" />
                {t("addNewUser")}
              </Button>
            </div>

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
            {!isLoading && !error && prompts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No prompts found. Add a new user to get started.</p>
              </div>
            )}

            {/* Learning prompts */}
            {!isLoading &&
              prompts.map((item) => (
                <Card key={item.id} className="bg-white shadow-sm p-6">
                  <div className="mb-2">
                    <h2 className="text-xl font-bold">{`${item.name}'s ${t("learningPrompt")}`}</h2>
                    <p className="text-sm text-gray-500">
                      {t("lastModified")}: {item.lastModified}
                    </p>
                  </div>

                  <div className="mt-4 bg-[#f8f5f2] p-4 rounded-md">
                    <div className="flex justify-between items-center">
                      <p>{item.prompt}</p>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(item)} title={t("editPrompt")}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openDeleteDialog(item)}
                          title={t("deletePrompt")}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                    {item.pdf_book && (
                      <div className="mt-2 pt-2 border-t border-gray-200 flex justify-between items-center">
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Book Reference:</span> {item.pdf_book.book_reference}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeletePDFBook(item.id, item.pdf_book!.id)}
                          className="text-red-500 hover:text-red-600"
                        >
                          Remove Book
                        </Button>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
          </div>
        </main>
      </div>

      {/* Add User Modal */}
      <AddUserModal open={isModalOpen} onOpenChange={setIsModalOpen} onAddUser={handleAddUser} />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("deletePrompt")}</AlertDialogTitle>
            <AlertDialogDescription>{t("confirmDelete")}</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isLoading}>{t("cancel")}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeletePrompt}
              disabled={isLoading}
              className="bg-red-500 hover:bg-red-600"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {t("delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Edit Prompt Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("editPrompt")}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-prompt">{t("learningPrompt")}</Label>
              <Textarea
                id="edit-prompt"
                value={editPromptText}
                onChange={(e) => setEditPromptText(e.target.value)}
                placeholder={t("enterPrompt")}
                className="min-h-[100px]"
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={isLoading}>
              {t("cancel")}
            </Button>
            <Button onClick={handleEditPrompt} disabled={isLoading || !editPromptText.trim()}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {t("save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

