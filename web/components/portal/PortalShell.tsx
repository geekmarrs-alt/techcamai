import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { PortalSidebar } from "@/components/portal/PortalSidebar"
import { PortalTopBar } from "@/components/portal/PortalTopBar"

interface PortalShellProps {
  children: React.ReactNode
  role: "ADMIN" | "INSTALLER"
  pageTitle?: string
  breadcrumb?: { label: string; href?: string }[]
}

export async function PortalShell({
  children,
  role,
  pageTitle,
  breadcrumb,
}: PortalShellProps) {
  const session = await auth()

  if (!session?.user) {
    redirect("/login")
  }

  return (
    <div className="flex h-screen overflow-hidden bg-app-bg">
      {/* Sidebar — hidden on mobile */}
      <div className="hidden lg:flex flex-shrink-0" style={{ width: 280 }}>
        <PortalSidebar
          role={role}
          userName={session.user.name}
          userEmail={session.user.email}
        />
      </div>

      {/* Main column */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <PortalTopBar
          pageTitle={pageTitle}
          breadcrumb={breadcrumb}
          userName={session.user.name}
          userEmail={session.user.email}
          role={role}
        />

        {/* Content area */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 lg:p-8 min-h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
