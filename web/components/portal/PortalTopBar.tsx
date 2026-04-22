"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ChevronRight, Home } from "lucide-react"
import { cn } from "@/lib/utils/cn"

interface BreadcrumbItem {
  label: string
  href?: string
}

interface PortalTopBarProps {
  pageTitle?: string
  breadcrumb?: BreadcrumbItem[]
  userName?: string | null
  userEmail?: string | null
  role: "ADMIN" | "INSTALLER"
}

function Clock() {
  const [now, setNow] = useState<Date | null>(null)

  useEffect(() => {
    setNow(new Date())
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  if (!now) return null

  const dateStr = now.toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  })
  const timeStr = now.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  })

  return (
    <span className="text-xs text-tcai-faint tabular-nums">
      {dateStr} &nbsp;·&nbsp; {timeStr}
    </span>
  )
}

export function PortalTopBar({
  pageTitle,
  breadcrumb,
  userName,
  userEmail,
  role,
}: PortalTopBarProps) {
  const initials = userName
    ? userName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??"

  const roleLabelMap: Record<string, string> = {
    ADMIN: "Admin",
    INSTALLER: "Installer",
  }

  return (
    <header
      className="flex-shrink-0 flex items-center justify-between px-6 h-16"
      style={{
        background: "rgba(7,17,31,.90)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(130,164,220,.12)",
      }}
    >
      {/* Left: title + breadcrumb */}
      <div className="flex flex-col justify-center min-w-0">
        {pageTitle && (
          <h1 className="text-base font-semibold text-tcai-text leading-tight truncate">
            {pageTitle}
          </h1>
        )}
        {breadcrumb && breadcrumb.length > 0 && (
          <nav className="flex items-center gap-1 mt-0.5">
            <Home className="w-3 h-3 text-tcai-faint" />
            {breadcrumb.map((crumb, i) => (
              <span key={i} className="flex items-center gap-1">
                <ChevronRight className="w-3 h-3 text-tcai-faint" />
                {crumb.href ? (
                  <Link
                    href={crumb.href}
                    className="text-xs text-tcai-faint hover:text-electric-blue transition-colors"
                  >
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="text-xs text-tcai-muted">{crumb.label}</span>
                )}
              </span>
            ))}
          </nav>
        )}
      </div>

      {/* Right: clock + user avatar */}
      <div className="flex items-center gap-4 flex-shrink-0 ml-4">
        <Clock />

        <div className="flex items-center gap-2.5">
          <div className="hidden sm:flex flex-col items-end leading-none">
            <span className="text-xs font-semibold text-tcai-text">{userName ?? "User"}</span>
            <span
              className={cn(
                "text-[10px] font-semibold uppercase tracking-wide mt-0.5",
                role === "ADMIN" ? "text-electric-purple" : "text-electric-blue"
              )}
            >
              {roleLabelMap[role] ?? role}
            </span>
          </div>
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold text-electric-blue flex-shrink-0"
            style={{
              background: "rgba(83,182,255,.15)",
              border: "1px solid rgba(83,182,255,.25)",
            }}
            title={userEmail ?? ""}
          >
            {initials}
          </div>
        </div>
      </div>
    </header>
  )
}
