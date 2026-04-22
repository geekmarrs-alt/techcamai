import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils/cn"

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger"
type ButtonSize = "sm" | "md" | "lg"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  asChild?: boolean
  isLoading?: boolean
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: [
    "bg-btn-primary text-white font-semibold",
    "shadow-inset-top shadow-btn-glow",
    "hover:shadow-glow-blue hover:brightness-110",
    "active:scale-[0.975]",
    "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:brightness-100",
  ].join(" "),

  secondary: [
    "glass-panel text-tcai-text font-medium",
    "border border-tcai-border",
    "hover:border-electric-blue/30 hover:text-electric-blue hover:shadow-card",
    "active:scale-[0.975]",
    "disabled:opacity-50 disabled:cursor-not-allowed",
  ].join(" "),

  ghost: [
    "bg-transparent text-tcai-muted font-medium",
    "border border-transparent",
    "hover:text-tcai-text hover:border-tcai-border hover:bg-white/[0.04]",
    "active:scale-[0.975]",
    "disabled:opacity-50 disabled:cursor-not-allowed",
  ].join(" "),

  danger: [
    "bg-electric-red/10 text-electric-red font-medium",
    "border border-electric-red/25",
    "hover:bg-electric-red/20 hover:border-electric-red/50 hover:shadow-[0_0_16px_rgba(255,91,118,0.25)]",
    "active:scale-[0.975]",
    "disabled:opacity-50 disabled:cursor-not-allowed",
  ].join(" "),
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-3.5 py-2 text-sm rounded-xl gap-1.5",
  md: "px-5 py-2.5 text-sm rounded-2xl gap-2",
  lg: "px-7 py-3.5 text-base rounded-2xl gap-2.5",
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      asChild = false,
      isLoading = false,
      className,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : "button"

    return (
      <Comp
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          "inline-flex items-center justify-center",
          "transition-all duration-200",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-navy-900",
          "whitespace-nowrap select-none",
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-4 w-4 shrink-0"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span>Loading…</span>
          </>
        ) : (
          children
        )}
      </Comp>
    )
  }
)

Button.displayName = "Button"

export { Button, type ButtonVariant, type ButtonSize, type ButtonProps }
