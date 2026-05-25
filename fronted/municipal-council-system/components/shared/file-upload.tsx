'use client'

import { useCallback, useState } from 'react'
import { useDropzone, type FileRejection } from 'react-dropzone'
import { Upload, X, FileSpreadsheet } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  accept?: Record<string, string[]>
  maxSize?: number
  className?: string
}

export function FileUpload({
  onFileSelect,
  accept = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-excel': ['.xls'],
  },
  maxSize = 10 * 1024 * 1024, // 10 MB
  className,
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      setError(null)
      if (rejectedFiles.length > 0) {
        setError(rejectedFiles[0].errors[0]?.message ?? 'Archivo no válido')
        return
      }
      if (acceptedFiles[0]) {
        setSelectedFile(acceptedFiles[0])
        onFileSelect(acceptedFiles[0])
      }
    },
    [onFileSelect],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  })

  function removeFile(e: React.MouseEvent) {
    e.stopPropagation()
    setSelectedFile(null)
    setError(null)
  }

  return (
    <div className={className}>
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50 hover:bg-muted/30',
          selectedFile && 'border-primary/40 bg-primary/5',
        )}
      >
        <input {...getInputProps()} />
        {selectedFile ? (
          <div className="flex items-center justify-center gap-3">
            <FileSpreadsheet className="w-8 h-8 text-primary flex-shrink-0" />
            <div className="text-left min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="ml-2 h-7 w-7 p-0 flex-shrink-0"
              onClick={removeFile}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-8 h-8 text-muted-foreground mx-auto" />
            <p className="text-sm font-medium text-foreground">
              {isDragActive ? 'Suelte el archivo aquí' : 'Arrastre un archivo o haga clic'}
            </p>
            <p className="text-xs text-muted-foreground">
              Excel (.xlsx, .xls) hasta {(maxSize / 1024 / 1024).toFixed(0)} MB
            </p>
          </div>
        )}
      </div>
      {error && <p className="text-xs text-destructive mt-1.5">{error}</p>}
    </div>
  )
}
