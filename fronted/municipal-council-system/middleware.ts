import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PUBLIC_PATHS = ['/login']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Development mode: skip auth entirely
  if (process.env.NODE_ENV === 'development') {
    return NextResponse.next()
  }

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p))

  // Check for refresh token cookie (httpOnly set by backend)
  const hasRefreshToken =
    request.cookies.has('refresh_token') ||
    request.cookies.has('refresh') ||
    request.cookies.has('jwt_refresh')

  if (!isPublic && !hasRefreshToken) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isPublic && hasRefreshToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|icon.*|apple-icon.*).*)'],
}
