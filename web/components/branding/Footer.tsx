import Link from "next/link"
import { Logo } from "@/components/branding/Logo"

const productLinks = [
  { href: "/features", label: "Features" },
  { href: "/pricing", label: "Pricing" },
  { href: "/shop", label: "Shop" },
  { href: "/preview", label: "Preview Demo" },
]

const companyLinks = [
  { href: "/partner-program", label: "Partner Program" },
  { href: "/support", label: "Support" },
  { href: "/login", label: "Portal Login" },
]

const supportLinks = [
  { href: "/support", label: "Get Help" },
  { href: "/support#faq", label: "FAQ" },
  { href: "/support#license-recovery", label: "License Recovery" },
  { href: "mailto:support@geek-tech.co.uk", label: "Email Support" },
]

export function Footer() {
  return (
    <footer
      className="relative border-t border-tcai-border"
      style={{ background: "rgba(7,17,31,0.98)" }}
    >
      {/* Top gradient line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-electric-blue/25 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-8">
          {/* Brand column */}
          <div className="md:col-span-1 flex flex-col gap-4">
            <Logo variant="full" size="sm" />
            <p className="text-tcai-muted text-sm leading-relaxed max-w-xs">
              The smart CCTV platform for modern security teams. AI-powered monitoring, edge deployed.
            </p>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-tcai-faint font-medium uppercase tracking-wider">
                Powered by Geek-Tech
              </span>
              <span className="text-xs text-tcai-faint">
                In collaboration with Geek-Tech
              </span>
            </div>
          </div>

          {/* Product links */}
          <div className="flex flex-col gap-4">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-tcai-faint">
              Product
            </h3>
            <ul className="flex flex-col gap-2.5">
              {productLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-tcai-muted hover:text-electric-blue transition-colors duration-200"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company links */}
          <div className="flex flex-col gap-4">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-tcai-faint">
              Company
            </h3>
            <ul className="flex flex-col gap-2.5">
              {companyLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-tcai-muted hover:text-electric-blue transition-colors duration-200"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support links */}
          <div className="flex flex-col gap-4">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-tcai-faint">
              Support
            </h3>
            <ul className="flex flex-col gap-2.5">
              {supportLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-tcai-muted hover:text-electric-blue transition-colors duration-200"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-16 pt-8 border-t border-tcai-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-tcai-faint">
            © 2025 TechCam AI. All rights reserved.
          </p>
          <p className="text-xs text-tcai-faint text-center sm:text-right">
            In collaboration with{" "}
            <span className="text-electric-blue font-medium">Geek-Tech</span>
          </p>
        </div>
      </div>
    </footer>
  )
}
