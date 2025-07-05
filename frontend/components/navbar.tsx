"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Moon, Sun, Wallet } from "lucide-react"
import { useTheme } from "next-themes"

export function Navbar() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()

  const navLinks = [
    { href: "/", label: "Dashboard" },
    { href: "/leaderboard", label: "Leaderboard" },
    { href: "/how-to", label: "How-To" },
  ]

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card dark:glass-card border-b border-white/10">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="text-xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent"
        >
          LiquidityHub
        </Link>

        <div className="hidden md:flex items-center space-x-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`transition-colors hover:text-blue-400 ${pathname === link.href ? "text-blue-400" : "text-gray-300"
                }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="hover:animate-bounce-micro"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
        </div>
      </div>
    </nav>
  )
}
