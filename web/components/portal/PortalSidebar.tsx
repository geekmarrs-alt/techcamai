"use client"

import { usePathname, useRouter } from "next/navigation"
import { signOut } from "next-auth/react"
import Link from "next/link"
import { Logo } from "@/components/branding/Logo"
import {
  LayoutDashboard,
  Users,
  Key,
  Zap,
  CreditCard,
  RefreshCw,
  LifeBuoy,
  Settings,
  LogOut,
  FileText,
  ShieldCheck,
  ShoppingCart,
  Wallet,
  ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils/cn"

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: number | string
}

interface NavSection {
  title: string
  items: NavItem[]
}

const adminSections: NavSection[] = [
  {
    title: "System",
    items: [
      { label: "Overview", href: "/admin", icon: LayoutDashboard },
      { label: "Partner Applications", href: "/admin/partner-applications", icon: FileText },
      { label: "Installers", href: "/admin/installers", icon: ShieldCheck },
      { label: "Customers", href: "/admin/customers", icon: Users },
      { label: "Licenses", href: "/admin/licenses", icon: Key },
      { label: "Activations", href: "/admin/activations", icon: Zap },
      { label: "Payments", href: "/admin/payments", icon: CreditCard },
      { label: "Renewals", href: "/admin/renewals", icon: RefreshCw },
      { label: "Support", href: "/admin/support", icon: LifeBuoy },
      { label: "Settings", href: "/admin/settings", icon: Settings },
    ],
  },
]

const installerSections: NavSection[] = [
  {
    title: "Workspace",
    items: [
      { label: "Overview", href: "/installer", icon: LayoutDashboard },
      { label: "Customers", href: "/installer/customers", icon: Users },
      { label: "Licenses", href: "/installer/licenses", icon: Key },
      { label: "Orders", href: "/installer/orders", icon: ShoppingCart },
      { label: "Billing", href: "/installer/billing", icon: Wallet },
      { label: "Renewals", href: "/installer/renewals", icon: RefreshCw },
      { label: "Settings", href: "/installer/settings", icon: Settings },
    ],
  },
]

const roleLabels: Record<string, string> = {
  ADMIN: "System Administrator",
  INSTALLER: "Installer Partner",
}

const roleBadgeColors: Record<string, string> = {
  ADMIN: "bg-electric-purple/20 text-electric-purple border-electric-purple/30",
  INSTALLER: "bg-electric-blue/20 text-electric-blue border-electric-blue/30",
}

interface PortalSidebarProps {
  role: "ADMIN" | "INSTALLER"
  userName?: string | null
  userEmail?: string | null
}

export function PortalSidebar({ role, userName, userEmail }: PortalSidebarProps) {
  const pathname = usePathname()
  const sections = role === "ADMIN" ? adminSections : installerSections

  const isActive = (href: string) => {
    if (href === "/admin" || href === "/installer") {
      return pathname === href
    }
    return pathname.startsWith(href)
  }

  const initials = userName
    ? userName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??"

  return (
    <aside
      className="flex flex-col h-full overflow-y-auto"
      style={{
        width: 280,
        background: "linear-gradient(180deg, rgba(8,17,33,.98) 0%, rgba(10,19,37,.95) 100%)",
        borderRight: "1px solid rgba(130,164,220,.16)",
      }}
    >
      {/* Logo */}
      <div className="px-5 py-6 border-b border-tcai-border flex-shrink-0">
        <Logo variant="full" size="md" />
      </div>

      {/* User info */}
      <div className="px-4 py-4 border-b border-tcai-border flex-shrink-0">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold text-electric-blue flex-shrink-0"
            style={{ background: "rgba(83,182,255,.15)", border: "1px solid rgba(83,182,255,.25)" }}
          >
            {initials}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-tcai-text truncate leading-tight">
              {userName ?? "Unknown User"}
            </p>
            <p className="text-xs text-tcai-faint truncate leading-tight mt-0.5">
              {userEmail ?? ""}
            </p>
          </div>
        </div>
        <div className="mt-3">
          <span
            className={cn(
              "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold border",
              roleBadgeColors[role] ?? "bg-tcai-border text-tcai-muted border-tcai-border"
            )}
          >
            {roleLabels[role] ?? role}
          </span>
        </div>
      </div>

      {/* Nav sections */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {sections.map((section) => (
          <div key={section.title}>
            <p className="px-2 mb-2 text-[10px] font-bold uppercase tracking-widest text-tcai-faint">
              {section.title}
            </p>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const active = isActive(item.href)
                const Icon = item.icon

                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                        active
                          ? "bg-active-nav text-electric-blue shadow-sm"
                          : "text-tcai-muted hover:text-tcai-text hover:bg-white/[0.04]"
                      )}
                      style={
                        active
                          ? { border: "1px solid rgba(83,182,255,.20)" }
                          : { border: "1px solid transparent" }
                      }
                    >
                      <Icon
                        className={cn(
                          "w-4 h-4 flex-shrink-0 transition-transform duration-150",
                          active ? "text-electric-blue" : "text-tcai-faint group-hover:text-tcai-muted",
                          "group-hover:translate-x-0.5"
                        )}
                      />
                      <span className="flex-1 truncate group-hover:translate-x-0.5 transition-transform duration-150">
                        {item.label}
                      </span>
                      {item.badge !== undefined && (
                        <span
                          className={cn(
                            "ml-auto inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[10px] font-bold",
                            active
                              ? "bg-electric-blue/20 text-electric-blue"
                              : "bg-white/10 text-tcai-muted"
                          )}
                        >
                          {item.badge}
                        </span>
                      )}
                      {active && (
                        <ChevronRight className="w-3 h-3 text-electric-blue/60 flex-shrink-0" />
                      )}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Sign out */}
      <div className="px-3 py-4 border-t border-tcai-border flex-shrink-0">
        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-tcai-faint hover:text-electric-red hover:bg-electric-red/5 transition-all duration-150 group"
          style={{ border: "1px solid transparent" }}
        >
          <LogOut className="w-4 h-4 flex-shrink-0 group-hover:translate-x-0.5 transition-transform duration-150" />
          <span className="group-hover:translate-x-0.5 transition-transform duration-150">
            Sign out
          </span>
        </button>
      </div>
    </aside>
  )
}
