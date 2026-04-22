"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X } from "lucide-react"
import { Logo } from "@/components/branding/Logo"
import { cn } from "@/lib/utils/cn"

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/features", label: "Features" },
  { href: "/pricing", label: "Pricing" },
  { href: "/partner-program", label: "Partner Program" },
  { href: "/shop", label: "Shop" },
  { href: "/support", label: "Support" },
]

export function NavBar() {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 16)
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    setMobileOpen(false)
  }, [pathname])

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/"
    return pathname.startsWith(href)
  }

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 h-16 transition-all duration-300",
        scrolled
          ? "glass-panel-strong shadow-panel border-b border-tcai-border"
          : "bg-transparent border-b border-transparent"
      )}
      style={{ backdropFilter: scrolled ? "blur(20px)" : "none" }}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between gap-6">
        {/* Logo */}
        <Link href="/" className="flex-shrink-0 outline-none" aria-label="TechCam AI home">
          <Logo variant="full" size="sm" />
        </Link>

        {/* Desktop nav links */}
        <ul className="hidden md:flex items-center gap-1 flex-1 justify-center">
          {navLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={cn(
                  "px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200 relative",
                  isActive(link.href)
                    ? "text-electric-blue bg-active-nav"
                    : "text-tcai-muted hover:text-tcai-text hover:bg-white/[0.04]"
                )}
              >
                {link.label}
                {isActive(link.href) && (
                  <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-electric-blue" />
                )}
              </Link>
            </li>
          ))}
        </ul>

        {/* Desktop CTA buttons */}
        <div className="hidden md:flex items-center gap-2 flex-shrink-0">
          <Link
            href="/login"
            className="px-4 py-2 rounded-xl text-sm font-medium text-tcai-muted border border-tcai-border hover:text-electric-blue hover:border-electric-blue/30 transition-all duration-200"
          >
            Login
          </Link>
          <Link
            href="/shop"
            className="px-4 py-2 rounded-xl text-sm font-semibold text-white bg-btn-primary hover:shadow-btn-glow transition-all duration-200 shadow-inset-top"
          >
            Buy License
          </Link>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden flex items-center justify-center w-9 h-9 rounded-xl border border-tcai-border text-tcai-muted hover:text-tcai-text transition-colors"
          onClick={() => setMobileOpen((v) => !v)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </nav>

      {/* Mobile slide-down nav */}
      <div
        className={cn(
          "md:hidden overflow-hidden transition-all duration-300 ease-in-out border-b border-tcai-border",
          mobileOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0"
        )}
        style={{ background: "rgba(10,19,37,0.97)", backdropFilter: "blur(20px)" }}
      >
        <ul className="px-4 py-4 flex flex-col gap-1">
          {navLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={cn(
                  "block px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                  isActive(link.href)
                    ? "text-electric-blue bg-active-nav"
                    : "text-tcai-muted hover:text-tcai-text hover:bg-white/[0.04]"
                )}
              >
                {link.label}
              </Link>
            </li>
          ))}
          <li className="pt-2 pb-1 border-t border-tcai-border mt-2 flex flex-col gap-2">
            <Link
              href="/login"
              className="block text-center px-4 py-2.5 rounded-xl text-sm font-medium text-tcai-muted border border-tcai-border hover:border-electric-blue/30 hover:text-electric-blue transition-all"
            >
              Login
            </Link>
            <Link
              href="/shop"
              className="block text-center px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-btn-primary hover:shadow-btn-glow transition-all"
            >
              Buy License
            </Link>
          </li>
        </ul>
      </div>
    </header>
  )
}
