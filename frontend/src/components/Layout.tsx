import React from 'react'
import { Button } from '@/components/ui/button'
import { Sun, Moon } from 'lucide-react'
import Logo from '@/components/Logo'

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDark, setIsDark] = React.useState<boolean>(typeof document !== 'undefined' ? document.documentElement.classList.contains('dark') : false)

  const toggleTheme = () => {
    const next = !isDark
    setIsDark(next)
    if (next) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-muted/40 to-background">
      <header className="sticky top-0 z-40 border-b bg-white/80 dark:bg-zinc-900/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-zinc-900/60">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <Logo />
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <a className="hover:text-foreground" href="/#features">Features</a>
            <a className="hover:text-foreground" href="/#how-it-works">How it works</a>
            <a className="hover:text-foreground" href="/#contact">Contact</a>
            <a className="hover:text-foreground" href="/about">About</a>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6">
        {children}
      </main>

      <footer className="mt-16 border-t bg-white dark:bg-zinc-900">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div>
            © {new Date().getFullYear()} Style Sync. All rights reserved.
          </div>
          <div className="flex items-center gap-4">
            <a href="#privacy" className="hover:text-foreground">Privacy</a>
            <a href="#terms" className="hover:text-foreground">Terms</a>
            <a href="#contact" className="hover:text-foreground">Contact</a>
          </div>
          <div className="text-xs opacity-80">
            Theme preference is saved on this device.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout

