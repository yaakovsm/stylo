import React from 'react'

const Wordmark: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} width="120" height="24" viewBox="0 0 240 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Style Sync">
    <text x="0" y="34" fontFamily="Playfair Display, serif" fontSize="32" fontWeight="700" fill="currentColor">Style Sync</text>
  </svg>
)

export const Logo: React.FC<{ className?: string; withWordmark?: boolean }> = ({ className, withWordmark = true }) => {
  return (
    <div className={`flex items-center gap-2 ${className ?? ''}`}>
      <svg width="28" height="28" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg" className="text-primary">
        <circle cx="14" cy="14" r="14" fill="currentColor" />
        <path d="M7.5 10.5c2.2-2.2 5.8-2.2 8 0 2.2-2.2 5.8-2.2 8 0" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round"/>
      </svg>
      {withWordmark && (
        <Wordmark className="h-6 w-auto" />
      )}
    </div>
  )
}

export default Logo

