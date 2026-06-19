import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function hasAccess(pathname: string, role: string | undefined) {
  if (!role) {
    return false;
  }
  if (pathname.startsWith("/admin")) {
    return role === "admin";
  }
  if (pathname.startsWith("/officer")) {
    return role === "officer" || role === "admin";
  }
  if (pathname.startsWith("/dashboard")) {
    return role === "citizen" || role === "officer" || role === "admin";
  }
  return true;
}

export function middleware(request: NextRequest) {
  const role = request.cookies.get("rti_role")?.value;
  const token = request.cookies.get("rti_session")?.value;
  const { pathname } = request.nextUrl;

  if ((pathname.startsWith("/dashboard") || pathname.startsWith("/officer") || pathname.startsWith("/admin")) && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if ((pathname.startsWith("/dashboard") || pathname.startsWith("/officer") || pathname.startsWith("/admin")) && !hasAccess(pathname, role)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/officer/:path*", "/admin/:path*"],
};

