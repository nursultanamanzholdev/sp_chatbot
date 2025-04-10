"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface BookUploadModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpload: (file: File, bookReference: string) => void
}

export function BookUploadModal({ open, onOpenChange, onUpload }: BookUploadModalProps) {
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [bookReference, setBookReference] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (pdfFile && bookReference.trim()) {
      onUpload(pdfFile, bookReference)
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
            <DialogTitle>Add Book to Prompt</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="bookReference">Book Reference</Label>
              <Input
                id="bookReference"
                value={bookReference}
                onChange={(e) => setBookReference(e.target.value)}
                placeholder="Enter book reference"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="pdf">PDF File</Label>
              <Input
                id="pdf"
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    setPdfFile(file)
                    // Auto-fill book reference with filename if empty
                    if (!bookReference) {
                      setBookReference(file.name.replace(/\.pdf$/, ''))
                    }
                  }
                }}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={!pdfFile || !bookReference.trim()}>
              Upload
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
