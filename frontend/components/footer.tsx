import { Github, Twitter } from "lucide-react"
import Link from "next/link"

export function Footer() {
  return (
    <footer className="glass-card dark:glass-card border-t border-white/10 py-6">
      <div className="container mx-auto px-4 flex items-center justify-between">
        <p className="text-sm text-gray-400">© 2025 LiquidityHub</p>

        <div className="flex items-center space-x-4">
          <Link
            href="https://github.com"
            className="text-gray-400 hover:text-blue-400 transition-colors hover:animate-bounce-micro"
          >
            <Github className="h-5 w-5" />
          </Link>
          <Link
            href="https://twitter.com"
            className="text-gray-400 hover:text-blue-400 transition-colors hover:animate-bounce-micro"
          >
            <Twitter className="h-5 w-5" />
          </Link>
        </div>
      </div>
    </footer>
  )
}
