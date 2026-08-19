import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { FiUpload, FiFile } from 'react-icons/fi'
import { classNames } from '@utils/helpers'
import { formatFileSize } from '@utils/formatters'

export default function UploadZone({
  onFilesSelect,
  files = [],
  label = 'Upload source papers',
  maxFiles = 5,
}) {
  const onDrop = useCallback((accepted) => {
    onFilesSelect(accepted)
  }, [onFilesSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    maxFiles,
    multiple: true,
  })

  return (
    <div>
      <div
        {...getRootProps()}
        className={classNames(
          'border-2 border-dashed rounded-xl p-6',
          'flex flex-col items-center gap-3 cursor-pointer',
          'transition-all duration-200',
          isDragActive
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
        )}
      >
        <input {...getInputProps()} />
        <FiUpload className="w-8 h-8 text-gray-400" />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</p>
          <p className="text-xs text-gray-500 mt-1">PDF, JPG, PNG • Max {maxFiles} files</p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-3 space-y-2">
          {files.map((file, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <FiFile className="w-4 h-4 text-primary-500" />
              <span className="truncate">{file.name}</span>
              <span className="text-gray-400 flex-shrink-0">
                {formatFileSize(file.size)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
