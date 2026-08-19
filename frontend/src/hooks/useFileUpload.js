/* ============================================================
   EDUMIND AI — FILE UPLOAD HOOK
   ============================================================ */

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { formatBytes } from '@utils/formatters'

export function useFileUpload({
  accept       = {},
  maxSize      = 20 * 1024 * 1024,
  multiple     = false,
  onFilesAdded = null,
} = {}) {
  const [files, setFiles]         = useState([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError]         = useState(null)

  const onDrop = useCallback(
    (accepted, rejected) => {
      setError(null)
      setIsDragOver(false)

      // Handle rejections
      if (rejected.length > 0) {
        const firstError = rejected[0].errors[0]
        if (firstError.code === 'file-too-large') {
          const msg = `[ SIZE ERROR ] File exceeds ${formatBytes(maxSize)} limit`
          setError(msg)
          toast.error(msg)
        } else if (firstError.code === 'file-invalid-type') {
          const msg = '[ TYPE ERROR ] File type not supported'
          setError(msg)
          toast.error(msg)
        } else {
          const msg = `[ ERROR ] ${firstError.message}`
          setError(msg)
          toast.error(msg)
        }
        return
      }

      // Accept files
      const newFiles = multiple
        ? [...files, ...accepted]
        : accepted

      setFiles(newFiles)

      if (onFilesAdded) {
        onFilesAdded(newFiles)
      }
    },
    [files, multiple, maxSize, onFilesAdded]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
    onDragEnter: () => setIsDragOver(true),
    onDragLeave: () => setIsDragOver(false),
  })

  // Remove file by index
  const removeFile = useCallback((index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  // Clear all files
  const clearFiles = useCallback(() => {
    setFiles([])
    setError(null)
  }, [])

  return {
    files,
    isDragOver: isDragOver || isDragActive,
    error,
    getRootProps,
    getInputProps,
    removeFile,
    clearFiles,
    hasFiles: files.length > 0,
  }
}

export default useFileUpload
