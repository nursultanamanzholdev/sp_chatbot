"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Pencil, Plus, Trash2, Loader2, Upload, CheckCircle, AlertCircle, Clock } from "lucide-react"
import { AddUserModal } from "@/components/add-user-modal"
import { BookUploadModal } from "@/components/book-upload-modal"
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface PDFBookStatus {
  status: string;
  message?: string;
}

interface PDFBook {
  id: number;
  book_reference: string;
  filename: string;
  json_content?: any;
}

interface LearningPrompt {
  id: string
  name: string
  prompt: string
  mode: string
  created_at: string
  updated_at: string | null
  pdf_book?: PDFBook | null
}

export default function DashboardPage() {
  const { t } = useLocale()
  const { toast } = useToast()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isBookUploadOpen, setIsBookUploadOpen] = useState(false)
  const [prompts, setPrompts] = useState<LearningPrompt[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPrompt, setSelectedPrompt] = useState<LearningPrompt | null>(null)
  const [editPromptText, setEditPromptText] = useState("")
  const [pdfStatuses, setPdfStatuses] = useState<Record<number, PDFBookStatus>>({})
  const [statusPollingInterval, setStatusPollingInterval] = useState<NodeJS.Timeout | null>(null)

  // Fetch prompts on component mount
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setIsLoading(true)
        const data = await promptsApi.getPrompts()
        setPrompts(data)
        
        // Check for any PDFs with books
        const pdfIds = data
          .filter(prompt => prompt.pdf_book)
          .map(prompt => prompt.pdf_book?.id)
          .filter(Boolean) as number[]
          
        if (pdfIds.length > 0) {
          // Check status for each PDF
          for (const pdfId of pdfIds) {
            checkPdfStatus(pdfId)
          }
          
          // Set up polling for all PDFs
          startStatusPolling()
        }
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
    
    // Cleanup polling interval on unmount
    return () => {
      if (statusPollingInterval) {
        clearInterval(statusPollingInterval)
      }
    }
  }, [toast])
  
  // Start polling for PDF status updates
  const startStatusPolling = () => {
    // Clear any existing interval
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval)
    }
    
    // Set up a new polling interval
    const interval = setInterval(async () => {
      // Get all PDF IDs from prompts
      const pdfIds = prompts
        .filter(prompt => prompt.pdf_book)
        .map(prompt => prompt.pdf_book?.id)
        .filter(Boolean) as number[]
      
      // Check if we have any PDFs in processing status
      const processingIds = Object.entries(pdfStatuses)
        .filter(([_, status]: [string, PDFBookStatus]) => status.status === "processing")
        .map(([id]: [string, any]) => parseInt(id))
      
      // If we have processing PDFs, check their status
      if (processingIds.length > 0) {
        for (const id of processingIds) {
          await checkPdfStatus(id)
        }
      } else if (pdfIds.length > 0) {
        // If no processing PDFs but we have PDFs, check their status anyway
        // This handles cases where the page was refreshed and we don't know the status
        for (const id of pdfIds) {
          if (!pdfStatuses[id] || !["complete", "error"].includes(pdfStatuses[id].status)) {
            await checkPdfStatus(id)
          }
        }
      } else {
        // If no PDFs at all, clear the interval
        clearInterval(statusPollingInterval!)
        setStatusPollingInterval(null)
      }
    }, 3000) // Check every 3 seconds
    
    setStatusPollingInterval(interval)
  }
  
  const checkPdfStatus = async (pdfId: number) => {
    try {
      const status = await pdfBooksApi.getPDFBookStatus(pdfId)
      
      // Update the status in state
      setPdfStatuses(prev => ({
        ...prev,
        [pdfId]: status
      }))
      
      // If status changed to complete or error, refresh the prompts
      if (status.status === "complete" || status.status === "error") {
        const updatedPrompts = await promptsApi.getPrompts()
        setPrompts(updatedPrompts)
        
        if (status.status === "complete") {
          toast({
            title: "PDF Processing Complete",
            description: "The PDF has been successfully processed and saved.",
          })
        } else if (status.status === "error") {
          toast({
            variant: "destructive",
            title: "PDF Processing Error",
            description: status.message || "An error occurred while processing the PDF.",
          })
        }
      }
      
      return status
    } catch (err) {
      console.error("Error checking PDF status:", err)
      return { status: "error", message: "Failed to check status" }
    }
  }

  const handleAddUser = async (name: string, prompt: string, pdfFile: File | null, bookReference: string, mode: string) => {
    try {
      setIsLoading(true)
      
      // First create the prompt
      const newPrompt = await promptsApi.createPrompt({ name, prompt, mode })
      
      // If PDF file and reference are provided, upload the PDF
      if (pdfFile && bookReference.trim()) {
        try {
          const pdfBook = await pdfBooksApi.uploadPDFBook(pdfFile, bookReference, parseInt(newPrompt.id))
          newPrompt.pdf_book = pdfBook
          
          // Start polling for status
          checkPdfStatus(pdfBook.id)
          startStatusPolling()
          
          toast({
            title: "Processing PDF",
            description: "Your PDF is being processed. This may take a few minutes.",
          })
        } catch (pdfErr: any) {
          console.error("Error uploading PDF:", pdfErr)
          toast({
            variant: "destructive",
            title: "PDF Upload Error",
            description: pdfErr.message || "Failed to upload PDF",
          })
        }
      }
      
      // Add the new prompt to the list
      setPrompts((prevPrompts) => [...prevPrompts, newPrompt])
      
      toast({
        title: "Success",
        description: "New prompt has been created",
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to create prompt",
      })
    } finally {
      setIsLoading(false)
      setIsModalOpen(false)
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
    if (!selectedPrompt || !editPromptText) return
    
    try {
      setIsLoading(true)
      const updatedPrompt = await promptsApi.updatePrompt(
        selectedPrompt.id,
        { 
          prompt: editPromptText,
          mode: selectedPrompt.mode 
        }
      )
      
      // Update the prompts list with the edited prompt
      setPrompts((prevPrompts) =>
        prevPrompts.map((p) => (p.id === selectedPrompt.id ? updatedPrompt : p))
      )
      
      setIsEditDialogOpen(false)
      toast({
        title: "Success",
        description: "Prompt has been updated",
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
                      {t("lastModified")}: {new Date(item.updated_at || item.created_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="mt-4 bg-[#f8f5f2] p-4 rounded-md">
                    <div className="flex flex-col gap-2">
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

                    </div>
                    {item.pdf_book ? (
                      <div className="mt-2 p-2 bg-gray-50 rounded-md">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-semibold">{item.pdf_book.book_reference}</p>
                            <p className="text-xs text-gray-500">{item.pdf_book.filename}</p>
                          </div>
                          <div className="flex items-center">
                            {/* Processing status indicator */}
                            {pdfStatuses[item.pdf_book.id]?.status === "processing" && (
                              <div className="flex items-center mr-3">
                                <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2 animate-pulse"></div>
                                <span className="text-sm font-medium text-yellow-700">Processing...</span>
                              </div>
                            )}
                            
                            {/* Complete status indicator */}
                            {pdfStatuses[item.pdf_book.id]?.status === "complete" && (
                              <div className="flex items-center mr-3">
                                <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                                <span className="text-sm font-medium text-green-700">Saved</span>
                              </div>
                            )}
                            
                            {/* Error status indicator */}
                            {pdfStatuses[item.pdf_book.id]?.status === "error" && (
                              <div className="flex items-center mr-3" title={pdfStatuses[item.pdf_book.id]?.message}>
                                <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                                <span className="text-sm font-medium text-red-700">Error</span>
                              </div>
                            )}
                            
                            {/* No status yet - check if json_content has a status */}
                            {!pdfStatuses[item.pdf_book.id] && item.pdf_book.json_content?.status === "processing" && (
                              <div className="flex items-center mr-3">
                                <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2 animate-pulse"></div>
                                <span className="text-sm font-medium text-yellow-700">Processing...</span>
                              </div>
                            )}
                            
                            {!pdfStatuses[item.pdf_book.id] && item.pdf_book.json_content?.status === "complete" && (
                              <div className="flex items-center mr-3">
                                <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                                <span className="text-sm font-medium text-green-700">Ready</span>
                              </div>
                            )}
                            
                            {!pdfStatuses[item.pdf_book.id] && item.pdf_book.json_content?.status === "error" && (
                              <div className="flex items-center mr-3" title={item.pdf_book.json_content?.message}>
                                <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                                <span className="text-sm font-medium text-red-700">Error</span>
                              </div>
                            )}
                            
                            {/* If no status at all, show unknown */}
                            {!pdfStatuses[item.pdf_book.id] && !item.pdf_book.json_content?.status && (
                              <div className="flex items-center mr-3">
                                <div className="w-3 h-3 rounded-full bg-gray-500 mr-2"></div>
                                <span className="text-sm font-medium text-gray-700">Unknown</span>
                              </div>
                            )}
                            
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeletePDFBook(item.id, item.pdf_book?.id || 0)}
                              className="text-red-500 hover:text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-2 pt-2 border-t border-gray-200 flex justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedPrompt(item)
                            setIsBookUploadOpen(true)
                          }}
                          className="text-blue-500 hover:text-blue-600"
                        >
                          <Upload className="h-4 w-4 mr-2" />
                          Add Book
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
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{t("editPrompt")}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="editPrompt">{t("prompt")}</Label>
              <Textarea
                id="editPrompt"
                value={editPromptText}
                onChange={(e) => setEditPromptText(e.target.value)}
                className="h-32"
              />
            </div>
            <div className="grid gap-2">
              <Label>Interaction Mode</Label>
              <RadioGroup 
                value={selectedPrompt?.mode || "chat"} 
                onValueChange={(value) => {
                  if (selectedPrompt) {
                    setSelectedPrompt({...selectedPrompt, mode: value});
                  }
                }}
                className="flex space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="chat" id="edit-chat" />
                  <Label htmlFor="edit-chat" className="cursor-pointer">Chat Mode</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="lecture" id="edit-lecture" />
                  <Label htmlFor="edit-lecture" className="cursor-pointer">Lecture Mode</Label>
                </div>
              </RadioGroup>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              {t("cancel")}
            </Button>
            <Button onClick={handleEditPrompt} disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {t("save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
