import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "@/styles/globals.css"
import { SessionProvider } from "@/components/providers/SessionProvider"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = {
  title: {
    default: "TechCam AI | AI CCTV Intelligence",
    template: "%s | TechCam AI",
  },
  description:
    "TechCam AI is the smart CCTV platform for modern security teams. AI-powered alerts, live monitoring, edge deployment — powered by Geek-Tech.",
  keywords: [
    "CCTV AI",
    "AI surveillance",
    "smart camera system",
    "security monitoring",
    "edge AI",
    "TechCam",
    "Geek-Tech",
  ],
  authors: [{ name: "Geek-Tech" }],
  creator: "Geek-Tech",
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_BASE_URL ?? "https://techcam.ai"
  ),
  openGraph: {
    type: "website",
    locale: "en_GB",
    url: "/",
    siteName: "TechCam AI",
    title: "TechCam AI | AI CCTV Intelligence",
    description:
      "AI-powered CCTV intelligence platform. Plug-and-play setup, real-time alerts, edge deployment. Powered by Geek-Tech.",
  },
  twitter: {
    card: "summary_large_image",
    title: "TechCam AI | AI CCTV Intelligence",
    description:
      "AI-powered CCTV intelligence platform. Plug-and-play setup, real-time alerts, edge deployment.",
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-navy-900 min-h-screen antialiased">
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  )
}
