"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useLocale } from "@/lib/locale-context"

interface AddUserModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAddUser: (name: string, prompt: string, pdfFile: File | null, bookReference: string) => void
}

export function AddUserModal({ open, onOpenChange, onAddUser }: AddUserModalProps) {
  const [name, setName] = useState("")
  const [prompt, setPrompt] = useState("")
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [bookReference, setBookReference] = useState("")
  const { t } = useLocale()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (name.trim() && prompt.trim()) {
      onAddUser(name, prompt, pdfFile, bookReference)
      setName("")
      setPrompt("")
      setPdfFile(null)
      setBookReference("")
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{t("addNewUser")}</DialogTitle>
            <DialogDescription>{t("addUserDescription")}</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">{t("name")}</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t("enterName")}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="prompt">{t("learningPrompt")}</Label>
              <Textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={t("enterPrompt")}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="pdf">PDF Upload (Optional)</Label>
              <Input
                id="pdf"
                type="file"
                accept=".pdf"
                onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="bookReference">Book Reference (Optional)</Label>
              <Input
                id="bookReference"
                value={bookReference}
                onChange={(e) => setBookReference(e.target.value)}
                placeholder="Enter book reference"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {t("cancel")}
            </Button>
            <Button type="submit">{t("add")}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

