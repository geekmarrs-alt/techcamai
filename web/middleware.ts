import { auth } from "@/auth"
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export default auth((req) => {
  const { nextUrl, auth: session } = req as NextRequest & { auth: typeof req.auth }
  const pathname = nextUrl.pathname

  const isInstaller = pathname.startsWith("/installer")
  const isAdmin = pathname.startsWith("/admin")

  if (!isInstaller && !isAdmin) {
    return NextResponse.next()
  }

  // No session → redirect to login
  if (!session) {
    const loginUrl = new URL("/login", nextUrl.origin)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  const role = session.user?.role

  // Non-admin trying to access /admin → redirect to installer portal
  if (isAdmin && role !== "ADMIN") {
    return NextResponse.redirect(new URL("/installer", nextUrl.origin))
  }

  return NextResponse.next()
})

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - public folder files
     * - api routes
     */
    "/((?!_next/static|_next/image|favicon\\.ico|api/|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js)$).*)",
  ],
}
