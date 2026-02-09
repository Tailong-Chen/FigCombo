import { useState } from 'react'
import { Type, AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline } from 'lucide-react'
import { useFigureStore } from '../../stores/index'
import toast from 'react-hot-toast'

export default function TextAnnotations() {
  const [text, setText] = useState('')
  const [fontSize, setFontSize] = useState(12)
  const [isBold, setIsBold] = useState(false)
  const [isItalic, setIsItalic] = useState(false)
  const [color, setColor] = useState('#000000')
  const [align, setAlign] = useState<'left' | 'center' | 'right'>('left')

  const { addPanel } = useFigureStore()

  const handleAddText = () => {
    if (!text.trim()) {
      toast.error('Please enter some text')
      return
    }

    addPanel({
      type: 'annotation',
      content: text,
      position: { x: 10, y: 10 },
      size: { width: 60, height: 20 },
      fontSize,
      bold: isBold,
      italic: isItalic,
      color,
    })

    toast.success('Text annotation added')
    setText('')
  }

  return (
    <div className="p-4 space-y-4">
      {/* Text Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Text Content
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter your text annotation..."
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-scientific-500 focus:border-scientific-500 resize-none"
        />
      </div>

      {/* Font Size */}
      <div>
        <label className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Font Size</span>
          <span>{fontSize}pt</span>
        </label>
        <input
          type="range"
          min="6"
          max="72"
          value={fontSize}
          onChange={(e) => setFontSize(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Formatting */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Formatting
        </label>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsBold(!isBold)}
            className={`p-2 rounded-md transition-colors ${
              isBold ? 'bg-scientific-100 text-scientific-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Bold className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsItalic(!isItalic)}
            className={`p-2 rounded-md transition-colors ${
              isItalic ? 'bg-scientific-100 text-scientific-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Italic className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-gray-300 mx-1" />
          <button
            onClick={() => setAlign('left')}
            className={`p-2 rounded-md transition-colors ${
              align === 'left' ? 'bg-scientific-100 text-scientific-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <AlignLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setAlign('center')}
            className={`p-2 rounded-md transition-colors ${
              align === 'center' ? 'bg-scientific-100 text-scientific-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <AlignCenter className="w-4 h-4" />
          </button>
          <button
            onClick={() => setAlign('right')}
            className={`p-2 rounded-md transition-colors ${
              align === 'right' ? 'bg-scientific-100 text-scientific-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <AlignRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Color */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Color
        </label>
        <div className="flex items-center gap-2">
          <input
            type="color"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            className="w-10 h-10 rounded-md border border-gray-300 cursor-pointer"
          />
          <input
            type="text"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
      </div>

      {/* Preview */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preview
        </label>
        <div className="bg-white border border-gray-200 rounded-md p-4 min-h-[60px] flex items-center justify-center">
          <p
            style={{
              fontSize: `${fontSize}px`,
              fontWeight: isBold ? 'bold' : 'normal',
              fontStyle: isItalic ? 'italic' : 'normal',
              color,
              textAlign: align,
            }}
            className="w-full"
          >
            {text || 'Preview text'}
          </p>
        </div>
      </div>

      {/* Add Button */}
      <button
        onClick={handleAddText}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-scientific-600 text-white font-medium rounded-md hover:bg-scientific-700 transition-colors"
      >
        <Type className="w-4 h-4" />
        Add Text Annotation
      </button>
    </div>
  )
}
