import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { FiUploadCloud, FiFile, FiX } from 'react-icons/fi'
import Button from '@components/ui/Button'
import { formatFileSize } from '@utils/formatters'
import { classNames } from '@utils/helpers'

export default function DocumentUpload({
  onFileSelect,
  selectedFile,
  onClear,
  accept = { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] },
  maxSizeMB = 10,
}) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
  })

  if (selectedFile) {
    return (
      <div className="flex items-center gap-4 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl border border-primary-200 dark:border-primary-800">
        <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/40 rounded-xl flex items-center justify-center flex-shrink-0">
          <FiFile className="w-6 h-6 text-primary-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 dark:text-white truncate">
            {selectedFile.name}
          </p>
          <p className="text-sm text-gray-500">
            {formatFileSize(selectedFile.size)}
          </p>
        </div>
        <button
          onClick={onClear}
          className="p-2 hover:bg-primary-100 dark:hover:bg-primary-900/40 rounded-lg transition-colors"
        >
          <FiX className="w-4 h-4 text-gray-500" />
        </button>
      </div>
    )
  }

  return (
    <div
      {...getRootProps()}
      className={classNames(
        'border-2 border-dashed rounded-xl p-8',
        'flex flex-col items-center justify-center gap-4',
        'cursor-pointer transition-all duration-200',
        isDragActive
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
      )}
    >
      <input {...getInputProps()} />
      <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center">
        <FiUploadCloud className="w-8 h-8 text-primary-600" />
      </div>
      <div className="text-center">
        <p className="font-medium text-gray-900 dark:text-white">
          {isDragActive ? 'Drop file here' : 'Upload document'}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          PDF, JPG, PNG up to {maxSizeMB}MB
        </p>
      </div>
      <Button variant="secondary" size="sm">
        Choose File
      </Button>
    </div>
  )
}
