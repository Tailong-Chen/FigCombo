import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon, X, AlertCircle } from 'lucide-react'
import { useFigureStore } from '../../stores/index'
import { apiClient } from '../../api/client'
import { isValidImageFile, formatFileSize } from '../../utils/helpers'
import toast from 'react-hot-toast'

export default function ImageUpload() {
  const [uploading, setUploading] = useState(false)
  const { addPanel } = useFigureStore()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      if (!isValidImageFile(file)) {
        toast.error(`${file.name} is not a valid image file`)
        continue
      }

      setUploading(true)
      try {
        const response = await apiClient.uploadImage(file)
        if (response.success && response.data) {
          addPanel({
            type: 'image',
            src: response.data.url,
            position: { x: 10, y: 10 },
            size: {
              width: response.data.size.width / 10,
              height: response.data.size.height / 10,
            },
            filters: {
              brightness: 100,
              contrast: 100,
              saturation: 100,
              blur: 0,
            },
          })
          toast.success(`Uploaded ${file.name}`)
        }
      } catch (error) {
        console.error('Upload failed:', error)
        toast.error(`Failed to upload ${file.name}`)
      } finally {
        setUploading(false)
      }
    }
  }, [addPanel])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.webp'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  return (
    <div className="p-4 space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-scientific-500 bg-scientific-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        <p className="text-sm font-medium text-gray-900">
          {isDragActive ? 'Drop images here' : 'Drag & drop images here'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          or click to select files
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Supports: PNG, JPG, TIFF, WebP (max 50MB)
        </p>
      </div>

      {/* Uploading indicator */}
      {uploading && (
        <div className="flex items-center justify-center gap-2 py-4">
          <div className="w-5 h-5 border-2 border-scientific-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-gray-600">Uploading...</span>
        </div>
      )}

      {/* Rejection errors */}
      {fileRejections.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-800 mb-2">
            <AlertCircle className="w-4 h-4" />
            <span className="font-medium text-sm">Some files were rejected</span>
          </div>
          <ul className="text-xs text-red-600 space-y-1">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                • {file.name}: {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        <h4 className="font-medium text-sm text-gray-900">Tips</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Use high-resolution images for best quality</li>
          <li>• PNG is recommended for figures with text</li>
          <li>• JPG is suitable for photos and complex images</li>
          <li>• Images will be automatically resized to fit panels</li>
        </ul>
      </div>
    </div>
  )
}
