import { useState, createContext, useContext, ReactNode, Children, isValidElement, cloneElement } from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

interface TabsContextValue {
  activeTab: string
  setActiveTab: (id: string) => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

function useTabs() {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs provider')
  }
  return context
}

// Tabs Container
interface TabsProps {
  children: ReactNode
  defaultTab: string
  className?: string
}

export function Tabs({ children, defaultTab, className }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn('flex flex-col h-full', className)}>{children}</div>
    </TabsContext.Provider>
  )
}

// Tab List
interface TabListProps {
  children: ReactNode
  className?: string
}

export function TabList({ children, className }: TabListProps) {
  return (
    <div className={cn('flex border-b border-gray-200', className)}>
      {children}
    </div>
  )
}

// Tab
interface TabProps {
  id: string
  children: ReactNode
  icon?: ReactNode
  className?: string
}

export function Tab({ id, children, icon, className }: TabProps) {
  const { activeTab, setActiveTab } = useTabs()
  const isActive = activeTab === id

  return (
    <button
      onClick={() => setActiveTab(id)}
      className={cn(
        'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
        isActive
          ? 'border-scientific-500 text-scientific-600'
          : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50',
        className
      )}
    >
      {icon && <span>{icon}</span>}
      {children}
    </button>
  )
}

// Tab Panels Container
interface TabPanelsProps {
  children: ReactNode
  className?: string
}

export function TabPanels({ children, className }: TabPanelsProps) {
  return (
    <div className={cn('flex-1 overflow-auto', className)}>
      {children}
    </div>
  )
}

// Tab Panel
interface TabPanelProps {
  id: string
  children: ReactNode
  className?: string
}

export function TabPanel({ id, children, className }: TabPanelProps) {
  const { activeTab } = useTabs()

  if (activeTab !== id) return null

  return (
    <div className={cn('animate-fade-in', className)}>
      {children}
    </div>
  )
}
