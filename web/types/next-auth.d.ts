import "next-auth"
import "next-auth/jwt"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      email: string
      name?: string | null
      image?: string | null
      role: "ADMIN" | "INSTALLER"
    }
  }

  interface User {
    id: string
    email: string
    name?: string | null
    role: "ADMIN" | "INSTALLER"
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string
    role: "ADMIN" | "INSTALLER"
  }
}
