import * as React from "react"
import { cn } from "@/lib/utils/cn"

type CardVariant = "default" | "glow" | "featured"

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  asChild?: boolean
}

const variantClasses: Record<CardVariant, string> = {
  default: [
    "bg-tcai-panel border border-tcai-border",
    "backdrop-blur-[16px]",
    "shadow-panel",
    "hover:border-[rgba(130,164,220,0.24)] hover:shadow-card-hover",
    "transition-all duration-300",
  ].join(" "),

  glow: [
    "bg-tcai-panel border border-tcai-border",
    "backdrop-blur-[16px]",
    "shadow-panel",
    "hover:border-electric-blue/25 hover:shadow-glow-blue hover:shadow-card-hover",
    "transition-all duration-300",
  ].join(" "),

  featured: [
    "bg-tcai-panel border border-electric-blue/30",
    "backdrop-blur-[16px]",
    "shadow-glow-blue shadow-panel",
    "transition-all duration-300",
  ].join(" "),
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = "default", className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("rounded-3xl", variantClasses[variant], className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col gap-2 p-6 pb-0", className)}
      {...props}
    />
  )
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn("text-tcai-text font-semibold text-lg leading-tight", className)}
      {...props}
    />
  )
)
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-tcai-muted text-sm leading-relaxed", className)}
      {...props}
    />
  )
)
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6", className)} {...props} />
  )
)
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center p-6 pt-0", className)}
      {...props}
    />
  )
)
CardFooter.displayName = "CardFooter"

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  type CardVariant,
  type CardProps,
}
