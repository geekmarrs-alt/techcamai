import * as React from "react"
import { cn } from "@/lib/utils/cn"

type BadgeVariant = "default" | "ok" | "warn" | "bad" | "info" | "purple"

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  dot?: boolean
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-navy-700 border border-tcai-border text-tcai-muted",
  ok:      "bg-electric-green/10 border border-electric-green/25 text-electric-green",
  warn:    "bg-electric-amber/10 border border-electric-amber/25 text-electric-amber",
  bad:     "bg-electric-red/10 border border-electric-red/25 text-electric-red",
  info:    "bg-electric-blue/10 border border-electric-blue/25 text-electric-blue",
  purple:  "bg-electric-purple/10 border border-electric-purple/25 text-electric-purple",
}

const dotColors: Record<BadgeVariant, string> = {
  default: "bg-tcai-faint",
  ok:      "bg-electric-green",
  warn:    "bg-electric-amber",
  bad:     "bg-electric-red",
  info:    "bg-electric-blue",
  purple:  "bg-electric-purple",
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = "default", dot = false, className, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center gap-1.5",
          "px-2.5 py-0.5 rounded-full",
          "text-xs font-medium",
          "whitespace-nowrap",
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              "w-1.5 h-1.5 rounded-full shrink-0",
              dotColors[variant],
              variant === "ok" ? "animate-pulse" : ""
            )}
            aria-hidden="true"
          />
        )}
        {children}
      </span>
    )
  }
)

Badge.displayName = "Badge"

export { Badge, type BadgeVariant, type BadgeProps }
