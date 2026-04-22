import { cn } from "@/lib/utils/cn"

interface LogoProps {
  className?: string
  variant?: "full" | "icon"
  size?: "sm" | "md" | "lg"
}

const sizeMap = {
  sm: { icon: 28, text: "text-base" },
  md: { icon: 36, text: "text-xl" },
  lg: { icon: 48, text: "text-2xl" },
}

export function Logo({ className, variant = "full", size = "md" }: LogoProps) {
  const { icon: iconSize, text: textSize } = sizeMap[size]

  return (
    <div className={cn("flex items-center gap-2.5 select-none", className)}>
      {/* Hexagonal camera icon with cyan lens */}
      <svg
        width={iconSize}
        height={iconSize}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* Hex background */}
        <path
          d="M24 2L43.05 13V35L24 46L4.95 35V13L24 2Z"
          fill="url(#hex-fill)"
          stroke="url(#hex-stroke)"
          strokeWidth="1.2"
        />

        {/* Camera body */}
        <rect
          x="11"
          y="16"
          width="22"
          height="16"
          rx="3"
          fill="rgba(10, 19, 37, 0.85)"
          stroke="rgba(83,182,255,0.40)"
          strokeWidth="1"
        />

        {/* Camera notch (top) */}
        <rect x="19" y="13" width="10" height="4" rx="1.5" fill="rgba(83,182,255,0.30)" />

        {/* Outer glow ring */}
        <circle
          cx="24"
          cy="24"
          r="6.5"
          fill="none"
          stroke="url(#ring-gradient)"
          strokeWidth="1.4"
          opacity="0.7"
        />

        {/* Lens outer */}
        <circle cx="24" cy="24" r="5" fill="url(#lens-fill)" />

        {/* Lens inner */}
        <circle cx="24" cy="24" r="3" fill="url(#lens-inner)" />

        {/* Lens highlight */}
        <circle cx="22.5" cy="22.5" r="1" fill="rgba(255,255,255,0.55)" />

        {/* Viewfinder dots */}
        <circle cx="14.5" cy="19.5" r="1" fill="rgba(83,182,255,0.5)" />

        {/* Record dot */}
        <circle cx="34" cy="19.5" r="1.5" fill="#ff5b76" opacity="0.9" />

        <defs>
          <linearGradient id="hex-fill" x1="4.95" y1="2" x2="43.05" y2="46" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="rgba(83,182,255,0.22)" />
            <stop offset="100%" stopColor="rgba(124,92,255,0.18)" />
          </linearGradient>
          <linearGradient id="hex-stroke" x1="4.95" y1="2" x2="43.05" y2="46" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="rgba(83,182,255,0.60)" />
            <stop offset="100%" stopColor="rgba(124,92,255,0.50)" />
          </linearGradient>
          <radialGradient id="ring-gradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#53b6ff" />
            <stop offset="100%" stopColor="#35e0b8" />
          </radialGradient>
          <radialGradient id="lens-fill" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#53b6ff" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#0d1c33" />
          </radialGradient>
          <radialGradient id="lens-inner" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#35e0b8" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#0b1629" stopOpacity="0.95" />
          </radialGradient>
        </defs>
      </svg>

      {variant === "full" && (
        <div className="flex flex-col leading-none">
          <span
            className={cn(
              "font-bold tracking-tight",
              textSize,
              "bg-gradient-to-r from-electric-blue to-electric-purple bg-clip-text text-transparent"
            )}
          >
            TechCam AI
          </span>
          <span className="text-[10px] text-tcai-faint tracking-widest uppercase mt-0.5 font-medium">
            Powered by Geek-Tech
          </span>
        </div>
      )}
    </div>
  )
}
